"""
Export network data to JSON for Three.js visualization
Updated for new organized structure
"""
import json
import pandas as pd
import numpy as np
import networkx as nx
from community import community_louvain
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

print("=" * 60)
print("EXPORTING NETWORK DATA FOR THREE.JS")
print("=" * 60)
print()

# Load and process data
print("Loading Twitter data...")
df = pd.read_csv('data/In-Depth Twitter Retweet Analysis Dataset.csv')

sna = df[['locationid', 'lang', 'reach', 'retweetcount', 'likes']].dropna()
sna['locationid'] = sna['locationid'].astype(str)
sna['lang'] = sna['lang'].astype(str)

loc_metrics = sna.groupby('locationid').agg(
    reach_sum=('reach', 'sum'),
    retweet_sum=('retweetcount', 'sum'),
    likes_sum=('likes', 'sum'),
    tweets=('locationid', 'size')
)

print("Building network...")
loc_agg = sna.groupby('locationid').agg({
    'reach': ['sum', 'mean', 'std'],
    'retweetcount': ['sum', 'mean'],
    'likes': ['sum', 'mean'],
    'lang': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'en'
}).fillna(0)
loc_agg.columns = ['_'.join(col).strip() for col in loc_agg.columns.values]

weekday_hour = df[['locationid', 'weekday', 'hour']].copy()
weekday_hour['locationid'] = weekday_hour['locationid'].astype(str)
wh_agg = weekday_hour.groupby('locationid').agg({
    'weekday': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Monday',
    'hour': 'mean'
})
loc_agg = loc_agg.join(wh_agg, how='left').fillna({'weekday': 'Monday', 'hour': 12})

feature_cols = ['reach_sum', 'reach_mean', 'reach_std', 'retweetcount_sum', 
                'retweetcount_mean', 'likes_sum', 'likes_mean', 'hour']
X = loc_agg[feature_cols].values
X_scaled = StandardScaler().fit_transform(X)

sim_matrix = cosine_similarity(X_scaled)
n_locs = len(loc_agg)

K = min(15, n_locs - 1)
G_loc = nx.Graph()

for idx, loc_id in enumerate(loc_agg.index):
    G_loc.add_node(f'loc_{loc_id}', 
                   locationid=loc_id,
                   reach_sum=float(loc_metrics.at[loc_id, 'reach_sum']) if loc_id in loc_metrics.index else 0.0,
                   retweet_sum=float(loc_metrics.at[loc_id, 'retweet_sum']) if loc_id in loc_metrics.index else 0.0,
                   likes_sum=float(loc_metrics.at[loc_id, 'likes_sum']) if loc_id in loc_metrics.index else 0.0,
                   tweets=int(loc_metrics.at[loc_id, 'tweets']) if loc_id in loc_metrics.index else 0,
                   dominant_lang=loc_agg.at[loc_id, 'lang_<lambda>'])

locs_list = list(loc_agg.index)
for i, loc_id in enumerate(locs_list):
    similarities = sim_matrix[i, :]
    top_k_idx = np.argsort(similarities)[::-1][1:K+1]
    for j in top_k_idx:
        neighbor_id = locs_list[j]
        weight = float(similarities[j])
        if weight > 0.3:
            G_loc.add_edge(f'loc_{loc_id}', f'loc_{neighbor_id}', weight=weight)

print("Detecting communities...")
partition = community_louvain.best_partition(G_loc, weight='weight', resolution=0.8, random_state=42)
nx.set_node_attributes(G_loc, partition, 'community')

print("Computing 3D layout...")
# Full location layout
pos_loc_3d = nx.spring_layout(G_loc, dim=3, k=0.4, iterations=50, seed=42)

# Normalize to [-10, 10]
all_coords = np.array(list(pos_loc_3d.values()))
loc_min, loc_max = all_coords.min(axis=0), all_coords.max(axis=0)
loc_range = loc_max - loc_min
loc_range[loc_range == 0] = 1

for node, coords in list(pos_loc_3d.items()):
    normalized = 2 * (coords - loc_min) / loc_range - 1
    pos_loc_3d[node] = normalized * 10.0

