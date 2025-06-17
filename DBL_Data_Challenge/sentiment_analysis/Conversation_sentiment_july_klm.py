import os
import json
import re
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import BigInteger, Text
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import gzip
import time
import pickle
import numpy as np


t0 = time.time()
with open("conversation_airlines_senti_correct.gpickle", "rb") as f:
    G = pickle.load(f)

print("Pickle load time (s):", time.time() - t0)

# --- Subgraph creation for KLM conversations ---

klm_id = {56377143}
wccs = list(nx.weakly_connected_components(G))
keep_sets = [
    comp for comp in wccs
    if any(G.nodes[n].get("user") in klm_id for n in comp)
]
nodes_to_keep = set().union(*keep_sets)
H = G.subgraph(nodes_to_keep).copy()
print(f"Created subgraph for KLM with {H.number_of_nodes()} nodes.")


# --- Data extraction loop (to get customer tweets) ---
# This correctly excludes all airline tweets from the analysis
created_times = []
sentiment_scores = []
airline_ids = {
    56377143, 106062176, 18332190, 22536055, 124476322, 26223583,
    2182373406, 38676903, 1542862735, 253340062, 218730857,
    45621423, 20626359
}
for node in H.nodes:
    user_id = H.nodes[node].get("user")
    if user_id in airline_ids:
        continue
    
    created = H.nodes[node].get("created")
    sentiment = H.nodes[node].get("sentiment_score")
    if created is not None and sentiment is not None:
        try:
            dt = pd.to_datetime(created)
            created_times.append(dt)
            sentiment_scores.append(sentiment)
        except:
            continue

# Create a DataFrame
df = pd.DataFrame({
    "created": created_times,
    "sentiment": sentiment_scores
})
df["created"] = pd.to_datetime(df["created"], errors="coerce")
print(f"Created DataFrame with {len(df)} customer tweets from KLM conversations.")

# --- MODIFICATION: Filter for July and group by day ---

# 1. Filter the DataFrame to only include data from July
#    We use .dt.month == 7 to select July.
print("\nFiltering for tweets in July...")
july_df = df[df["created"].dt.month == 7].copy()

if july_df.empty:
    print("No data found for July. Cannot create plot.")
else:
    print(f"Found {len(july_df)} customer tweets in July.")

    # 2. Extract the day of the month into a new column
    july_df['day'] = july_df['created'].dt.day

    # 3. Group by the 'day' column and calculate the mean sentiment
    print("Aggregating sentiment by day...")
    mean_sentiment_by_day_july = july_df.groupby("day")["sentiment"].mean()

    # 4. Reindex to ensure all days from 1 to 31 are present for a continuous plot
    #    Days with no data will appear as gaps in the line.
    all_july_days = range(1, 32)
    mean_sentiment_by_day_july = mean_sentiment_by_day_july.reindex(all_july_days)

    print("\nMean sentiment per day in July:")
    print(mean_sentiment_by_day_july.dropna())


    # --- Plotting the daily sentiment for July ---
    plt.figure(figsize=(14, 7))
    sns.lineplot(x=mean_sentiment_by_day_july.index, y=mean_sentiment_by_day_july.values, marker='o', color='b')
    
    # Customize the plot
    plt.title("Mean Customer Sentiment per Day in July for KLM", fontsize=16)
    plt.xlabel("Day of July", fontsize=12)
    plt.ylabel("Mean Sentiment Score", fontsize=12)
    
    # Set x-axis ticks to be every 2 days for readability
    plt.xticks(range(1, 32, 2))
    plt.xlim(0, 32) # Set x-axis limits
    
    # Set y-axis limits to zoom in on the variation
    plt.ylim(0.2, 0.6) 

    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.savefig("sentiment_per_day_july_klm.png", dpi=300, bbox_inches="tight")
    plt.show()