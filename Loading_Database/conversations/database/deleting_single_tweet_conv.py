import psycopg2

# Database connection string
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/dbl_challenge"

# Connect to the database
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Step 1: Fetch conversation IDs that have only one tweet
print("Identifying single-tweet conversations...")
cur.execute("""
    SELECT id
    FROM public.conversations
    GROUP BY id
    HAVING COUNT(*) = 1
""")
single_tweet_convs = [row[0] for row in cur.fetchall()]

# Step 2: Delete those conversations
if single_tweet_convs:
    print(f"Deleting {len(single_tweet_convs)} single-tweet conversations...")
    cur.execute("""
        DELETE FROM public.conversations
        WHERE id = ANY(%s)
    """, (single_tweet_convs,))
    conn.commit()
    print("✅ Deletion complete.")
else:
    print("ℹ️ No single-tweet conversations found.")

# Clean up
cur.close()
conn.close()
