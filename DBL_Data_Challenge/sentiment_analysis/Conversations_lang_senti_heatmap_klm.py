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
with open("conversation_airlines_senti.gpickle", "rb") as f:
    G = pickle.load(f)

print("Pickle load time (s):", time.time() - t0)

airline_id = {20626359}
# 106062176, 18332190, 124476322, 20626359
wccs = list(nx.weakly_connected_components(G))
keep_sets = [
    comp for comp in wccs
    if any(G.nodes[n].get("user") in airline_id for n in comp)
]

# Induce pruned subgraph
nodes_to_keep = set().union(*keep_sets)
H = G.subgraph(nodes_to_keep).copy()

airline_ids = {
    56377143, 106062176, 18332190, 22536055, 124476322, 26223583,
    2182373406, 38676903, 1542862735, 253340062, 218730857,
    45621423, 20626359
}

languages = []
sentiment_scores = []

for node in H.nodes:
    # Get the user ID for the current node
    user_id = H.nodes[node].get("user")
    
    # If the user is an airline, skip this node and continue to the next one
    if user_id in airline_ids:
        continue
    
    language = H.nodes[node].get("language")
    sentiment = H.nodes[node].get("sentiment_score")
    
    # Add to lists if both values are valid
    if language is not None and sentiment is not None:
        languages.append(language)
        sentiment_scores.append(sentiment)

# Create a DataFrame with language and sentiment
df = pd.DataFrame({
    "language": languages,
    "sentiment": sentiment_scores
})

print("Original DataFrame shape:", df.shape)

# Get the list of the 10 most frequent languages
top_10_languages = df['language'].value_counts().nlargest(10).index.tolist()
print(f"Top 10 Languages Found: {top_10_languages}")

# Filter the DataFrame to include only these top 10 languages
df = df[df['language'].isin(top_10_languages)]
print("Shape after filtering for top 10 languages:", df.shape)

# Bin sentiment scores into labels (same as before)
bins = [-0.01, 0.125, 0.375, 0.625, 0.875, 1.01]
labels = ["Very Negative", "Negative", "Neutral", "Positive", "Very Positive"]
df["sentiment_label"] = pd.cut(df["sentiment"], bins=bins, labels=labels)

print("\nSentiment distribution in top 10 languages:")
print(df["sentiment_label"].value_counts(dropna=False))

# Group by language to calculate proportions ---
#  Count tweets per (language, sentiment_label)
counts = (
    df.groupby(["language", "sentiment_label"])
      .size()
      .reset_index(name="count")
)

# Compute total tweets per language
counts["total"] = counts.groupby("language")["count"].transform("sum")

# Compute proportion
counts["proportion"] = counts["count"] / counts["total"]

#  Enforce order on languages and sentiment 
language_order = top_10_languages 
sentiment_order = ["Very Negative", "Negative", "Neutral", "Positive", "Very Positive"]

# Convert to categorical to enforce order in the pivot table and plot
counts["language"] = pd.Categorical(counts["language"], categories=language_order, ordered=True)
counts["sentiment_label"] = pd.Categorical(counts["sentiment_label"], categories=sentiment_order, ordered=True)

# Pivot table for heatmap
heat_df = counts.pivot(index="language", columns="sentiment_label", values="proportion")

# Reindex to make sure all rows/columns exist and are in correct order
heat_df = heat_df.reindex(index=language_order, columns=sentiment_order).fillna(0)

# Print the dataframe to debug
print("\nHeat map data:")
print(heat_df)
print("\nShape:", heat_df.shape)
print("Non-null values:", heat_df.notna().sum().sum())

language_map = {
    'en': 'English',
    'und': 'Undetermined', 
    'nl': 'Dutch',
    'fr': 'French',
    'es': 'Spanish',
    'de': 'German',
    'pt': 'Portuguese',
    'in': 'Indonesian', 
    'it': 'Italian',
    'ht': 'Haitian Creole',
    'ja': 'Japanese',
    'tr': 'Turkish',
    'hi': 'Hindi',      
    'tl': 'Tagalog',    
    'pl': 'Polish',
    'et': 'Estonian'
}

# Create heatmap using matplotlib
fig, ax = plt.subplots(figsize=(12, 8))
im = ax.imshow(heat_df.values, cmap='viridis', aspect='auto')

# Set ticks and x-labels
ax.set_xticks(range(len(heat_df.columns)))
ax.set_yticks(range(len(heat_df.index)))
ax.set_xticklabels(heat_df.columns, rotation=45, ha='right')

# Use a mapping to set full language names as y-labels

full_language_names = [language_map.get(code, code) for code in heat_df.index]
ax.set_yticklabels(full_language_names)

# Add text annotations manually
for i in range(len(heat_df.index)):
    for j in range(len(heat_df.columns)):
        value = heat_df.iloc[i, j]
        text_color = 'white' if value < 0.5 else 'black'
        text = ax.text(j, i, f'{value:.3f}', 
                      ha='center', va='center', 
                      color=text_color, fontsize=10, fontweight='bold')

# Add colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Proportion of Tweets', rotation=270, labelpad=15)

# Set labels and title
ax.set_xlabel('Sentiment', fontsize=12)
ax.set_ylabel('Language (Most Frequent First)', fontsize=12)
ax.set_title('Sentiment Distribution by Language (Top 10) for Virgin Atlantic', fontsize=14)

plt.tight_layout()
plt.savefig("sentiment_heatmap_language_VirginAtlantic2_user.png", dpi=300, bbox_inches="tight")
plt.show()