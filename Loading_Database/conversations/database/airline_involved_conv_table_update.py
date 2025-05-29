import psycopg2

# Database connection
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/dbl_challenge"
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Step 1: Add column if not exists
cur.execute("""
    ALTER TABLE public.conversations
    ADD COLUMN IF NOT EXISTS airline_involved BOOLEAN;
""")
conn.commit()

# Step 2: Airline user IDs
airline_user_ids = [
    56377143,     # KLM
    106062176,    # AirFrance
    18332190,     # British_Airways
    22536055,     # AmericanAir
    124476322,    # Lufthansa
    26223583,     # AirBerlin
    2182373406,   # AirBerlin assist
    38676903,     # easyJet
    1542862735,   # RyanAir
    253340062,    # SingaporeAir
    218730857,    # Qantas
    45621423,     # EtihadAirways
    20626359      # VirginAtlantic
]

# Step 3: Set all to FALSE initially
cur.execute("UPDATE public.conversations SET airline_involved = FALSE")
conn.commit()

# Step 4: Find all conversation IDs where any tweet is from an airline
cur.execute(f"""
    SELECT DISTINCT c.id
    FROM public.conversations c
    JOIN public.tweets t ON c.tweet_id = t.id
    WHERE t.user_id = ANY(%s)
""", (airline_user_ids,))
conversation_ids = [row[0] for row in cur.fetchall()]

# Step 5: Mark all tweets in those conversations as airline_involved = TRUE
if conversation_ids:
    cur.execute("""
        UPDATE public.conversations
        SET airline_involved = TRUE
        WHERE id = ANY(%s)
    """, (conversation_ids,))
    conn.commit()

# Cleanup
cur.close()
conn.close()
print("✅ All conversations updated with airline involvement.")
