"""
Unified Network Visualization Configuration
Ensures consistency across Jupyter notebook, Plotly, and ThreeJS visualizations
"""

# ============================================================
# LAYOUT PARAMETERS
# ============================================================

# Spring layout configuration for location network (G_loc)
LAYOUT_CONFIG = {
    'dim': 3,              # 3D visualization
    'k': 0.35,             # Optimal node separation (compromise between 0.3 and 0.4)
    'iterations': 50,      # Convergence iterations for 822 nodes
    'seed': 42             # Reproducible layouts
}

# Community graph layout (for separate community-only visualization)
COMMUNITY_LAYOUT_CONFIG = {
    'dim': 3,
    'k': 2.0,              # More spread for aggregated communities
    'iterations': 100,     # More iterations for better community positioning
    'seed': 42
}

# ============================================================
# COORDINATE NORMALIZATION
# ============================================================

COORD_RANGE = (-10.0, 10.0)  # Normalized coordinate bounds for WebGL compatibility

# ============================================================
# EDGE FILTERING
# ============================================================

MAX_EDGES_DISPLAY = -1      # Maximum edges to display (balance detail vs performance)
EDGE_WEIGHT_THRESHOLD = 0.3   # Minimum similarity to create edge
K_NEIGHBORS = 15              # Number of nearest neighbors per node

# ============================================================
# VISUAL STYLING
# ============================================================

# Community color palette (consistent across all visualizations)
COMMUNITY_COLORS = [
    '#1f77b4',  # Blue
    '#ff7f0e',  # Orange
    '#2ca02c',  # Green
    '#d62728',  # Red
    '#9467bd',  # Purple
    '#8c564b',  # Brown
    '#e377c2',  # Pink
    '#7f7f7f',  # Gray
    '#bcbd22',  # Olive
    '#17becf',  # Cyan
    '#aec7e8',  # Light blue
    '#ffbb78'   # Light orange
]

# Node size ranges
LOCATION_NODE_SIZE_RANGE = (1.5, 4.0)      # Size range for individual locations
COMMUNITY_REP_SIZE_RANGE = (4.0, 10.0)     # Size range for community representatives

# Opacity values
LOCATION_NODE_OPACITY = 0.5      # Lower opacity for individual locations
COMMUNITY_NODE_OPACITY = 0.95    # Higher opacity for community representatives
EDGE_OPACITY = 0.12              # Faint connections between locations
INTER_COMM_EDGE_OPACITY = 0.6    # Stronger inter-community connections

# ============================================================
# THREE.JS VISUALIZATION PARAMETERS
# ============================================================

THREEJS_PARAMS = {
    'node_size': 1.0,            # Base node size multiplier
    'bloom_strength': 2.0,       # Bloom post-processing strength
    'node_spread': 1.0,          # Spatial spread multiplier
    'connection_width': 1.0,     # Community connection width multiplier
    'connection_opacity': 0.6,   # Community connection opacity
    'edge_opacity': 0.12,        # Faint edge opacity
    'stars_opacity': 0.7,        # Background stars opacity
    'auto_rotate': True,         # Auto-rotation enabled
    'show_edges': True,          # Show faint edges
    'show_connections': True,    # Show community connections
    'show_labels': True,         # Show community labels
    'location_node_size': 0.12,  # Base size for location nodes
    'community_size_min': 0.4,   # Minimum community node size
    'community_size_range': 0.8  # Range for community node scaling
}

# ============================================================
# NETWORK CONSTRUCTION
# ============================================================

# Data quality thresholds
MIN_TWEETS = 3  # Minimum tweets per location for reliable aggregation

# Features used for similarity computation (excluding language - will be encoded separately)
SIMILARITY_FEATURES = [
    'reach_sum', 'reach_mean', 'reach_std',
    'retweetcount_sum', 'retweetcount_mean',
    'likes_sum', 'likes_mean',
    'hour'
]

# Community detection parameters
COMMUNITY_DETECTION_CONFIG = {
    'weight': 'weight',
    'resolution': 0.8,
    'random_state': 42
}

# ============================================================
# DATA PATHS
# ============================================================

DATA_DIR = 'data'
DATASET_FILE = 'In-Depth Twitter Retweet Analysis Dataset.csv'
NETWORK_JSON = 'network_data.json'

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_coordinates(positions_dict, coord_range=COORD_RANGE):
    """
    Normalize 3D coordinates to specified range
    
    Args:
        positions_dict: Dictionary of {node: [x, y, z]}
        coord_range: Tuple of (min, max) for normalization
        
    Returns:
        Dictionary with normalized positions
    """
    import numpy as np
    
    all_coords = np.array(list(positions_dict.values()))
    coord_min, coord_max = all_coords.min(axis=0), all_coords.max(axis=0)
    coord_range_vals = coord_max - coord_min
    coord_range_vals[coord_range_vals == 0] = 1  # Avoid division by zero
    
    normalized = {}
    range_min, range_max = coord_range
    scale = range_max - range_min
    
    for node, coords in positions_dict.items():
        # Normalize to [0, 1]
        norm_coords = (coords - coord_min) / coord_range_vals
        # Scale to [range_min, range_max]
        scaled_coords = norm_coords * scale + range_min
        normalized[node] = scaled_coords
    
    return normalized

def get_community_color(community_id, colors=COMMUNITY_COLORS):
    """Get consistent color for a community"""
    return colors[community_id % len(colors)]

def filter_top_edges(graph, max_edges=MAX_EDGES_DISPLAY):
    """
    Filter graph to keep only the strongest edges
    
    Args:
        graph: NetworkX graph with 'weight' attribute
        max_edges: Maximum number of edges to keep
        
    Returns:
        List of (source, target, weight) tuples
    """
    edges = [(u, v, d['weight']) for u, v, d in graph.edges(data=True)]
    edges.sort(key=lambda x: x[2], reverse=True)
    return edges[:max_edges]
