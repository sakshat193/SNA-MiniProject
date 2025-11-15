# Twitter Network Analysis and Visualization

A comprehensive social network analysis project that constructs, analyzes, and visualizes Twitter location networks based on engagement patterns. The project employs community detection algorithms and provides interactive 3D visualizations using Three.js with WebGL rendering.

## Overview

This project analyzes Twitter retweet data to identify engagement patterns across geographic locations. Using behavioral similarity metrics and community detection algorithms, it constructs and visualizes network structures that reveal natural groupings in the data.

## Project Structure

```
SNAMiniProject/
├── data/
│   ├── In-Depth Twitter Retweet Analysis Dataset.csv
│   └── network_data.json              # Generated network data with parameters
├── threejs/
│   ├── js/
│   │   ├── main.js                     # Entry point, data loading, coordination
│   │   ├── config.js                   # Runtime configuration loader
│   │   ├── scene.js                    # Three.js scene, rendering, visualization
│   │   ├── ui.js                       # UI event handlers, parameter updates
│   │   └── materials.js                # Shader materials, texture generation
│   ├── index.html                      # Visualization interface
│   └── launch.py                       # Local development server
├── config.py                           # ⭐ CENTRAL configuration authority
├── miniProject.ipynb                   # Network analysis and data generation
├── requirements.txt                    # Python dependencies
├── CONFIGURATION.md                    # Configuration system documentation
└── README.md
```

## Key Features

### Network Construction
- k-Nearest Neighbors (k-NN) graph based on cosine similarity
- Aggregated behavioral features: reach, retweets, likes, temporal patterns
- One-hot encoding for language diversity
- Configurable edge weight thresholds and minimum tweet filters

### Community Detection
- Louvain algorithm for modularity optimization
- Resolution parameter tuning for granularity control
- Community-level statistics and inter-community connections

### Interactive 3D Visualization
- WebGL-accelerated Three.js rendering with modular ES6 architecture
- Real-time parameter adjustment (node size, spread, bloom, connection width/opacity)
- Dynamic node positioning with smooth updates using original coordinate caching
- Community representatives positioned at cluster centroids with glow effects
- Inter-community connection beams with gradient shaders and adjustable thickness
- Hover tooltips with detailed statistics (reach, retweets, likes)
- Background starfield with configurable opacity for spatial depth
- Sidebar control panel with live parameter display and reset functionality

### Centralized Configuration System
- **Single source of truth**: `config.py` defines ALL parameters
- Parameters exported to `network_data.json` via `THREEJS_PARAMS` dictionary
- JavaScript modules (`js/config.js`) load configuration dynamically from JSON
- Zero duplicate constants across Python/JavaScript codebases
- Original position caching prevents coordinate drift during parameter updates
- Reproducible layouts with fixed random seeds
- See `CONFIGURATION.md` for detailed architecture documentation

## Technical Implementation

### Network Metrics
- Nodes: 822 unique locations (filtered by minimum tweet threshold)
- Edges: k-NN connections (k=15) with similarity weights
- Communities: 12 detected groups
- Modularity: ~0.81 (strong community structure)

### Feature Engineering
- Behavioral aggregation: sum, mean, standard deviation
- Temporal features: weekday mode, hourly patterns
- Language encoding: one-hot vectors for categorical data
- Standardized scaling for cosine similarity computation

### Visualization Technology
- Three.js r160 with modular ES6 architecture (separated concerns: scene, UI, materials)
- Custom shader materials with gradient interpolation and opacity uniforms for connection edges
- Post-processing: Unreal Bloom Pass with adaptive emissive intensity based on color luminance
- Orbit controls with smooth damping and auto-rotation toggle
- Real-time parameter updates without scene rebuild using original position storage
- Efficient geometry updates: only modified elements are rebuilt (e.g., connection beams)

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- Modern web browser with WebGL support

### Install Dependencies
```powershell
pip install -r requirements.txt
```

## Usage

### 1. Run the Jupyter Notebook
Open and execute `miniProject.ipynb` to:
- Load and preprocess the Twitter dataset
- Construct the similarity network
- Detect communities using the Louvain algorithm
- Generate 2D and 3D visualizations
- Export network data to JSON format

The notebook includes detailed markdown documentation explaining each step of the analysis pipeline.

### 2. Launch the Interactive Visualization
```powershell
python threejs/launch.py
```

This starts a local HTTP server at `http://localhost:8000` and opens the visualization in your default browser.

## Visualization Controls

### Camera Navigation
- Left Click + Drag: Rotate view
- Right Click + Drag: Pan camera
- Scroll: Zoom in/out
- Space Bar: Toggle auto-rotation

### Interactive Parameters (Side Panel)
- **Node Size**: Adjust all node scales (0.5-2.5)
- **Bloom Strength**: Control glow intensity (0.5-5.0)
- **Node Spread**: Modify spatial distribution (0.1-5.0) - scales from original positions
- **Connection Width**: Scale inter-community beam thickness (0.1-3.0)
- **Connection Opacity**: Adjust beam transparency (0.0-1.0) via shader uniforms
- **Faint Edge Opacity**: Control location-to-location edge visibility (0.0-0.5)
- **Stars Opacity**: Background starfield brightness (0.0-1.0)
- **Display Toggles**: Show/hide edges, connections, labels, auto-rotation

