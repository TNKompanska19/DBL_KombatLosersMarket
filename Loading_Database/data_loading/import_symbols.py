import os
import json
import re
import pandas as pd
from sqlalchemy import create_engine, BigInteger, Text
from sqlalchemy import create_engine, text
from configuration import *
# ─── CONFIG ───────────────────────────────────────────────────────────────────
TABLE_HASHTAGS   = 'symbols'
TABLE_TWEET_HASH = 'tweet_symbols'
# ────────────────────────────────────────────────────────────────────────────────

def load_json_file(filepath):
    """Load a JSON file as an array or line-delimited objects, skipping bad lines."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    if not text:
        return []
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        recs = []
        for i, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                recs.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"  → Skipping invalid JSON line {i} in {os.path.basename(filepath)}")
        return recs


def main():
    # Load all JSON files
    records = []
    for fn in sorted(os.listdir(FOLDER)):
        if not fn.lower().endswith('.json'):
            continue
        path = os.path.join(FOLDER, fn)
        recs = load_json_file(path)
        print(f"Loaded {len(recs)} records from {fn}")
        records.extend(recs)
    if not records:
        print("No valid JSON found. Exiting.")
        return

    # Extract raw hashtags rows
    raw = []
    for rec in records:
        tweet_id = rec.get('id')
        for h in rec.get('entities', {}).get('symbols', []):
            raw.append({
                'tweet_id':    tweet_id,
                'symbol_text': h.get('text'),
                'indices':      h.get('indices'),
            })
    if not raw:
        print("No hashtags found in any tweet. Exiting.")
        return

    df_raw = pd.DataFrame(raw)

    # Build hashtags lookup table
    df_tags = (
        df_raw[['symbol_text']]
        .drop_duplicates()
        .reset_index(drop=True)
        .rename(columns={'symbol_text': 'text'})
    )
    # assign surrogate IDs
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        max_id = conn.execute(text("""
            SELECT
            CASE
             WHEN to_regclass('public.symbols') IS NULL THEN 0
                ELSE (SELECT COALESCE(MAX(id::BIGINT), 0) FROM public.symbols)
            END AS max_id;
        """)).scalar()
    print("Max id =", max_id)
    df_tags.insert(0, 'id', range(max_id + 1, max_id + 1 + len(df_tags)))

    # Build tweet_hashtags table with foreign keys
    df_link = (
        df_raw
        .merge(df_tags, left_on='symbol_text', right_on='text', how='left')
        [['tweet_id', 'id', 'indices']]
        .rename(columns={'id': 'symbol_id'})
    )

    # Serialize indices
    df_link['indices'] = df_link['indices'].apply(
        lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x
    )

    # Write both tables to Postgres
    engine = create_engine(DATABASE_URL)

    # hashtags lookup
    df_tags.to_sql(
        TABLE_HASHTAGS,
        engine,
        if_exists='append',
        index=False,
        method='multi',
        chunksize=1_000 ,
        dtype={'id': BigInteger(), 'text': Text()}
    )

    # tweet_hashtags link
    df_link.to_sql(
        TABLE_TWEET_HASH,
        engine,
        if_exists='append',
        index=False,
        method='multi',
        chunksize=1_000 ,
        dtype={
            'tweet_id':   BigInteger(),
            'symbol_id': BigInteger(),
            'indices':    Text()
        }
    )

    print(f"Imported {len(df_tags)} unique hashtags into '{TABLE_HASHTAGS}'")
    print(f"Imported {len(df_link)} rows into '{TABLE_TWEET_HASH}'")

if __name__ == '__main__':
    main()
