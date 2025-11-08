# Twitter Network Visualization

Professional network analysis with community detection and interactive 3D rendering.

## Project Structure

```
MiniProject/
├── data/                           # Dataset and network data
│   ├── In-Depth Twitter Retweet Analysis Dataset.csv
│   └── network_data.json
│
├── plotly/                         # Python/Plotly implementation
│   ├── network_visualization.py
│   └── network_visualization.html
│
├── threejs/                        # JavaScript/Three.js implementation
│   ├── network_visualization.html
│   ├── export_data.py
│   └── launch.py
│
├── docs/                          # Documentation
│   ├── README.md
│   └── VISUALIZATION_GUIDE.md
│
├── miniProject.ipynb             # Analysis notebook
└── requirements.txt              # Dependencies
```

## Quick Start

### Prerequisites
```powershell
pip install -r requirements.txt
```

### Plotly Version
```powershell
cd plotly
python network_visualization.py
```

### Three.js Version (Recommended)
```powershell
cd threejs
python launch.py
```

## Features

### Both Versions
- Community representatives positioned at cluster centroids
- All nodes colored by community membership
- Representatives scaled by member count
- Professional tooltips with detailed information
- Edge hover showing connection strength
- Proper opacity scaling

### Three.js Specific
- WebGL-accelerated rendering
- Bloom post-processing effects
- 3D cylinder beams for inter-community connections
- Radial gradient textures on nodes
- Background starfield
- Smooth camera controls with auto-rotate

### Plotly Specific
- Single HTML file output
- No server required
- Dark theme presentation
- Easy sharing and embedding

## Network Statistics

- **Locations**: 822 unique nodes
- **Communities**: 12 detected groups
- **Edges**: 8,392 total (top 2,000 displayed)
- **Algorithm**: Louvain community detection
- **Similarity**: Cosine similarity on behavioral features

## Controls

### Plotly
- **Rotate**: Click + Drag
- **Zoom**: Scroll
- **Pan**: Right Click + Drag
- **Hover**: View node/edge details

### Three.js
- **Rotate**: Left Click + Drag
- **Pan**: Right Click + Drag
- **Zoom**: Scroll
- **Auto-Rotate**: Press Space
- **Hover**: View details

## Data Features

The visualization uses these behavioral features for similarity calculation:
1. Reach (sum, mean, std)
2. Retweet count (sum, mean)
3. Likes (sum, mean)
4. Posting hour patterns (mean)

## Node Types

### Representative Nodes
- Positioned at community centroids
- Size scaled by member count
- Higher bloom intensity
- Detailed community statistics in tooltips

### Individual Nodes
- Colored by community membership
- White center with community color gradient
- Lower bloom intensity
- Basic location statistics

### Edges
- Location-to-location: Thin gray connections
- Community-to-community: Thick cylinder beams with bloom
- Hover shows connection strength

## Customization

### Change Community Colors
Edit `COMMUNITY_COLORS` array in visualization files

### Adjust Node Sizes
**Plotly**: Modify size calculations in `network_visualization.py`
**Three.js**: Adjust sphere radius and scaling factors

### Modify Bloom Effect
**Three.js**: Update `UnrealBloomPass` parameters and `emissiveIntensity` values

## Performance

**Plotly**: 822 nodes + 2000 edges, 30-40 fps
**Three.js**: 427 nodes + 2000 edges + 3000 stars, 60 fps

## Recommendations

- **Presentations**: Three.js (superior visuals)
- **Analysis**: Plotly (easier modification)
- **Sharing**: Plotly (single HTML file)
- **Performance**: Three.js (WebGL acceleration)

## Troubleshooting

**"Port 8000 in use"**: Close previous server instances or change port in `launch.py`

**"Three.js blank page"**: Ensure `network_data.json` exists, run `export_data.py`

**"Plotly not opening"**: Check generated HTML file in plotly folder

## License

Educational project for Social Network Analysis coursework.

### Both Versions

- ✅ Community representatives positioned at cluster centroids (normalized coordinates)- 🌌 Dark universe background with 500+ twinkling stars

- ✅ All nodes colored by community- ⭐ Star systems (communities) with size scaled proportionally to member count

- ✅ Representatives larger than regular nodes- 🪐 Individual location nodes (planets) rendered as small glowing points

- ✅ Clean, professional tooltips (no "universe" theme)- ⚡ Energy beam connections showing inter-community relationships

- ✅ Edge hover showing connection strength- 🎨 Unique color palette for each star system type

- ✅ Proper opacity: representatives (0.95), regular nodes (0.5-0.6)- 📊 Interactive hover info for both stars and planets

- 🔄 Fully rotatable, zoomable 3D view

### Three.js Specific

- ✅ WebGL-accelerated rendering### Optimizations

- ✅ Moderate bloom effect (not overwhelming)

