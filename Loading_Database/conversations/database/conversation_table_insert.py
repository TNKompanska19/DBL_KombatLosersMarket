import psycopg2
from collections import defaultdict

# Database connection string
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/dbl_challenge"

# Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Step 1: Create conversations table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS public.conversations (
    id BIGINT NOT NULL,
    tweet_id BIGINT NOT NULL,
    PRIMARY KEY (id, tweet_id)
);
""")
conn.commit()

# Step 2: Load tweets
print("Loading tweets...")
cur.execute("SELECT id, in_reply_to_status_id FROM public.tweets")
rows = cur.fetchall()

# Step 3: Prepare structures
parent = {}  # keeps track of each tweet's parent (initially, every tweet is its own parent
reply_graph = defaultdict(list) # maps a tweet_id to a list of tweets that reply to it
participating_tweets = set() # a set of tweet ids that participate in at least one reply relationship

# Initialize parent and track participating tweets
for tweet_id, reply_id in rows:
    parent[tweet_id] = tweet_id
    if reply_id:
        participating_tweets.add(tweet_id)
        participating_tweets.add(reply_id)
        reply_graph[reply_id].append(tweet_id)

# Union-Find functions
def find(x):
    """"
        Find the root parent of a tweet by following parent links.
        Uses path compression to speed up future lookups by pointing nodes directly to the root.
    """
    while parent[x] != x:
        parent[x] = parent[parent[x]]  # Path compression
        x = parent[x]
    return x

def union(x, y):
    """
    Finds the roots of tweets x and y. If they differ, merges the two sets by linking one root to the other.
    Thus, tweets in the same conversation get connected.
    :param x: tweet x
    :param y: tweet y
    """
    x_root = find(x)
    y_root = find(y)
    if x_root != y_root:
        parent[y_root] = x_root

# Step 4: Build unions only if both tweets exist
print("Building unions...")

# For each tweet that replies to another tweet (and that parent tweet exists in the dataset), perform a union operation.
for tweet_id, reply_id in rows:
    if reply_id and reply_id in parent:
        union(tweet_id, reply_id) # This merges reply chains into connected groups, each group representing a conversation.

# Step 5: Assign unique conversation IDs
print("Assigning conversation IDs...")
root_to_conv = {}
conversations = []
conv_id_counter = 1

for tweet_id in participating_tweets:
    if tweet_id not in parent:
        continue  # skip tweets whose parents don't exist
    root = find(tweet_id)
    if root not in root_to_conv:
        root_to_conv[root] = conv_id_counter
        conv_id_counter += 1
    conversations.append((root_to_conv[root], tweet_id))

# Step 6: Insert into database
print(f"Inserting {len(conversations)} tweets into conversations...")
batch_size = 1000
for i in range(0, len(conversations), batch_size):
    batch = conversations[i:i+batch_size]
    args_str = ",".join(cur.mogrify("(%s, %s)", rec).decode("utf-8") for rec in batch)
    cur.execute(f"""
        INSERT INTO public.conversations (id, tweet_id)
        VALUES {args_str}
        ON CONFLICT DO NOTHING
    """)

conn.commit()
cur.close()
conn.close()
print("✅ All conversations inserted successfully.")
