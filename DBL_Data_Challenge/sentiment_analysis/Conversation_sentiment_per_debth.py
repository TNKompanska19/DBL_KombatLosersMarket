import os
import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import time
import pickle

# --- Load the Graph (same as before) ---
t0 = time.time()
with open("conversation_airlines_senti_correct.gpickle", "rb") as f:
    G = pickle.load(f)
print("Pickle load time (s):", time.time() - t0)


# --- 1. Calculate the depth of every node ---
print("Calculating node depths...")
# Find all root nodes (tweets with no replies to them, i.e., starting the conversation)
root_nodes = [node for node, in_degree in G.in_degree() if in_degree == 0]
print(f"Found {len(root_nodes)} root tweets (conversation starters).")

# Dictionary to store the depth of each node
node_depths = {}

# Calculate depth for nodes in each conversation thread starting from a root
for root in root_nodes:
    # shortest_path_length gives the distance from the root
    # This distance is our 'depth'
    lengths = nx.shortest_path_length(G, source=root)
    for node, depth in lengths.items():
        node_depths[node] = depth

print("Finished calculating depths.")

airline_ids = {
    56377143, 106062176, 18332190, 22536055, 124476322, 26223583,
    2182373406, 38676903, 1542862735, 253340062, 218730857,
    45621423, 20626359
}

    
# --- 2. Gather data (depth and sentiment) into a list ---
depth_sentiment_data = []
for node in G.nodes:
    user_id = G.nodes[node].get("user")
    # If the user is an airline, skip this node and continue to the next one
    if user_id in airline_ids:
        continue
    sentiment = G.nodes[node].get("sentiment_score")
    depth = node_depths.get(node) # Get the pre-calculated depth
    
    # Ensure both sentiment and depth were successfully found for the node
    if sentiment is not None and depth is not None:
        depth_sentiment_data.append({
            "depth": depth,
            "sentiment": sentiment
        })

# --- 3. Create a pandas DataFrame ---
df = pd.DataFrame(depth_sentiment_data)
print(f"\nCreated DataFrame with {len(df)} nodes that have both depth and sentiment.")
print(df.head())

# --- 4. Aggregate by depth to get mean sentiment and tweet count ---
# We calculate both 'mean' and 'count' to see how many tweets are at each depth
# This is important because means from very few data points can be misleading
sentiment_by_depth = df.groupby("depth")["sentiment"].agg(['mean', 'count']).reset_index()

# Optional: Limit the analysis to a maximum depth if the tail has very few tweets
max_depth_to_plot = 15 
sentiment_by_depth = sentiment_by_depth[sentiment_by_depth['depth'] <= max_depth_to_plot]


print("\nMean sentiment and count by conversation depth:")
print(sentiment_by_depth)


# --- 5. Create the Line Chart ---
fig, ax1 = plt.subplots(figsize=(14, 7))

# Plotting the mean sentiment on the primary y-axis (ax1)
color = 'tab:blue'
ax1.set_xlabel('Tweet Depth (0 = Root Tweet)', fontsize=12)
ax1.set_ylabel('Mean Sentiment Score', color=color, fontsize=12)
ax1.set_ylim(0.40, 0.60)
ax1.plot(sentiment_by_depth['depth'], sentiment_by_depth['mean'], color=color, marker='o', linestyle='-', label='Mean Sentiment')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, linestyle='--', alpha=0.6)

# Create a second y-axis (ax2) to show the number of tweets at each depth
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Number of Tweets (Log Scale)', color=color, fontsize=12)
ax2.set_ylim(100, 1000000)
# Using a bar chart for the count makes it easy to distinguish from the line
ax2.bar(sentiment_by_depth['depth'], sentiment_by_depth['count'], color=color, alpha=0.5, label='Tweet Count')
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_yscale('log') # Log scale is useful because tweet counts drop off very quickly

# Set plot title and layout
plt.title('Mean Sentiment by Conversation Depth for user tweets', fontsize=16)
fig.tight_layout() # Adjust plot to ensure everything fits without overlapping
plt.xticks(sentiment_by_depth['depth']) # Ensure every depth level has a tick

# Add a legend
lines, labels = ax1.get_legend_handles_labels()
bars, bar_labels = ax2.get_legend_handles_labels()
ax2.legend(lines + bars, labels + bar_labels, loc='upper right')

plt.savefig("sentiment_by_depth2_user.png", dpi=300, bbox_inches="tight")
plt.show()