import psycopg2
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configuration import *

# Add project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(FOLDER), '..')))

def fast_enumeration():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name='tweets' AND column_name='row_num'
                    ) THEN
                        ALTER TABLE tweets ADD COLUMN row_num bigint;
                    END IF;
                END
                $$;
            """)

        cursor.execute("""
            WITH numbered AS (
                SELECT ctid, ROW_NUMBER() OVER () AS rn
                FROM tweets
            )
            UPDATE tweets
            SET row_num = numbered.rn
            FROM numbered
            WHERE tweets.ctid = numbered.ctid;
        """)

        conn.commit()
        print("Row numbers updated FAST using physical order.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fast_enumeration()