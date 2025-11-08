"""
Twitter Network Visualization - Plotly Version
Clean, professional visualization with improved theming
"""

import os
import webbrowser
from pathlib import Path
import pandas as pd
import numpy as np
import networkx as nx
from community import community_louvain
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import plotly.graph_objects as go
import plotly.io as pio

# Community color palette
COMMUNITY_COLORS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b',
    '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#aec7e8', '#ffbb78'
]

def load_and_process_data():
    """Load the dataset and build the network"""
    print("Loading Twitter data...")
    df = pd.read_csv('../data/In-Depth Twitter Retweet Analysis Dataset.csv')
    
    # Clean and prepare data
    sna = df[['locationid', 'lang', 'reach', 'retweetcount', 'likes']].dropna()
    sna['locationid'] = sna['locationid'].astype(str)
    sna['lang'] = sna['lang'].astype(str)
    
    # Pre-compute metrics per location
    loc_metrics = sna.groupby('locationid').agg(
        reach_sum=('reach', 'sum'),
        retweet_sum=('retweetcount', 'sum'),
        likes_sum=('likes', 'sum'),
        tweets=('locationid', 'size')
    )
    
    print("Building similarity network...")
    # Aggregate tweet attributes per location
    loc_agg = sna.groupby('locationid').agg({
        'reach': ['sum', 'mean', 'std'],
        'retweetcount': ['sum', 'mean'],
        'likes': ['sum', 'mean'],
        'lang': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'en'
    }).fillna(0)
    loc_agg.columns = ['_'.join(col).strip() for col in loc_agg.columns.values]
    
    # Add weekday/hour patterns
    weekday_hour = df[['locationid', 'weekday', 'hour']].copy()
    weekday_hour['locationid'] = weekday_hour['locationid'].astype(str)
    wh_agg = weekday_hour.groupby('locationid').agg({
        'weekday': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Monday',
        'hour': 'mean'
    })
    loc_agg = loc_agg.join(wh_agg, how='left').fillna({'weekday': 'Monday', 'hour': 12})
    
    # Normalize features for similarity
    feature_cols = ['reach_sum', 'reach_mean', 'reach_std', 'retweetcount_sum', 
                    'retweetcount_mean', 'likes_sum', 'likes_mean', 'hour']
    X = loc_agg[feature_cols].values
    X_scaled = StandardScaler().fit_transform(X)
    
    # Compute cosine similarity
    sim_matrix = cosine_similarity(X_scaled)
    n_locs = len(loc_agg)
    
    # Create sparse graph
    K = min(15, n_locs - 1)
    G_loc = nx.Graph()
    
    # Add nodes
    for idx, loc_id in enumerate(loc_agg.index):
        G_loc.add_node(f'loc_{loc_id}', 
                       locationid=loc_id,
                       reach_sum=float(loc_metrics.at[loc_id, 'reach_sum']) if loc_id in loc_metrics.index else 0.0,
                       retweet_sum=float(loc_metrics.at[loc_id, 'retweet_sum']) if loc_id in loc_metrics.index else 0.0,
                       likes_sum=float(loc_metrics.at[loc_id, 'likes_sum']) if loc_id in loc_metrics.index else 0.0,
                       tweets=int(loc_metrics.at[loc_id, 'tweets']) if loc_id in loc_metrics.index else 0,
                       dominant_lang=loc_agg.at[loc_id, 'lang_<lambda>'])
    
    # Add edges
    locs_list = list(loc_agg.index)
    for i, loc_id in enumerate(locs_list):
        similarities = sim_matrix[i, :]
        top_k_idx = np.argsort(similarities)[::-1][1:K+1]
        for j in top_k_idx:
            neighbor_id = locs_list[j]
            weight = float(similarities[j])
            if weight > 0.3:
                G_loc.add_edge(f'loc_{loc_id}', f'loc_{neighbor_id}', weight=weight)
    
    print(f"Network built: {G_loc.number_of_nodes()} locations, {G_loc.number_of_edges()} edges")
    
    # Community detection
    print("Detecting communities...")
    partition = community_louvain.best_partition(G_loc, weight='weight', resolution=0.8, random_state=42)
    nx.set_node_attributes(G_loc, partition, 'community')
    
    num_communities = len(set(partition.values()))
    print(f"Detected {num_communities} communities")
    
    return G_loc, partition

