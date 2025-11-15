// ============================================================
// CONFIGURATION SYSTEM - SINGLE SOURCE OF TRUTH
// ============================================================
// ALL configuration values are defined in config.py
// config.py exports THREEJS_PARAMS to network_data.json
// This module loads those values at runtime
// DO NOT hardcode values here - modify config.py instead
// ============================================================

// Runtime parameters object (populated from network_data.json)
export const P = {
    size: 1.0,              // Fallback only - real value from config.py
    bloom: 2.0,
    spread: 1.0,
    conn: 1.0,
    connOp: 0.6,
    edgeOp: 0.12,
    starOp: 0.7,
    showEdge: true,
    showConn: true,
    autoRot: true,
    showLabel: true,
    locNodeSize: 0.12,
    commSizeMin: 0.4,
    commSizeRange: 0.8
};

export const COLORS = [
    0x1f77b4, 0xff7f0e, 0x2ca02c, 0xd62728, 0x9467bd, 0x8c564b,
    0xe377c2, 0x7f7f7f, 0xbcbd22, 0x17becf, 0xaec7e8, 0xffbb78
];

// Load parameters from network_data.json (exported from config.py)
export function loadConfigFromData(threejsParams) {
    if (!threejsParams) return;
    
    P.size = threejsParams.node_size ?? P.size;
    P.bloom = threejsParams.bloom_strength ?? P.bloom;
    P.spread = threejsParams.node_spread ?? P.spread;
    P.conn = threejsParams.connection_width ?? P.conn;
    P.connOp = threejsParams.connection_opacity ?? P.connOp;
    P.edgeOp = threejsParams.edge_opacity ?? P.edgeOp;
    P.starOp = threejsParams.stars_opacity ?? P.starOp;
    P.showEdge = threejsParams.show_edges ?? P.showEdge;
    P.showConn = threejsParams.show_connections ?? P.showConn;
    P.autoRot = threejsParams.auto_rotate ?? P.autoRot;
    P.showLabel = threejsParams.show_labels ?? P.showLabel;
    P.locNodeSize = threejsParams.location_node_size ?? P.locNodeSize;
    P.commSizeMin = threejsParams.community_size_min ?? P.commSizeMin;
    P.commSizeRange = threejsParams.community_size_range ?? P.commSizeRange;
}