All parameters update in real-time without requiring a scene rebuild. Original coordinates are cached to prevent drift during repeated adjustments.

## Configuration Architecture

The project uses a centralized configuration system where `config.py` is the single source of truth:

### Configuration Flow
1. Define all parameters in `config.py` (Python)
2. Notebook exports parameters to `network_data.json`
3. JavaScript modules (`js/config.js`) load from JSON at runtime
4. No hardcoded duplicates - one place to change, everywhere updates

### Layout Parameters
- Spring layout configuration (k-value, iterations, dimensionality)
- Coordinate normalization ranges for WebGL compatibility
- Separate layouts for location and community networks

### Network Construction
- K-neighbors value (default: 15)
- Edge weight threshold (default: 0.3)
- Minimum tweets per location (default: 3)

### Visual Styling
- Community color palette (12 distinct colors)
- Node size ranges for locations and communities
- Opacity values for different element types
- Three.js-specific rendering parameters

### Community Detection
- Louvain algorithm resolution (default: 0.8)
- Weight attribute and random seed for reproducibility

## Data Format

### Input Dataset
The project expects a CSV file with the following columns:
- locationid: Geographic location identifier
- lang: Tweet language code
- reach: User reach/follower count
- retweetcount: Number of retweets
- likes: Number of likes
- weekday: Day of week posted
- hour: Hour of day posted

### Exported Network Data
The notebook exports a JSON file containing:
- Communities: Position, size, reach, and connections
- Locations: Position, community assignment, and reach
- Edges: Source, target, and weight for all connections
- Metadata: Generation timestamp, filter thresholds, node counts
- Three.js Parameters: Synchronized visualization settings

## Methodology

### 1. Data Preprocessing
- Remove rows with missing essential data
- Convert categorical variables to appropriate types
- Filter locations with insufficient tweet counts

### 2. Feature Aggregation
- Group tweets by locationid
- Compute statistical summaries (sum, mean, std)
- Determine dominant language and temporal patterns

### 3. Similarity Computation
- Standardize numerical features
- One-hot encode categorical language variable
- Calculate pairwise cosine similarity matrix

### 4. Graph Construction
- Create k-NN graph structure
- Add edges only if similarity exceeds threshold
- Attach node attributes for visualization

### 5. Community Detection
- Apply Louvain algorithm with configurable resolution
- Calculate modularity to assess community quality
- Assign community labels to all nodes

### 6. Layout Computation
- Generate 3D spring layout using NetworkX
- Normalize coordinates to [-10, 10] range
- Calculate community centroids from member positions

### 7. Export and Visualization
- Serialize network data to JSON format
- Load data in Three.js application
- Render with WebGL and post-processing effects

## Performance Considerations

### Network Sparsity
The k-NN approach creates a sparse graph, significantly improving:
- Community detection speed
- Visualization rendering performance
- Memory consumption

### Edge Filtering
For large networks, only the strongest connections are displayed (configurable via MAX_EDGES_DISPLAY in config.py).

### WebGL Acceleration
Three.js utilizes GPU rendering for smooth 60fps visualization of hundreds of nodes and thousands of edges.

## Recent Updates

### December 2024 - Architecture Refactor
- ✅ Modularized JavaScript codebase into separate files (main, scene, ui, materials, config)
- ✅ Established `config.py` as single source of truth for all parameters
- ✅ Fixed coordinate drift bug by caching original positions in `userData`
- ✅ Implemented shader-based connection opacity via `uOpacity` uniform
- ✅ Added comprehensive configuration documentation (`CONFIGURATION.md`)
- ✅ Styled sidebar panel with animated close button
- ✅ Eliminated 700+ lines of duplicate inline code from HTML

## Troubleshooting

### THREE is not defined / Module Import Errors
Ensure your browser supports ES6 modules and the importmap is loaded. Use a modern browser (Chrome 89+, Firefox 108+, Safari 16.4+).

### Connection Opacity/Spread Not Working
Clear browser cache (Ctrl+Shift+Delete) and hard refresh (Ctrl+F5). Ensure `network_data.json` was regenerated after updating `config.py`.

### Browser Does Not Open
Navigate to `http://localhost:8000/threejs/index.html` manually after starting the server.

### Edges Not Aligned with Nodes
This was caused by coordinate drift from repeated calculations. Now fixed - positions are always calculated from cached originals.

### Port Conflicts
Modify the PORT variable in `threejs/launch.py` (default: 8000).

### Missing Dependencies
Run `pip install -r requirements.txt`.

## Academic Context

Developed for a Social Network Analysis course, demonstrating network construction from behavioral data, community detection algorithms, and interactive 3D visualization techniques.
## License

Educational project for Social Network Analysis coursework.