- ✅ 3000 background stars- **Fixed positioning**: Stars now appear at cluster centroids (normalized coordinates)

- ✅ Representative node sizes: 0.4-1.2 units (properly scaled)- Reduced node sizes for better visibility (stars: 8-20 range, planets: 1-3 range)

- ✅ Regular node size: 0.12 units- Top 2000 strongest location connections shown (from 8392 total)

- ✅ Community-based coloring with matching colors- Dual-layer 3D layout for optimal separation

- Reduced glow layers from 3 to 2 for improved performance

### Plotly Specific

- ✅ Single HTML file output## Setup (Windows PowerShell)

- ✅ No server required

- ✅ Easy to share### For Python Version



## 📊 Network Statistics1. Create/activate a virtual environment (optional but recommended)



- **Locations**: 822 unique nodes```powershell

- **Communities**: 12 detected groupspython -m venv .venv

- **Edges**: 8,392 total (showing top 2,000 strongest).\.venv\Scripts\Activate.ps1

- **Algorithm**: Louvain community detection```

- **Similarity**: Cosine similarity on 8 features

2. Install dependencies

## 🎮 Controls

```powershell

### Plotlypip install -r requirements.txt

- **Rotate**: Click + Drag```

- **Zoom**: Scroll

- **Pan**: Right Click + Drag### For Three.js Version

- **Hover**: View details

No installation needed! Just needs Python's built-in HTTP server.

### Three.js

- **Rotate**: Left Click + Drag## Run

- **Pan**: Right Click + Drag

- **Zoom**: Scroll### Three.js Version (Recommended)

- **Auto-Rotate**: Press Space```powershell

- **Hover**: View detailspython launch_threejs.py

```

## 📈 Visualizations

### Python/Plotly Version

### Representatives (Community Nodes)```powershell

- Positioned at the centroid of their member nodespython universe_visualization.py

- Size scaled by number of members```

- Higher opacity (0.95) and moderate bloom

- Same color as their community membersThis will:

- Load the dataset `In-Depth Twitter Retweet Analysis Dataset.csv`

### Individual Nodes (Locations)- Build the similarity network and detect communities

- Colored by community (matching representative)- Open an interactive 3D universe in your default browser

- Smaller size (based on reach)- Save a copy as `twitter_universe.html` in the same folder (open manually if auto-open is blocked)

- Lower opacity (0.5-0.6)

- Less bloom effect## Notes

- If no browser window opens, double-click the generated `twitter_universe.html` file to view the universe.

### Edges- You can adjust the default renderer in the script by changing `pio.renderers.default` to `"vscode"` if preferred inside VS Code.

- Location-to-location: Faint gray lines
- Community-to-community: Brighter colored lines
- Hover shows connection strength

## 🔧 Customization

### Change Community Colors
Edit `COMMUNITY_COLORS` array in:
- `plotly/network_visualization.py` (line 15)
- `threejs/network_visualization.html` (line 147)

### Adjust Node Sizes
**Plotly** (`network_visualization.py`):
- Representatives: Line 260 (size_range = (4, 10))
- Regular nodes: Line 221 (size = 1.5 + 2.0 * ...)

**Three.js** (`network_visualization.html`):
- Representatives: Line 242 (minSize = 0.4, maxSize = 1.2)
- Regular nodes: Line 219 (radius = 0.12)

### Modify Bloom Effect
**Three.js** (`network_visualization.html`, line 101):
```javascript
const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(width, height),
    1.0,  // strength (0.5-2.0)
    0.3,  // radius
    0.9   // threshold (0-1, higher = less bloom)
);
```

## 📝 Data Format

The visualization uses these features for similarity:
1. Reach (sum, mean, std)
2. Retweet count (sum, mean)
3. Likes (sum, mean)
4. Posting hour (mean)

## 🐛 Troubleshooting

**"Representatives not at cluster centers"**
- Fixed! Uses centroid calculation with normalized coordinates

**"Three.js blank page"**
- Ensure `network_data.json` exists in `/data/`
- Run: `python export_data.py` from `/threejs/`

**"Plotly not opening"**
- Check file: `plotly/network_visualization.html`
- Open manually in browser

**"Port 8000 in use"**
- Edit `launch.py`, change `PORT = 8000` to another port

## 📊 Performance

**Plotly**:
- 822 nodes + 2000 edges
- ~30-40 fps

**Three.js**:
- 427 nodes + 2000 edges + 3000 stars
- 60 fps (WebGL)
- Lower memory usage

## 🎯 Recommendations

- **Presentations**: Use Three.js (better visuals)
- **Analysis**: Use Plotly (easier to modify)
- **Sharing**: Plotly (single HTML file)
- **Performance**: Three.js (WebGL accelerated)

## 📄 License

Educational project for SNA lab coursework.
