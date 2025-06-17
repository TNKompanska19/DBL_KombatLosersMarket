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

airline_id = {56377143}
# AirFrance 106062176, British_Airways 18332190, Lufthansa 124476322, VirginAtlantic 20626359
wccs = list(nx.weakly_connected_components(G))
keep_sets = [
    comp for comp in wccs
    if any(G.nodes[n].get("user") in airline_id for n in comp)
]

# Induce pruned subgraph
nodes_to_keep = set().union(*keep_sets)
H = G.subgraph(nodes_to_keep).copy()

created_times = []
sentiment_scores = []

airline_ids = {
    56377143, 106062176, 18332190, 22536055, 124476322, 26223583,
    2182373406, 38676903, 1542862735, 253340062, 218730857,
    45621423, 20626359
}

for node in H.nodes:
    user_id = H.nodes[node].get("user")
    
    # If the user is an airline, skip this node and continue to the next one
    if user_id in airline_ids:
        continue
    created = H.nodes[node].get("created")
    sentiment = H.nodes[node].get("sentiment_score")  # Adjust key if different, e.g., 'sentiment_score'
    
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

#df["sentiment"] = pd.to_numeric(df["sentiment"], errors="coerce")
print(df["sentiment"].head(10))
print(df["sentiment"].describe())
# Extract hour of day
df["created"] = pd.to_datetime(df["created"], errors="coerce")
df["month"] = df["created"].dt.month_name()

ordered_months = [
    "May", "June",
    "July", "August", "September", "October", "November", "December","January", "February", "March", "April",
]
april_tweets = df[df["created"].dt.month_name() == "April"]

# Check how many tweets are in April
print(f"Number of tweets in April: {len(april_tweets)}")

# Optionally print them
if not april_tweets.empty:
    print(april_tweets)
# Group by month name
mean_sentiment_by_month = (
    df.groupby("month")["sentiment"]
    .mean()
    .reindex(ordered_months)
)

# Print descriptive stats
print(df.groupby("month")["sentiment"].describe().reindex(ordered_months))

# Plotting
plt.figure(figsize=(10, 5))
sns.lineplot(x=mean_sentiment_by_month.index, y=mean_sentiment_by_month.values, marker='o')
plt.xticks(range(0, 12))
plt.yticks(np.arange(0, 1.1, 0.01))
plt.ylim(0.4, 0.6)  # Force Y-axis from 0 to 1
plt.title("Mean Sentiment Score by Months for KLM user tweets", fontsize=14)
plt.xlabel("Months", fontsize=12)
plt.ylabel("Mean Sentiment Score", fontsize=12)
plt.grid(True)
plt.tight_layout()
plt.savefig("sentiment_per_month_KLM_user2.png", dpi=300, bbox_inches="tight")
plt.show()