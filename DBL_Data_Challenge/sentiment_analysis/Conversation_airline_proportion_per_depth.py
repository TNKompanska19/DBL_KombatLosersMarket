import os
import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import time
import pickle

# Load the Graph
t0 = time.time()
with open("conversation_airlines_senti_correct.gpickle", "rb") as f:
    G = pickle.load(f)
print("Pickle load time (s):", time.time() - t0)

# Defining the set of airline user IDs
airline_ids = {
    56377143, 106062176, 18332190, 22536055, 124476322, 26223583,
    2182373406, 38676903, 1542862735, 253340062, 218730857,
    45621423, 20626359
}

# Calculate the depth of every node 
print("\nCalculating node depths...")
root_nodes = [node for node, in_degree in G.in_degree() if in_degree == 0]
print(f"Found {len(root_nodes)} root tweets (conversation starters).")

node_depths = {}
for root in root_nodes:
    lengths = nx.shortest_path_length(G, source=root)
    for node, depth in lengths.items():
        node_depths[node] = depth
print("Finished calculating depths.")


# Gather data (depth and whether it's an airline tweet)
depth_airline_data = []
for node in G.nodes:
    depth = node_depths.get(node)
    user_id = G.nodes[node].get('user')
    
    if depth is not None and user_id is not None:
        is_airline = user_id in airline_ids
        depth_airline_data.append({
            "depth": depth,
            "is_airline": is_airline
        })

# Create a pandas DataFrame
df = pd.DataFrame(depth_airline_data)
print(f"\nCreated DataFrame with {len(df)} nodes.")
print(df.head())


#  Aggregate by depth to get airline tweet proportion

agg_df = df.groupby('depth')['is_airline'].agg(
    airline_count=lambda x: x.sum(), # Sum of booleans (True=1, False=0)
    total_count='count'
).reset_index()

# Calculate the proportion
agg_df['proportion'] = agg_df['airline_count'] / agg_df['total_count']

# Limit the analysis to a maximum depth
max_depth_to_plot = 15 
airline_proportion_by_depth = agg_df[agg_df['depth'] <= max_depth_to_plot]

print("\nProportion of airline tweets by conversation depth:")
print(airline_proportion_by_depth)


# Create the Line Chart
fig, ax1 = plt.subplots(figsize=(14, 7))

# Plotting the airline proportion on the primary y-axis (ax1)
color = 'tab:green'
ax1.set_xlabel('Tweet Depth (0 = Root Tweet)', fontsize=12)
ax1.set_ylabel('Proportion of Tweets by Airlines', color=color, fontsize=12)
ax1.set_ylim(0, 1.0) 
ax1.plot(airline_proportion_by_depth['depth'], airline_proportion_by_depth['proportion'], color=color, marker='o', linestyle='-', label='Airline Tweet Proportion')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, linestyle='--', alpha=0.6)

# Create a second y-axis (ax2) to show the total number of tweets for context
ax2 = ax1.twinx()
color = 'tab:gray'
ax2.set_ylabel('Total Number of Tweets (Log Scale)', color=color, fontsize=12)
ax2.bar(airline_proportion_by_depth['depth'], airline_proportion_by_depth['total_count'], color=color, alpha=0.5, label='Total Tweet Count')
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_yscale('log')

# Set plot title and layout
plt.title('Proportion of Airline Tweets by Conversation Depth', fontsize=16)
fig.tight_layout()
plt.xticks(airline_proportion_by_depth['depth'])

# Add a combined legend
lines, labels = ax1.get_legend_handles_labels()
bars, bar_labels = ax2.get_legend_handles_labels()
ax2.legend(lines + bars, labels + bar_labels, loc='upper right')

#plt.savefig("airline_proportion_by_depth.png", dpi=300, bbox_inches="tight")
plt.show()