import { P, COLORS, loadConfigFromData } from './config.js';
import { updateUI, setupUIEventListeners } from './ui.js';
import { init, animate, buildVis, getRenderer, onMouse } from './scene.js';

console.log('THREE.js loaded, version:', THREE.REVISION);

// Globals
let data;

// UI Functions
window.togglePanel = () => {
    const panel = document.getElementById('panel');
    const btn = document.getElementById('panelToggle');
    if (panel.classList.contains('open')) {
        panel.classList.remove('open');
        btn.textContent = '⚙';
    } else {
        panel.classList.add('open');
        btn.textContent = '✕';
    }
};

window.resetParams = () => {
    Object.assign(P, {
        size: 1.0, bloom: 2.0, spread: 1.0, conn: 1.0,
        connOp: 0.6, edgeOp: 0.12, starOp: 0.7,
        showEdge: true, showConn: true, autoRot: true, showLabel: true,
    });
    
    document.getElementById('iSize').value = P.size;
    document.getElementById('iBloom').value = P.bloom;
    document.getElementById('iSpread').value = P.spread;
    document.getElementById('iConn').value = P.conn;
    document.getElementById('iConnOp').value = P.connOp;
    document.getElementById('iEdge').value = P.edgeOp;
    document.getElementById('iStar').value = P.starOp;
    document.getElementById('cEdge').checked = P.showEdge;
    document.getElementById('cConn').checked = P.showConn;
    document.getElementById('cRot').checked = P.autoRot;
    document.getElementById('cLabel').checked = P.showLabel;
    
    updateUI();
    applyParams();
};

// Load and visualize data
async function loadData() {
    try {
        console.log('Fetching network data...');
        const res = await fetch('/data/network_data.json');
        
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}: ${res.statusText}. Make sure server is running from project root.`);
        }
        
        data = await res.json();
        console.log('Data loaded:', data.communities?.length, 'communities,', data.locations?.length, 'locations');
        
        // Load Three.js parameters from config if available
        if (data.threejs_params) {
            console.log('Loading parameters from config.py via network_data.json...');
            loadConfigFromData(data.threejs_params);
            
            // Update UI controls to reflect loaded config
            document.getElementById('iSize').value = P.size;
            document.getElementById('iBloom').value = P.bloom;
            document.getElementById('iSpread').value = P.spread;
            document.getElementById('iConn').value = P.conn;
            document.getElementById('iConnOp').value = P.connOp;
            document.getElementById('iEdge').value = P.edgeOp;
            document.getElementById('iStar').value = P.starOp;
            document.getElementById('cEdge').checked = P.showEdge;
            document.getElementById('cConn').checked = P.showConn;
            document.getElementById('cRot').checked = P.autoRot;
            document.getElementById('cLabel').checked = P.showLabel;
            updateUI();
        }
        
        updateStats(data.communities.length, data.locations.length, data.edges.length);
        buildVis(data);
        
        document.getElementById('loading').style.display = 'none';
        console.log('Visualization complete!');
        
    } catch (err) {
        console.error('ERROR loading data:', err);
        document.getElementById('loadingText').innerHTML = 
            `<span style="color: #ff6666;">Error: ${err.message}</span><br><br>` +
            `<span style="font-size: 14px;">Check:<br>` +
            `1. Server running from project root<br>` +
            `2. /data/network_data.json exists<br>` +
            `3. Browser console (F12)</span>`;
    }
}

function updateStats(c, l, e) {
    document.getElementById('communityCount').textContent = c;
    document.getElementById('locationCount').textContent = l;
    document.getElementById('edgeCount').textContent = e;
    document.getElementById('pComm').textContent = c;
    document.getElementById('pLoc').textContent = l;
    document.getElementById('pEdge').textContent = e;
}

// Event Listeners
window.addEventListener('resize', () => {
    const { cam, rend, comp } = getRenderer();
    cam.aspect = window.innerWidth / window.innerHeight;
    cam.updateProjectionMatrix();
    rend.setSize(window.innerWidth, window.innerHeight);
    comp.setSize(window.innerWidth, window.innerHeight);
}, false);

document.addEventListener('mousemove', onMouse, false);

// Initialization
init();
animate();
loadData();
setupUIEventListeners();
