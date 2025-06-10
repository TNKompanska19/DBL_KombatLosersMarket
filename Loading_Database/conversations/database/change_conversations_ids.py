import psycopg2
from configuration import *

# Connect to DB
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Get distinct conversation IDs in current order of appearance
cur.execute("""
    SELECT DISTINCT id
    FROM public.conversations
""")
ids = [row[0] for row in cur.fetchall()]

# Create mapping old_id -> new_id
id_mapping = {old_id: new_id for new_id, old_id in enumerate(ids, start=1)}


# Add a temporary column to store new_id
cur.execute("""
    ALTER TABLE public.conversations
    ADD COLUMN IF NOT EXISTS new_temp_id INT;
""")
conn.commit()

# Fill temporary column with new ids
for old_id, new_id in id_mapping.items():
    cur.execute("""
        UPDATE public.conversations
        SET new_temp_id = %s
        WHERE id = %s
    """, (new_id, old_id))
conn.commit()

# Drop primary key temporarily
cur.execute("""
    ALTER TABLE public.conversations
    DROP CONSTRAINT conversations_pkey;
""")
conn.commit()

# Overwrite old id with new id
cur.execute("""
    UPDATE public.conversations
    SET id = new_temp_id;
""")
conn.commit()

# Drop temp column and recreate primary key
cur.execute("""
    ALTER TABLE public.conversations
    DROP COLUMN new_temp_id;
""")
conn.commit()

cur.execute("""
    ALTER TABLE public.conversations
    ADD PRIMARY KEY (id, tweet_id);
""")
conn.commit()

cur.close()
conn.close()
print("✅ Conversation IDs successfully reassigned starting from 1 based on original order.")
