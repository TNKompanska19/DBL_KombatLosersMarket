import os
import json
import pandas as pd
from sqlalchemy import create_engine
import networkx as nx
import pickle
import ast
import time

TABLE_NAME = "tweets"
DATABASE_URL = "postgresql://dbadmin:BZ6uHRGxki6a7qD@dcpostgres.postgres.database.azure.com:5432/DataChallenge"
engine = create_engine(DATABASE_URL)

query = """
SELECT
    id::text,
    in_reply_to_status_id::text,
    user_id::text,
    in_reply_to_user_id::text,
    full_text,
    created_at,
    lang,
    senti_raw_tabularis
FROM tweets
"""
tweets_df = pd.read_sql_query(query, con=engine)

print("=== DEBUGGING RAW DATA ===")
print(type(tweets_df["senti_raw_tabularis"].iloc[0]))
print(tweets_df["senti_raw_tabularis"].iloc[0])
print("Sample of raw in_reply_to_status_id values:")
print(tweets_df["in_reply_to_status_id"].head(10).tolist())
print("\nUnique types in in_reply_to_status_id:")
print(tweets_df["in_reply_to_status_id"].apply(type).value_counts())
print("\nNon-null in_reply_to_status_id count:", tweets_df["in_reply_to_status_id"].notna().sum())

# Check a specific test case
test_child = "1142827347370029057"
test_parent = "1142825622932250630"

print(f"\n=== CHECKING TEST CASE ===")
child_row = tweets_df[tweets_df["id"] == test_child]
if not child_row.empty:
    print(f"Child tweet {test_child} found:")
    print(f"  Raw in_reply_to_status_id: '{child_row.iloc[0]['in_reply_to_status_id']}'")
    print(f"  Type: {type(child_row.iloc[0]['in_reply_to_status_id'])}")
else:
    print(f"Child tweet {test_child} NOT found in dataset")

parent_row = tweets_df[tweets_df["id"] == test_parent]
if not parent_row.empty:
    print(f"Parent tweet {test_parent} found:")
else:
    print(f"Parent tweet {test_parent} NOT found in dataset")

def improved_safe_int(val):
    """Improved version that handles large integers correctly"""
    if pd.isna(val) or val is None:
        return None
    
    # Handle string types
    if isinstance(val, str):
        val_str = val.strip()
        if val_str.lower() in ['none', 'null', '', 'nan']:
            return None
        try:
            # Convert directly to int, avoiding float conversion
            return int(val_str)
        except (ValueError, TypeError):
            print(f"Failed to convert string: '{val}'")
            return None
    
    # Handle numeric types
    if isinstance(val, (int, float)):
        if pd.isna(val):
            return None
       
        return int(val)
    
    # Convert to string first, then to int
    try:
        val_str = str(val).strip()
        if val_str.lower() in ['none', 'null', '', 'nan']:
            return None
        return int(val_str)
    except (ValueError, TypeError):
        print(f"Failed to convert: '{val}' (type: {type(val)})")
        return None

# Apply improved conversion with proper dtypes
print("\n=== APPLYING IMPROVED CONVERSION ===")

# Create conversion dictionaries to avoid pandas dtype issues
id_dict = {}
user_id_dict = {}
reply_to_dict = {}
reply_to_user_dict = {}

for idx, row in tweets_df.iterrows():
    id_dict[idx] = improved_safe_int(row["id"])
    user_id_dict[idx] = improved_safe_int(row["user_id"])
    reply_to_dict[idx] = improved_safe_int(row["in_reply_to_status_id"])
    reply_to_user_dict[idx] = improved_safe_int(row["in_reply_to_user_id"])

# Add as object type to prevent automatic conversion
tweets_df["id_int"] = pd.Series(id_dict, dtype='object')
tweets_df["user_id_int"] = pd.Series(user_id_dict, dtype='object')
tweets_df["in_reply_to_status_id_int"] = pd.Series(reply_to_dict, dtype='object')
tweets_df["in_reply_to_user_id_int"] = pd.Series(reply_to_user_dict, dtype='object')

print("After conversion:")
print("Non-null in_reply_to_status_id_int count:", tweets_df["in_reply_to_status_id_int"].notna().sum())

# Check test case after conversion
if not child_row.empty:
    child_idx = child_row.index[0]
    print(f"\nTest case after conversion:")
    print(f"  Child in_reply_to_status_id_int: {tweets_df.loc[child_idx, 'in_reply_to_status_id_int']}")

