import os,sys, json
import pandas as pd
from sqlalchemy import create_engine, Table, Column, MetaData, BigInteger, Text, Boolean, Float
from sqlalchemy.dialects.postgresql import insert
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configuration import *

# ─── CONFIG ────────────────────────────────────────
TABLE_NAME = "users"
BIGINT_MAX = 9223372036854775807

# ─── HELPERS ───────────────────────────────────────
def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    if not text:
        return []

    try:
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        pass

    valid = []
    for i, line in enumerate(text.splitlines()):
        line = line.strip()
        if not line or not line.startswith('{'):
            continue
        try:
            valid.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"Skipping broken JSON line {i+1} in {os.path.basename(filepath)}: {e}")
    return valid


def sanitize_text(val):
    return val.replace('\x00', '') if isinstance(val, str) else val

# ─── MAIN ──────────────────────────────────────────
def main():
    users = []
    for fn in os.listdir(FOLDER):
        if fn.endswith('.json'):
            for record in load_json(os.path.join(FOLDER, fn)):
                if isinstance(record, dict) and "user" in record:
                    users.append(record["user"])

    if not users:
        print("No users found.")
        return

    df = pd.json_normalize(users)

    columns = [
        "id", "screen_name", "description", "protected", "verified", "followers_count",
        "friends_count", "listed_count", "favourites_count", "statuses_count", "created_at",
        "default_profile", "default_profile_image"
    ]

    for col in columns:
        if col not in df.columns:
            df[col] = None

    df = df[columns]

    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df[df["id"].notnull() & (df["id"] <= BIGINT_MAX)]

    df["description"] = df["description"].apply(sanitize_text)
    df["screen_name"] = df["screen_name"].apply(sanitize_text)

    # Convert numeric fields to float
    for col in ["followers_count", "friends_count", "listed_count", "favourites_count", "statuses_count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["protected", "verified", "default_profile", "default_profile_image"]:
        df[col] = df[col].fillna(False).astype(bool)

    df["created_at"] = df["created_at"].fillna("")

    # ─── DB INSERT ──────────────────────────────────
    engine = create_engine(DATABASE_URL)
    meta = MetaData()

    users_table = Table(TABLE_NAME, meta,
        Column("id", BigInteger, primary_key=True),
        Column("screen_name", Text),
        Column("description", Text),
        Column("protected", Boolean),
        Column("verified", Boolean),
        Column("followers_count", Float),
        Column("friends_count", Float),
        Column("listed_count", Float),
        Column("favourites_count", Float),
        Column("statuses_count", Float),
        Column("created_at", Text),
        Column("default_profile", Boolean),
        Column("default_profile_image", Boolean),
        extend_existing=True
    )

    failed_rows = []

    with engine.begin() as conn:
        for start in range(0, len(df), 1000):
            chunk = df.iloc[start:start+1000].to_dict(orient='records')
            stmt = insert(users_table).values(chunk).on_conflict_do_nothing(index_elements=['id'])
            try:
                conn.execute(stmt)
            except Exception as e:
                print(f"Error inserting chunk {start}: {e}")
                failed_rows.extend(chunk)

    print(f"Inserted {len(df) - len(failed_rows)} users. Failed inserts: {len(failed_rows)}")

main()
