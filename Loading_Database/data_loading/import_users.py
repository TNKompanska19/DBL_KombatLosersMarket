import os
import json
import re
import pandas as pd
from sqlalchemy import create_engine

# ─── CONFIG ───────────────────────────────────────────────────────────────────
FOLDER = r"C:\Users\User\Desktop\TUE\Q4\DBL_Documents\data\testing"
TABLE_NAME = "users"
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/dbl_challenge"
# ────────────────────────────────────────────────────────────────────────────────

COLUMNS_TO_KEEP = [
    "user.id", "user.screen_name", "user.description", "user.protected", "user.verified", "user.followers_count",
    "user.friends_count", "user.listed_count", "user.favourites_count", "user.statuses_count",
    "user.created_at", "user.default_profile", "user.default_profile_image"

]


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
            line = line.strip()
            if not line:
                continue
            try:
                recs.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"  → Skipping invalid JSON line {i} in {os.path.basename(filepath)}")
        return recs


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

        s = re.sub(r'\W+', '_', orig)

        s = s.strip('_')

        if len(s) > max_len:
            s = s[:max_len]
        base = s
        count = seen.get(base, 0)
        if count:
            suffix = f"_{count}"

            s = base[: max_len - len(suffix)] + suffix
        seen[base] = count + 1
        safe_cols.append(s)
    return safe_cols


def main():
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

    df = pd.json_normalize(all_records)
    df = df[COLUMNS_TO_KEEP]

    df.columns = make_safe_colnames(df.columns, max_len=63)
    df.columns = ["id", "screen_name", "description", "protected", "verified", "followers_count",
                  "friends_count", "listed_count", "favourites_count", "statuses_count",
                  "created_at", "default_profile", "default_profile_image"]

    df = df.applymap(
        lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else x
    )

    engine = create_engine(DATABASE_URL)
    df.to_sql(TABLE_NAME, engine, if_exists='replace', index=False)
    print(f"Imported {len(df)} rows into '{TABLE_NAME}'")


main()