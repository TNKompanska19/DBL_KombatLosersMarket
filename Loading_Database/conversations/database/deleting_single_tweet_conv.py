import psycopg2
from configuration import *

# Connect to the database
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Fetch conversation IDs that have only one tweet
print("Identifying single-tweet conversations...")
cur.execute("""
    SELECT id
    FROM public.conversations
    GROUP BY id
    HAVING COUNT(*) = 1
""")
single_tweet_convs = [row[0] for row in cur.fetchall()]

# Delete the single conversations
if single_tweet_convs:
    print(f"Deleting {len(single_tweet_convs)} single-tweet conversations...")
    cur.execute("""
        DELETE FROM public.conversations
        WHERE id = ANY(%s)
    """, (single_tweet_convs,))
    conn.commit()
    print("Deletion complete.")
else:
    print("No single-tweet conversations found.")

# Clean up
cur.close()
conn.close()
