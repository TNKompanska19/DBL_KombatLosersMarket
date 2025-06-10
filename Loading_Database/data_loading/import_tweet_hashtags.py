import os
import json
import re
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import BigInteger, Text
from configuration import *

# ─── CONFIG ───────────────────────────────────────────────────────────────────
TABLE_NAME = "tweet_hashtags"

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


def make_safe_colnames(columns, max_len=63):
    """
    Sanitize and dedupe column names for PostgreSQL:
    - Non-alphanumerics → '_'
    - Truncate to max_len
    - Append suffix _1, _2… if needed
    """
    safe = []
    seen = {}
    for orig in columns:
        s = re.sub(r'\W+', '_', orig).strip('_')
        if len(s) > max_len:
            s = s[:max_len]
        base = s
        count = seen.get(base, 0)
        if count:
            suffix = f"_{count}"
            s = base[: max_len - len(suffix)] + suffix
        seen[base] = count + 1
        safe.append(s)
    return safe


def main():
    # Load all JSON
    all_records = []
    for fn in sorted(os.listdir(FOLDER)):
        if not fn.lower().endswith('.json'):
            continue
        recs = load_json_file(os.path.join(FOLDER, fn))
        print(f"Loaded {len(recs)} records from {fn}")
        all_records.extend(recs)
    if not all_records:
        print("No valid JSON found. Exiting.")
        return

        # Build list of mention‑rows
    mentions = []
    for rec in all_records:
        tweet_id = rec.get("id")

        for m in rec.get("entities", {}).get("hashtags", []):
            mentions.append({
                "tweet_id": tweet_id,
                "indices": m.get("indices"),
            })

    if not mentions:
        print("No hashtags found in any tweet.")
        return

    df = pd.DataFrame(mentions, columns=["tweet_id", "indices"])
    df.insert(0, "hashtagid", range(1, len(df) + 1))

    # sanitize column names:
    df.columns = make_safe_colnames(df.columns, max_len=63)

    # Serialize list/dict fields
    df = df.map(
        lambda x: json.dumps(x, ensure_ascii=False)
        if isinstance(x, (dict, list)) else x
    )

    # Write to Postgres
    engine = create_engine(DATABASE_URL)
    df.to_sql(
        TABLE_NAME,
        engine,
        if_exists='replace',
        index=False,
        dtype={
            'tweet_id': BigInteger(),
            'hashtag_id': BigInteger(),
            'indices': Text(),
        }
    )
    print(f"Imported {len(df)} rows into '{TABLE_NAME}'")


if __name__ == '__main__':
    main()
