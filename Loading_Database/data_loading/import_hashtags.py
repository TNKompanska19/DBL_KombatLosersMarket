import os, sys
import json
import re
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import BigInteger, Text
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configuration import *
# ─── CONFIG ───────────────────────────────────────────────────────────────────
TABLE_NAME = "hashtags"
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
    # 1) Load all JSON
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

        # 2) Build a flat list of mention‑rows instead of json_normalize
    mentions = []
    for rec in all_records:
        tweet_id = rec.get("id")
        # safely grab the mentions list (or empty list)
        for m in rec.get("entities", {}).get("hashtags", []):
            mentions.append({
                "text":       m.get("text"),
            })

    if not mentions:
        print("No hashtags found in any tweet.")
        return

    df = pd.DataFrame(mentions, columns=["text"])
    df.insert(0, "hashtag_id", range(1, len(df) + 1))

    # 3) (Optional) sanitize column names for Postgres if you still want to:
    df.columns = make_safe_colnames(df.columns, max_len=63)

    # 4) Serialize list/dict fields
    df = df.map(
        lambda x: json.dumps(x, ensure_ascii=False)
                  if isinstance(x, (dict, list)) else x
    )

    # 5) Write to Postgres (replace table each run)
    engine = create_engine(DATABASE_URL)
    df.to_sql(
    TABLE_NAME,
    engine,
    if_exists='replace',
    index=False,
    dtype={
      'tweet_id':   BigInteger(),
      'hashtag_id':    BigInteger(),
      'indices':     Text(),
    }
)
    print(f"Imported {len(df)} rows into '{TABLE_NAME}'")

if __name__ == '__main__':
    main()