def create_visualization(G_loc, partition):
    """Create the interactive 3D visualization"""
    print("Rendering visualization...")
    
    # Build community dataframe
    comm_df = pd.DataFrame({
        'node': list(G_loc.nodes()),
        'locationid': [n.replace('loc_', '') for n in G_loc.nodes()],
        'community': [G_loc.nodes[n].get('community', -1) for n in G_loc.nodes()],
        'reach_sum': [G_loc.nodes[n].get('reach_sum', 0.0) for n in G_loc.nodes()],
        'retweet_sum': [G_loc.nodes[n].get('retweet_sum', 0.0) for n in G_loc.nodes()],
        'likes_sum': [G_loc.nodes[n].get('likes_sum', 0.0) for n in G_loc.nodes()],
        'tweets': [G_loc.nodes[n].get('tweets', 0) for n in G_loc.nodes()],
    })
    
    community_stats = comm_df.groupby('community').agg({
        'reach_sum': 'sum',
        'retweet_sum': 'sum',
        'likes_sum': 'sum',
        'tweets': 'sum',
        'locationid': 'count',
    }).rename(columns={'locationid': 'num_locations'})
    
    # Get min/max for scaling
    min_locs = community_stats['num_locations'].min()
    max_locs = community_stats['num_locations'].max()
    
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
    
    # Create community graph
    G_comm = nx.Graph()
    for comm_id, stats in community_stats.iterrows():
        G_comm.add_node(comm_id,
                        reach_sum=float(stats['reach_sum']),
                        retweet_sum=float(stats['retweet_sum']),
                        likes_sum=float(stats['likes_sum']),
                        tweets=int(stats['tweets']),
                        num_locations=int(stats['num_locations']))
    
    for (c1, c2), edge_data in inter_comm_edges.items():
        G_comm.add_edge(c1, c2, weight=edge_data['weight'], count=edge_data['count'])
    
    print(f"Community network: {G_comm.number_of_nodes()} communities, {G_comm.number_of_edges()} inter-community edges")
    
    # Compute 3D layouts with proper normalization
    print("Computing 3D spatial coordinates...")
    
    # Full location layout (individual nodes) - PRIMARY layout
    pos_loc_3d = nx.spring_layout(G_loc, dim=3, k=0.4, iterations=50, seed=42)
    
    # Normalize location positions to [-1, 1] range
    all_coords = np.array(list(pos_loc_3d.values()))
    loc_min, loc_max = all_coords.min(axis=0), all_coords.max(axis=0)
    loc_range = loc_max - loc_min
    loc_range[loc_range == 0] = 1
    
    for node, coords in list(pos_loc_3d.items()):
        normalized = 2 * (coords - loc_min) / loc_range - 1
        pos_loc_3d[node] = normalized * 10.0  # Scale to [-10, 10]
    
    # Position community nodes at the CENTER of their member locations
    pos_comm_3d = {}
    for comm_id in G_comm.nodes():
        member_nodes = [n for n in G_loc.nodes() if G_loc.nodes[n].get('community') == comm_id]
        if member_nodes:
            member_positions = np.array([pos_loc_3d[n] for n in member_nodes])
            centroid = member_positions.mean(axis=0)
            pos_comm_3d[comm_id] = centroid
        else:
            pos_comm_3d[comm_id] = np.array([0.0, 0.0, 0.0])
    
    print(f"Positioned {len(pos_comm_3d)} community representatives at cluster centroids")
    
    # Select strongest edges for visualization
    edges_with_weights = [(u, v, d['weight']) for u, v, d in G_loc.edges(data=True)]
    edges_with_weights.sort(key=lambda x: x[2], reverse=True)
    top_edges = edges_with_weights[:2000]
    
    # Create visualization traces
    print("Rendering individual locations...")
    location_traces = []
    
    # Add faint connections between locations WITH HOVER INFO
    for u, v, w in top_edges:
        x0, y0, z0 = pos_loc_3d[u]
        x1, y1, z1 = pos_loc_3d[v]
        
        location_traces.append(go.Scatter3d(
            x=[x0, x1, None],
            y=[y0, y1, None],
            z=[z0, z1, None],
            mode='lines',
            line=dict(color='rgba(180, 200, 255, 0.12)', width=0.5),
            hoverinfo='text',
            hovertext=f'Connection Strength: {w:.3f}',
            showlegend=False
        ))
    
    # Add location nodes (individual members) - COLORED BY COMMUNITY
    loc_x, loc_y, loc_z = [], [], []
    loc_size, loc_color, loc_text = [], [], []
    
    max_reach = max([G_loc.nodes[n].get('reach_sum', 1) for n in G_loc.nodes()])
    
    for n in G_loc.nodes():
        x, y, z = pos_loc_3d[n]
        loc_x.append(x)
        loc_y.append(y)
        loc_z.append(z)
        
        node_data = G_loc.nodes[n]
        reach = node_data.get('reach_sum', 0)
        community = node_data.get('community', -1)
        loc_id = node_data.get('locationid', 'unknown')
        
        # Smaller sizes for individual nodes
        size = 1.5 + 2.0 * (np.log1p(reach) / np.log1p(max_reach))
        loc_size.append(size)
        
        # Use community color
        loc_color.append(COMMUNITY_COLORS[community % len(COMMUNITY_COLORS)])
        
        loc_text.append(
            f"<b>Location {loc_id}</b><br>"
            f"Community: {community}<br>"
            f"Reach: {int(reach):,}<br>"
            f"Retweets: {int(node_data.get('retweet_sum', 0)):,}<br>"
            f"Likes: {int(node_data.get('likes_sum', 0)):,}<br>"
            f"Tweets: {node_data.get('tweets', 0)}"
        )
    
    location_traces.append(go.Scatter3d(
        x=loc_x, y=loc_y, z=loc_z,
        mode='markers',
        marker=dict(
            size=loc_size,
            color=loc_color,
            line=dict(color='white', width=0.3),
            opacity=0.5  # Lower opacity for non-representatives
        ),
        hovertext=loc_text,
        hoverinfo='text',
        name='Locations',
        showlegend=False
    ))
    
    # Create community representatives (larger nodes at centroids)
    print("Rendering community representatives...")
    
    # Create inter-community connection lines WITH HOVER INFO
    edge_traces = []
    for u, v in G_comm.edges():
        x0, y0, z0 = pos_comm_3d[u]
        x1, y1, z1 = pos_comm_3d[v]
        edge_count = G_comm[u][v]['count']
        edge_weight = G_comm[u][v]['weight']
        
        edge_traces.append(go.Scatter3d(
            x=[x0, x1, None],
            y=[y0, y1, None],
            z=[z0, z1, None],
            mode='lines',
            line=dict(
                color='rgba(120, 220, 255, 0.6)',
                width=2 + edge_count/25
            ),
            hoverinfo='text',
            hovertext=f'<b>Inter-Community Connection</b><br>Communities: {u} ↔ {v}<br>Connections: {edge_count}<br>Total Weight: {edge_weight:.2f}',
            showlegend=False
        ))
    
    # Create community representative nodes
    star_traces = []
    
    for comm_id in sorted(G_comm.nodes()):
        x, y, z = pos_comm_3d[comm_id]
        node_data = G_comm.nodes[comm_id]
        
        reach = node_data['reach_sum']
        num_locs = node_data['num_locations']
        tweets = node_data['tweets']
        retweets = node_data['retweet_sum']
        likes = node_data['likes_sum']
        
        # Size SCALED by community size (4-10 range - SMALLER)
        size_range = (4, 10)
        if max_locs > min_locs:
            rep_size = size_range[0] + (size_range[1] - size_range[0]) * ((num_locs - min_locs) / (max_locs - min_locs))
        else:
            rep_size = (size_range[0] + size_range[1]) / 2
        
        # Use community color
        comm_color = COMMUNITY_COLORS[comm_id % len(COMMUNITY_COLORS)]
        
        # Single representative marker (no glow layers)
        star_traces.append(go.Scatter3d(
            x=[x], y=[y], z=[z],
            mode='markers+text',
            marker=dict(
                size=rep_size,
                color=comm_color,
                line=dict(color='white', width=2),
                opacity=0.95  # Higher opacity for representatives
            ),
            text=f'C{comm_id}',
            textposition='top center',
            textfont=dict(size=10, color='white', family='Arial'),
            hoverinfo='text',
            hovertext=f"<b>Community {comm_id} (Representative)</b><br>"
                     f"━━━━━━━━━━━━━━━<br>"
                     f"Members: {num_locs} locations<br>"
                     f"Total Reach: {int(reach):,}<br>"
                     f"Total Retweets: {int(retweets):,}<br>"
                     f"Total Likes: {int(likes):,}<br>"
                     f"Total Tweets: {tweets}",
            showlegend=False,
            name=f'Community {comm_id}'
        ))
    
    # Combine all traces
    all_traces = location_traces + edge_traces + star_traces
    
    # Create figure
    fig = go.Figure(data=all_traces)
    
    # Update layout (dark presentation)
    fig.update_layout(
        title=dict(
            text='Twitter Network Visualization<br><sub>Community representatives at cluster centers | Size = member count | Color = community</sub>',
            x=0.5,
            font=dict(size=20, color='#e6e6e6', family='Segoe UI')
        ),
        paper_bgcolor='#0a0a15',
        plot_bgcolor='#0a0a15',
        showlegend=False,
        scene=dict(
            xaxis=dict(
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                title='',
                showbackground=False,
                color='#cfd3dc'
            ),
            yaxis=dict(
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                title='',
                showbackground=False,
                color='#cfd3dc'
            ),
            zaxis=dict(
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                title='',
                showbackground=False,
                color='#cfd3dc'
            ),
            bgcolor='#0a0a15'
        ),
        margin=dict(l=0, r=0, b=0, t=60),
        height=900,
        hovermode='closest',
        hoverlabel=dict(bgcolor='#0e1220', bordercolor='#2a2f45', font_color='#e6e6e6')
    )
    
    return fig

