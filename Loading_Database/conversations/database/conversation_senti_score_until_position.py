import sys,os
import psycopg2
import json
from collections import defaultdict
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))
from configuration import *

# Connect to DB
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Add column if it doesn't exist
cur.execute("""
    ALTER TABLE public.conversations
    ADD COLUMN IF NOT EXISTS senti_score_until_now FLOAT;
""")
conn.commit()

# Load tweets with conversation id, tweet id, timestamp, and sentiment
cur.execute("""
    SELECT c.id, c.tweet_id, t.created_at, t.senti_raw_tabularis
    FROM public.conversations c
    JOIN public.tweets t ON c.tweet_id = t.id
""")
rows = cur.fetchall()

# Group tweets by conversation and sort them
senti_mapping = {
    'Very Negative': 0.0,
    'Negative': 0.25,
    'Neutral': 0.5,
    'Positive': 0.75,
    'Very Positive': 1.0
}

conversations = defaultdict(list)
for conv_id, tweet_id, created_at, senti_raw in rows:
    conversations[conv_id].append((tweet_id, created_at, senti_raw))

# Calculate senti_score_until_now for each tweet
updates = []
for conv_id, tweets in conversations.items():
    tweets.sort(key=lambda x: x[1])  # sort by created_at
    senti_sum = 0
    count = 0
    for tweet_id, _, senti_raw in tweets:
        try:
            parsed = json.loads(senti_raw.replace("'", "\""))
            label = parsed.get('label')
            score = senti_mapping.get(label, 0.5)
        except Exception:
            score = 0.5
        senti_sum += score
        count += 1
        avg_so_far = senti_sum / count
        updates.append((avg_so_far, conv_id, tweet_id))

# Update senti_score_until_now in batches
batch_size = 1000
for i in range(0, len(updates), batch_size):
    batch = updates[i:i+batch_size]
    args_str = ",".join(cur.mogrify("(%s, %s, %s)", x).decode() for x in batch)
    cur.execute(f"""
        UPDATE public.conversations AS c SET senti_score_until_now = vals.avg
        FROM (VALUES {args_str}) AS vals(avg, conv_id, tweet_id)
        WHERE c.id = vals.conv_id AND c.tweet_id = vals.tweet_id
    """)
conn.commit()

print("Updated senti_score_until_now for all tweets.")