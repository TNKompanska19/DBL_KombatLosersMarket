import os,sys
import json
import pandas as pd
from sqlalchemy import create_engine, text
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configuration import *

def load_all_json_lines(folder_path):
    tweets = []
    for file_name in sorted(os.listdir(folder_path)):
        if not file_name.endswith(".json"):
            continue
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        tweet_id = record.get("id")
                        full_text = record.get("extended_tweet", {}).get("full_text", record.get("text"))
                        if tweet_id and full_text:
                            tweets.append((tweet_id, full_text))
                    except json.JSONDecodeError:
                        continue
    return pd.DataFrame(tweets, columns=["id", "full_text"])

def main():
    engine = create_engine(DATABASE_URL)
    df = load_all_json_lines(FOLDER)
    print(f"[INFO] Loaded {len(df)} tweets with full_text from all JSON files.")

    if df.empty:
        print("[INFO] No data to update.")
        return

    with engine.begin() as conn:
        # Ensure full_text column exists in tweets table
        conn.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'tweets' AND column_name = 'full_text'
            ) THEN
                ALTER TABLE tweets ADD COLUMN full_text TEXT;
            END IF;
        END$$;
        """))
        print("[INFO] Ensured 'full_text' column exists in tweets table.")

        # Create temporary table
        conn.execute(text("""
            CREATE TEMP TABLE temp_updates (
                id BIGINT,
                full_text TEXT
            ) ON COMMIT DROP;
        """))

        # Bulk insert using pandas
        df.to_sql("temp_updates", con=conn, index=False, if_exists="append", method="multi")
        print("[INFO] Inserted data into temporary table.")

        # Perform one big update
        result = conn.execute(text("""
            UPDATE tweets
            SET full_text = temp_updates.full_text
            FROM temp_updates
            WHERE tweets.id = temp_updates.id;
        """))
        print(f"[INFO] Updated {result.rowcount} rows in the tweets table.")

if __name__ == "__main__":
    main()