def main():
    """Main execution function"""
    print("=" * 60)
    print("TWITTER NETWORK VISUALIZATION (Plotly)")
    print("=" * 60)
    print()
    
    # Set renderer
    try:
        pio.renderers.default = "browser"
    except Exception as e:
        print(f"Renderer configuration warning: {e}")
    
    # Load data and build network
    G_loc, partition = load_and_process_data()
    
    # Create visualization
    fig = create_visualization(G_loc, partition)
    
    # Show the visualization
    print()
    print("Launching visualization...")
    print()
    
    # Try both live render and HTML export
    opened = False
    try:
        fig.show()
        opened = True
    except Exception as e:
        print(f"fig.show() failed ({e}); falling back to HTML export...")
    
    # Always write HTML file
    out_path = Path(__file__).with_name("network_visualization.html")
    try:
        fig.write_html(str(out_path), include_plotlyjs="cdn", full_html=True, auto_open=not opened)
        if not opened:
            try:
                webbrowser.open(out_path.as_uri())
                opened = True
            except Exception:
                pass
        print(f"Saved: {out_path}")
        if not opened:
            print("Could not auto-open. Please open manually:")
            print(f"   {out_path}")
    except Exception as e:
        print(f"Failed to write HTML ({e}).")
    
    print()
    print("Visualization complete!")
    print(f"  - {len(set(partition.values()))} communities (representatives)")
    print(f"  - {G_loc.number_of_nodes()} individual locations")
    print(f"  - Representatives positioned at cluster centroids")
    print(f"  - All nodes colored by community")
    print()

if __name__ == "__main__":
    main()