# Build community data
comm_df = pd.DataFrame({
    'node': list(G_loc.nodes()),
    'locationid': [n.replace('loc_', '') for n in G_loc.nodes()],
    'community': [G_loc.nodes[n].get('community', -1) for n in G_loc.nodes()],
    'reach_sum': [G_loc.nodes[n].get('reach_sum', 0.0) for n in G_loc.nodes()],
    'retweet_sum': [G_loc.nodes[n].get('retweet_sum', 0.0) for n in G_loc.nodes()],
    'likes_sum': [G_loc.nodes[n].get('likes_sum', 0.0) for n in G_loc.nodes()],
})

community_stats = comm_df.groupby('community').agg({
    'reach_sum': 'sum',
    'retweet_sum': 'sum',
    'likes_sum': 'sum',
    'locationid': 'count',
}).rename(columns={'locationid': 'num_locations'})

# Build inter-community edges
inter_comm_edges = {}
for u, v, w in G_loc.edges(data='weight'):
    comm_u = G_loc.nodes[u]['community']
    comm_v = G_loc.nodes[v]['community']
    if comm_u != comm_v:
        edge_key = tuple(sorted([comm_u, comm_v]))
        if edge_key not in inter_comm_edges:
            inter_comm_edges[edge_key] = {'weight': 0, 'count': 0}
        inter_comm_edges[edge_key]['weight'] += w
        inter_comm_edges[edge_key]['count'] += 1

# Position community nodes at centroids
pos_comm_3d = {}
comm_connections = {}
for comm_id in sorted(set(partition.values())):
    member_nodes = [n for n in G_loc.nodes() if G_loc.nodes[n].get('community') == comm_id]
    if member_nodes:
        member_positions = np.array([pos_loc_3d[n] for n in member_nodes])
        centroid = member_positions.mean(axis=0)
        pos_comm_3d[comm_id] = centroid.tolist()
    else:
        pos_comm_3d[comm_id] = [0.0, 0.0, 0.0]
    
    connections = set()
    for (c1, c2) in inter_comm_edges.keys():
        if c1 == comm_id:
            connections.add(c2)
        elif c2 == comm_id:
            connections.add(c1)
    comm_connections[comm_id] = list(connections)

print("Exporting to JSON...")

# Prepare export data
export_data = {
    'communities': [],
    'locations': [],
    'edges': []
}

# Export communities
for comm_id in sorted(set(partition.values())):
    stats = community_stats.loc[comm_id]
    export_data['communities'].append({
        'id': int(comm_id),
        'position': pos_comm_3d[comm_id],
        'size': int(stats['num_locations']),
        'reach': int(stats['reach_sum']),
        'retweets': int(stats['retweet_sum']),
        'likes': int(stats['likes_sum']),
        'connections': comm_connections[comm_id]
    })

# Export locations
edges_with_weights = [(u, v, d['weight']) for u, v, d in G_loc.edges(data=True)]
edges_with_weights.sort(key=lambda x: x[2], reverse=True)
top_edges = edges_with_weights

edge_nodes = set()
for u, v, w in top_edges:
    edge_nodes.add(u)
    edge_nodes.add(v)

for node in edge_nodes:
    node_data = G_loc.nodes[node]
    export_data['locations'].append({
        'id': node_data['locationid'],
        'position': pos_loc_3d[node].tolist(),
        'community': int(node_data.get('community', -1)),
        'reach': int(node_data.get('reach_sum', 0))
    })

# Export edges
for u, v, w in top_edges:
    export_data['edges'].append({
        'source': pos_loc_3d[u].tolist(),
        'target': pos_loc_3d[v].tolist(),
        'weight': float(w)
    })

# Write JSON file
with open('data/network_data.json', 'w') as f:
    json.dump(export_data, f, indent=2)

print()
print("Export complete!")
print(f"Exported {len(export_data['communities'])} communities")
print(f"Exported {len(export_data['locations'])} locations")
print(f"Exported {len(export_data['edges'])} connections")
print()
print("Output: ../data/network_data.json")
print()
print("=" * 60)
