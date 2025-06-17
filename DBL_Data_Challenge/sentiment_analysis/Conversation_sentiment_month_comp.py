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

# --- 1. SETUP ---
t0 = time.time()
with open("conversation_airlines_senti_correct.gpickle", "rb") as f:
    G = pickle.load(f)
print("Pickle load time (s):", time.time() - t0)

# Define the target airlines with their IDs and names
target_airlines = {
    56377143: 'KLM',
    106062176: 'Air France',
    18332190: 'British Airways',
    124476322: 'Lufthansa',
    20626359: 'Virgin Atlantic'
}

# Define a master list of ALL airline IDs to filter out their tweets later
all_airline_ids = {
    56377143, 106062176, 18332190, 22536055, 124476322, 26223583,
    2182373406, 38676903, 1542862735, 253340062, 218730857,
    45621423, 20626359
}

# Pre-calculate weakly connected components once to save time
wccs = list(nx.weakly_connected_components(G))

# This list will hold data from all airlines before creating the final DataFrame
all_customer_tweets = []


# --- 2. LOOP THROUGH EACH AIRLINE TO GATHER DATA ---
for airline_id, airline_name in target_airlines.items():
    print(f"\nProcessing data for {airline_name} (ID: {airline_id})...")
    
    # a. Isolate conversations involving the current airline
    keep_sets = [
        comp for comp in wccs
        if any(G.nodes[n].get("user") == airline_id for n in comp)
    ]
    nodes_to_keep = set().union(*keep_sets)
    H = G.subgraph(nodes_to_keep)
    print(f"  Found {H.number_of_nodes()} nodes in conversations involving {airline_name}.")
    
    # b. Extract customer tweets from this airline's conversations
    for node in H.nodes:
        user_id = H.nodes[node].get("user")
        
        created = H.nodes[node].get("created")
        sentiment = H.nodes[node].get("sentiment_score")
        
        if created is not None and sentiment is not None:
            try:
                dt = pd.to_datetime(created)
                # Append a dictionary with all necessary info
                all_customer_tweets.append({
                    'airline': airline_name,
                    'created': dt,
                    'sentiment': sentiment
                })
            except:
                continue

# --- 3. CREATE AND PREPARE THE MASTER DATAFRAME ---
df = pd.DataFrame(all_customer_tweets)
print(f"\nCreated a single DataFrame with {len(df)} total customer tweets.")

# Convert 'created' column to datetime objects
df["created"] = pd.to_datetime(df["created"], errors="coerce")

# Create a 'month' column for grouping
df["month"] = df["created"].dt.month_name()


# --- 4. AGGREGATE DATA FOR PLOTTING ---
# Group by both airline and month to get the mean sentiment
mean_sentiment_by_month = (
    df.groupby(["airline", "month"])["sentiment"]
      .mean()
      .reset_index()
)

# Enforce a calendar order on the months for correct plotting
ordered_months = [
    "May", "June", "July", "August", "September", "October", 
    "November", "December", "January", "February", "March", "April"
]
mean_sentiment_by_month["month"] = pd.Categorical(
    mean_sentiment_by_month["month"], categories=ordered_months, ordered=True
)

# Sort the data to ensure lines connect correctly
mean_sentiment_by_month = mean_sentiment_by_month.sort_values("month")

print("\nAggregated mean sentiment data:")
print(mean_sentiment_by_month.head())


# --- 5. PLOTTING ---
plt.figure(figsize=(14, 8))

# Use seaborn's 'hue' parameter to automatically create a line for each airline
sns.lineplot(
    data=mean_sentiment_by_month,
    x='month',
    y='sentiment',
    hue='airline',  
    marker='o',
    linestyle='-',
    linewidth=3 
)

plt.title("Mean Sentiment by Month for all tweets (KLM and competitors)", fontsize=16)
plt.xlabel("Month", fontsize=12)
plt.ylabel("Mean Sentiment Score", fontsize=12)
plt.xticks(rotation=45)
plt.ylim(0.40, 0.75)  
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(title='Airline')
plt.tight_layout()
plt.savefig("sentiment_per_month_competitors_all.png", dpi=300, bbox_inches="tight")
plt.show()