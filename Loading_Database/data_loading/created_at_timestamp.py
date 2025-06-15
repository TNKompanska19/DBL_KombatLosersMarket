import sys, os
import psycopg2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configuration import *

# Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Add a new TIMESTAMP column
cursor.execute("""
    ALTER TABLE tweets 
    ADD COLUMN IF NOT EXISTS created_at_new TIMESTAMP;
""")

# Update new column by parsing the old text format
cursor.execute("""
    UPDATE tweets
    SET created_at_new = to_timestamp(created_at, 'Dy Mon DD HH24:MI:SS +0000 YYYY')
    WHERE created_at_new IS NULL;
""")

# Drop old column and rename new one
cursor.execute("ALTER TABLE tweets DROP COLUMN created_at;")
cursor.execute("ALTER TABLE tweets RENAME COLUMN created_at_new TO created_at;")

# Create an index on the created_at column
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_tweets_created_at ON tweets (created_at);
""")

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()
