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

FOLDER = r"C:\New folder"
TABLE_NAME = "tweets"
DATABASE_URL = "postgresql://dbadmin:BZ6uHRGxki6a7qD@dcpostgres.postgres.database.azure.com:5432/DataChallenge"

t0 = time.time()
with open(os.path.join(FOLDER, "conversation_airlines.gpickle"), "rb") as f:
    G = pickle.load(f)

total_nodes = G.number_of_nodes()

wccs = list(nx.weakly_connected_components(G))
num_weakly_connected_components = len(wccs)
wcc_sizes = [len(c) for c in wccs]

num_singleton_wcc = wcc_sizes.count(1)
avg_num_of_nodes_per_thread = total_nodes/num_weakly_connected_components
avg_num_of_nodes_per_nonsing_thread = (total_nodes - num_singleton_wcc) / (num_weakly_connected_components - num_singleton_wcc)  

num_NON_singleton_wcc = num_weakly_connected_components - num_singleton_wcc 

non_singleton_wccs = [wcc for wcc in nx.weakly_connected_components(G) if len(wcc) > 1]
branch_counts = []

import networkx as nx

def compute_average_depth(G):
    depths = []
    for component in nx.weakly_connected_components(G):
        subgraph = G.subgraph(component)
        roots = [n for n in subgraph.nodes if subgraph.in_degree(n) == 0]
        for root in roots:
            lengths = nx.single_source_shortest_path_length(subgraph, root)
            depths.extend(lengths.values())
    average_depth = sum(depths) / len(depths) if depths else 0
    return average_depth
print(compute_average_depth(G))

branch_lengths = []

for component in nx.weakly_connected_components(G):
    subgraph = G.subgraph(component)
    roots = [n for n in subgraph.nodes if subgraph.in_degree(n) == 0]
    leaves = [n for n in subgraph.nodes if subgraph.out_degree(n) == 0]

    for root in roots:
        paths = nx.single_source_shortest_path(subgraph, root)
        for leaf in leaves:
            if leaf in paths:
                path = paths[leaf]
                branch_lengths.append(len(path))  



length_counts = {
    "Length 2": sum(1 for l in branch_lengths if l == 2),
    "Length 3": sum(1 for l in branch_lengths if l == 3),
    "Length 4": sum(1 for l in branch_lengths if l == 4),
    "Length 5": sum(1 for l in branch_lengths if l == 5),
    "Length >5": sum(1 for l in branch_lengths if l > 5)
}


total = sum(length_counts.values())
mean_length = sum(branch_lengths) / len(branch_lengths)


labels = [f"{k} — {v:,} ({v/total:.1%})" for k, v in length_counts.items()]
sizes = list(length_counts.values())
colors = plt.cm.Pastel1.colors[:len(sizes)]


fig, ax = plt.subplots(figsize=(9, 6))
wedges, texts = ax.pie(
    sizes,
    labels=None,
    startangle=90,
    colors=colors,
    wedgeprops=dict(width=0.4)
)

ax.legend(wedges, labels, title="Conversation Lengths", loc="center left", bbox_to_anchor=(1, 0.5))


plt.title("Conversation Length Distribution", fontsize=14)

text_summary = f"Mean Length: {mean_length:.2f}\nTotal Conversations: {total}"
plt.text(0, 0, text_summary, ha='center', va='center', fontsize=11)

ax.axis("equal")  
plt.tight_layout()
#plt.savefig(r"C:\Users\20243895\OneDrive - TU Eindhoven\Desktop\DBL\New folder\Conversations_trans_final.png", dpi=300, bbox_inches="tight", transparent=True)
plt.show()