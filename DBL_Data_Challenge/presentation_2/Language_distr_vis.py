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
for wcc in non_singleton_wccs:
    subgraph = G.subgraph(wcc)
    branches = sum(1 for node in subgraph if subgraph.out_degree(node) > 0)
    branch_counts.append(branches)
total_branches = sum(branch_counts)
print(f"Total number of branches in non-singleton threads: {total_branches}")


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

from collections import Counter

branch_language_majority = []


non_singleton_wccs = [wcc for wcc in nx.weakly_connected_components(G) if len(wcc) > 1]


for wcc in non_singleton_wccs:
    subgraph = G.subgraph(wcc)
    roots = [n for n in subgraph.nodes if subgraph.in_degree(n) == 0]
    leaves = [n for n in subgraph.nodes if subgraph.out_degree(n) == 0]

    for root in roots:
        paths = nx.single_source_shortest_path(subgraph, root)
        for leaf in leaves:
            if leaf in paths:
                path = paths[leaf]
                langs = [G.nodes[n].get("language") for n in path if G.nodes[n].get("language") is not None]
                if langs:
                    majority_lang = Counter(langs).most_common(1)[0][0]
                    branch_language_majority.append(majority_lang)


branch_lang_counts = Counter(branch_language_majority)

branch_lang_df = pd.DataFrame(branch_lang_counts.items(), columns=["Language", "Branch Count"])
branch_lang_df = branch_lang_df.sort_values(by="Branch Count", ascending=False)


total_branches = sum(branch_lang_counts.values())
branch_lang_df["Percentage"] = (branch_lang_df["Branch Count"] / total_branches) * 100


threshold = 0.6  
main_langs_df = branch_lang_df[branch_lang_df["Percentage"] >= threshold].copy()
other_df = branch_lang_df[branch_lang_df["Percentage"] < threshold]

 
if not other_df.empty:
    other_row = pd.DataFrame([{
        "Language": "Other",
        "Branch Count": other_df["Branch Count"].sum(),
        "Percentage": other_df["Percentage"].sum()
    }])
    branch_lang_df_plot = pd.concat([main_langs_df, other_row], ignore_index=True)
else:
    branch_lang_df_plot = main_langs_df


branch_lang_df_plot = branch_lang_df_plot.sort_values(by="Percentage", ascending=False)


plt.figure(figsize=(10, 6))
sns.barplot(
    data=branch_lang_df_plot,
    y="Language",
    x="Percentage",
    palette="viridis",
    order=branch_lang_df_plot["Language"]  
)


for i, row in branch_lang_df_plot.iterrows():
    plt.text(
        x=row["Percentage"],
        y=i,
        s=f"{row['Percentage']:.1f}%",
        va='center'
    )

plt.title("Language Distribution ")
plt.xlabel("Percentage of Conversations")
plt.ylabel("Language")
plt.xlim(0, branch_lang_df_plot["Percentage"].max() + 5)
plt.tight_layout()
#plt.savefig(r"C:\Users\20243895\OneDrive - TU Eindhoven\Desktop\DBL\New folder\Language_distr.png", dpi=300, bbox_inches="tight", transparent=True)
plt.show()


