import os
import json
import re
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import BigInteger, Text, Boolean
from configuration import *

# ─── CONFIG ───────────────────────────────────────────────────────────────────
TABLE_NAME = "tweets"
# ────────────────────────────────────────────────────────────────────────────────

COLUMNS_TO_KEEP = [
    "id", "created_at", "text", "truncated", "lang", "quote_count", "reply_count",
    "retweet_count", "favorite_count", "favorited", "retweeted", "possibly_sensitive",
    "filter_level", "in_reply_to_screen_name", "is_quote_status",
    "user.id", "place.id", "in_reply_to_status_id", "in_reply_to_user_id",
    "quoted_status_id", "retweeted_status.id"

]


def load_json_file(filepath):
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            try:
                record = json.loads(line, parse_int=str)
                records.append(record)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line {line_number}: {e}")
    return records


def make_safe_colnames(columns, max_len=63):
    """
    Sanitize and deduplicate column names for PostgreSQL:
    - Replace non-alphanumerics with '_'
    - Truncate to max_len
    - Append suffix _1, _2… to avoid duplicates (after truncation)
    """
    safe_cols = []
    seen = {}
    for orig in columns:
        # replace any non-word char with underscore
        s = re.sub(r'\W+', '_', orig)
        # strip leading/trailing underscores
        s = s.strip('_')
        # truncate if too long
        if len(s) > max_len:
            s = s[:max_len]
        base = s
        count = seen.get(base, 0)
        if count:
            suffix = f"_{count}"
            # ensure the full name stays within max_len
            s = base[: max_len - len(suffix)] + suffix
        seen[base] = count + 1
        safe_cols.append(s)
    return safe_cols


def main():
    # Load all JSON
    all_records = []
    for fn in sorted(os.listdir(FOLDER)):
        if not fn.lower().endswith('.json'):
            continue
        path = os.path.join(FOLDER, fn)
        recs = load_json_file(path)
        print(f"Loaded {len(recs)} records from {fn}")
        all_records.extend(recs)

    if not all_records:
        print("No valid JSON found. Exiting.")
        return

    # Flatten into DataFrame

    df = pd.json_normalize(all_records)

    df = df[COLUMNS_TO_KEEP]

    #  Sanitize columns for PostgreSQL
    df.columns = make_safe_colnames(df.columns, max_len=63)

    print("Columns after sanitizing:", df.columns.tolist())  # debug

    # Serialize any dict or list cells to JSON strings
    df = df.applymap(
        lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else x
    )

    # Drop any rows missing an 'id'
    df.dropna(subset=["id"], inplace=True)

    # Drop rows missing a 'user_id'
    df.dropna(subset=["user_id"], inplace=True)

    df["id"] = df["id"].astype(str).astype("Int64")
    df["user_id"] = df["user_id"].astype(str).astype("Int64")
    #  Write to Postgres
    engine = create_engine(DATABASE_URL)
    df.to_sql(TABLE_NAME, engine, if_exists='replace', index=False,
              dtype={

                  "id": BigInteger(),
                  "created_at": Text(),
                  "text": Text(),
                  "truncated": Boolean(),
                  "lang": Text(),
                  "quote_count": BigInteger(),
                  "reply_count": BigInteger(),
                  "retweet_count": BigInteger(),
                  "favorite_count": BigInteger(),
                  "favorited": Boolean(),
                  "retweeted": Boolean(),
                  "possibly_sensitive": Boolean(),
                  "filter_level": Text(),
                  "in_reply_to_screen_name": Text(),
                  "is_quote_status": Boolean(),
                  "user_id": BigInteger(),
                  "place_id": Text(),
                  "in_reply_to_status_id": BigInteger(),
                  "in_reply_to_user_id": BigInteger(),
                  "quoted_status_id": BigInteger(),
                  "retweeted_status_id": BigInteger()
              })
    print(f"Imported {len(df)} rows into '{TABLE_NAME}'")


main()