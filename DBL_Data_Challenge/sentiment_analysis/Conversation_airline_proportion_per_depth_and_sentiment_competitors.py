import os
import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import time
import pickle

# --- Load the Graph ---
t0 = time.time()
with open("conversation_airlines_senti_correct.gpickle", "rb") as f:
    G = pickle.load(f)
print("Pickle load time (s):", time.time() - t0)

# Define the relevant airlines
airline_keep = {20626359}

# 106062176, 18332190, 124476322, 20626359
wccs = list(nx.weakly_connected_components(G))
keep_sets = [
    comp for comp in wccs
    if any(G.nodes[n].get("user") in airline_keep for n in comp)
]

# Induce pruned subgraph, to eliminate other airlines
nodes_to_keep = set().union(*keep_sets)
H = G.subgraph(nodes_to_keep).copy()
# --- Define the set of airline user IDs ---
airline_ids = {
    56377143, 106062176, 18332190, 22536055, 124476322, 26223583,
    2182373406, 38676903, 1542862735, 253340062, 218730857,
    45621423, 20626359
}

# ---  Calculate the depth of every node (same as before) ---
print("\nCalculating node depths...")
root_nodes = [node for node, in_degree in G.in_degree() if in_degree == 0]
print(f"Found {len(root_nodes)} root tweets (conversation starters).")

node_depths = {}
for root in root_nodes:
    lengths = nx.shortest_path_length(G, source=root)
    for node, depth in lengths.items():
        node_depths[node] = depth
print("Finished calculating depths.")


# ---  Gather comprehensive data (depth, sentiment, and is_airline) ---
all_data = []
for node in H.nodes:
    depth = node_depths.get(node)
    sentiment = H.nodes[node].get("sentiment_score")
    user_id = H.nodes[node].get('user')
    
    if all(v is not None for v in [depth, sentiment, user_id]):
        is_airline = user_id in airline_ids
        all_data.append({
            "depth": depth,
            "sentiment": sentiment,
            "is_airline": is_airline
        })

# ---  Create a pandas DataFrame ---
df = pd.DataFrame(all_data)
print(f"\nCreated DataFrame with {len(df)} nodes.")
print(df.head())


# ---  Aggregate by depth to get both proportion and mean sentiment ---

agg_df = df.groupby('depth').agg(
    proportion=('is_airline', 'mean'),
    mean_sentiment=('sentiment', 'mean')
).reset_index()

# Limit the analysis to a maximum depth
max_depth_to_plot = 15 
final_df = agg_df[agg_df['depth'] <= max_depth_to_plot]

print("\nAirline Proportion and Mean Sentiment by Conversation Depth:")
print(final_df)


# ---  Create the Dual-Axis Line Chart
fig, ax1 = plt.subplots(figsize=(14, 7))

# Plotting Airline Proportion on the primary y-axis (ax1)
color1 = 'tab:green'
ax1.set_xlabel('Tweet Depth (0 = Root Tweet)', fontsize=12)
ax1.set_ylabel('Proportion of Tweets by Airlines', color=color1, fontsize=12)
ax1.set_ylim(0, 1.0)
ax1.plot(final_df['depth'], final_df['proportion'], color=color1, marker='o', linestyle='-', label='Airline Tweet Proportion')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True, which='major', linestyle='--', axis='y', alpha=0.6)


# Create a second y-axis (ax2) for the Mean Sentiment
ax2 = ax1.twinx()
color2 = 'tab:blue'
ax2.set_ylabel('Mean Sentiment Score', color=color2, fontsize=12)
#ax2.set_ylim(0.40, 0.60) 
ax2.plot(final_df['depth'], final_df['mean_sentiment'], color=color2, marker='s', linestyle='--', label='Mean Sentiment')
ax2.tick_params(axis='y', labelcolor=color2)

# Set plot title and layout
plt.title('Airline Engagement and Sentiment by Conversation Depth for Virgin Atlantic', fontsize=16)
fig.tight_layout()
plt.xticks(final_df['depth'])

# Add a combined legend
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc='upper right')

plt.savefig("proportion_vs_sentiment_by_depth_VirginAtlantic_adjusted.png", dpi=300, bbox_inches="tight")
plt.show()