label_to_score = {
    "Very Negative": 0.0,
    "Negative": 0.25,
    "Neutral": 0.5,
    "Positive": 0.75,
    "Very Positive": 1.0,
}

G = nx.DiGraph()
orig_ids_set = set()

# Add nodes using the converted integer IDs
for idx, row in tweets_df.iterrows():
    node_id = row["id_int"]
    user_id = row["user_id_int"]
    
    if node_id is None or user_id is None:
        continue

    try:
        sentiment_data = ast.literal_eval(row["senti_raw_tabularis"])
        label = sentiment_data.get("label", "Neutral")
    except Exception:
        label = "Neutral"

    score = label_to_score.get(label)  

    G.add_node(
        node_id,
        user=user_id,
        text=row["full_text"],
        created=row["created_at"],
        language=row["lang"],
        sentiment_score=score
    )
    
    orig_ids_set.add(node_id)
# Add edges using the converted integer IDs
edges_added = 0
missing = 0

for idx, row in tweets_df.iterrows():
    parent = row["in_reply_to_status_id_int"]
    child = row["id_int"]

    if parent is None or child is None:
        continue

    if parent in orig_ids_set and child in orig_ids_set:
        G.add_edge(parent, child, relation="reply")
        edges_added += 1
    else:
        missing += 1

# Analysis using converted IDs
parent_ids = set(filter(None, tweets_df["in_reply_to_status_id_int"]))
tweet_ids = set(filter(None, tweets_df["id_int"]))
intersection = parent_ids & tweet_ids

print("Reply IDs in dataset:", len(parent_ids))
print("Matching parent tweets in dataset:", len(intersection))
print("Edges added:", edges_added)
print("Missing edge candidates:", missing)

# Manual test with converted IDs
p_id = int(test_parent)
c_id = int(test_child)

print(f"\n=== MANUAL TEST ===")
print("Parent in graph?", G.has_node(p_id))
print("Child in graph?", G.has_node(c_id))
print("Edge present?", G.has_edge(p_id, c_id))

# Additional debugging for the test case
if G.has_node(c_id):
    child_data = G.nodes[c_id]
    print(f"Child node data: {child_data}")

t0 = time.time()

# Define the set of airline user IDs
airline_ids = {
    56377143, 106062176, 18332190, 22536055, 124476322, 26223583,
    2182373406, 38676903, 1542862735, 253340062, 218730857,
    45621423, 20626359
}

# "Mark" all nodes that were posted by an airline.
print("\nStep 1: Finding all tweets posted by airlines...")
airline_nodes = {
    node for node, data in G.nodes(data=True) 
    if data.get('user') in airline_ids
}
print(f"Found {len(airline_nodes)} airline tweets.")

# "Propagate" from the marked nodes to find all ancestors and descendants.
print("Step 2: Finding all ancestors and descendants of airline tweets...")

# Initialize the set of nodes to keep with the airline tweets themselves.
nodes_to_keep = set(airline_nodes)

# Loop through each airline tweet and gather its ancestors and descendants
for i, node in enumerate(airline_nodes):
    if (i + 1) % 100 == 0:
        print(f"  ... processing airline node {i+1}/{len(airline_nodes)}")
    
    # Add all nodes that lead TO this airline tweet
    ancestors = nx.ancestors(G, node)
    nodes_to_keep.update(ancestors)
    
    # Add all nodes that come FROM this airline tweet
    descendants = nx.descendants(G, node)
    nodes_to_keep.update(descendants)

print(f"\nIdentified a total of {len(nodes_to_keep)} nodes to keep.")

# Create the new subgraph from the collected set of nodes
H = G.subgraph(nodes_to_keep).copy()
print(f"New pruned graph 'H' has {H.number_of_nodes()} nodes and {H.number_of_edges()} edges.")

cript_dir = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.dirname(script_dir)

# Define the target folder for our data, relative to the project root
data_folder = os.path.join(project_root, "data")

# Define the filename
filename = "conversation_airlines_senti_correct.gpickle"

# Create the data directory if it doesn't exist
os.makedirs(data_folder, exist_ok=True)

# Combine the folder and filename into the full, final path
full_path = os.path.join(data_folder, filename)

print(f"\nSaving the pruned graph to the relative project path: {full_path}")

# Write the new graph file using the full path
with open(full_path, "wb") as f:
    pickle.dump(H, f, protocol=pickle.HIGHEST_PROTOCOL)


print(f"\nSuccessfully saved the new graph to 'conversation_airlines_senti_correct.gpickle'.")
print(f"Total process time: {time.time() - t0:.2f} seconds.")
