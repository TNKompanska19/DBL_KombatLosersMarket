import psycopg2
import sys
import os

# Adjust paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configuration import *

# Add project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(FOLDER), '..')))

def fast_enumeration():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Add the column if it doesn't exist
        cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'tweets' AND column_name = 'row_num'
                ) THEN
                    ALTER TABLE tweets ADD COLUMN row_num bigint;
                END IF;
            END
            $$;
        """)

        # Assign row numbers
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

        # Create a unique index
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_row_num_unique ON tweets(row_num);
        """)

        conn.commit()
        print("Row numbers updated and unique index created on 'row_num'.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fast_enumeration()