import psycopg2
from collections import defaultdict
from configuration import *
# Connect to the database
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Step 1: Create the new table
cur.execute("""
CREATE TABLE IF NOT EXISTS public.conversations (
    id BIGINT NOT NULL,
    tweet_id BIGINT NOT NULL,
    conversation_length INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    position INTEGER NOT NULL,
    PRIMARY KEY (id, tweet_id)
);
""")
conn.commit()

# Step 2: Load tweets with timestamps and reply links
print("Loading tweets...")
cur.execute("SELECT id, in_reply_to_status_id, created_at FROM public.tweets")
rows = cur.fetchall()

# Step 3: Build reply graph
reply_graph = defaultdict(list)
reply_to = {}
tweet_time = {}

for tweet_id, reply_id, created_at in rows:
    tweet_time[tweet_id] = created_at
    if reply_id:
        reply_graph[reply_id].append(tweet_id)
        reply_to[tweet_id] = reply_id

# Step 4: DFS to find linear conversations
visited = set()
conversations = []
conv_id = 1

def dfs(path):
    current = path[-1]
    if current not in reply_graph or not reply_graph[current]:  # Leaf node
        global conv_id
        conv_len = len(path)
        start_time = tweet_time[path[0]]
        end_time = tweet_time[path[-1]]

        for idx, tweet in enumerate(path):
            conversations.append((
                conv_id, tweet, conv_len, start_time, end_time, idx
            ))
        conv_id += 1
        return

    for child in reply_graph[current]:
        dfs(path + [child])

# Step 5: Start DFS from root tweets
print("Building conversations...")
all_tweet_ids = set(tweet_time.keys())
roots = all_tweet_ids - set(reply_to.keys())

for root in roots:
    dfs([root])

# Step 6: Insert into conversations
print(f"Inserting {len(conversations)} tweets into conversations...")
batch_size = 1000
for i in range(0, len(conversations), batch_size):
    batch = conversations[i:i + batch_size]
    args_str = ",".join(cur.mogrify("(%s, %s, %s, %s, %s, %s)", rec).decode("utf-8") for rec in batch)
    cur.execute(f"""
        INSERT INTO public.conversations (id, tweet_id, conversation_length, start_time, end_time, position)
        VALUES {args_str}
        ON CONFLICT DO NOTHING
    """)

conn.commit()
cur.close()
conn.close()
print("All conversations inserted into conversations table.")
