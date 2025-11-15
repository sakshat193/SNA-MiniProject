import { P } from './config.js';
import { applyParams, updateNodePositions } from './scene.js';

export function setupUIEventListeners() {
    document.getElementById('iSize').addEventListener('input', e => {
        P.size = parseFloat(e.target.value);
        updateUI();
        updateNodePositions();
    });
    document.getElementById('iBloom').addEventListener('input', e => {
        P.bloom = parseFloat(e.target.value);
        updateUI();
        applyParams();
    });
    document.getElementById('iSpread').addEventListener('input', e => {
        P.spread = parseFloat(e.target.value);
        updateUI();
        updateNodePositions();
    });
    document.getElementById('iConn').addEventListener('input', e => {
        P.conn = parseFloat(e.target.value);
        updateUI();
        updateNodePositions();
    });
    document.getElementById('iConnOp').addEventListener('input', e => {
        P.connOp = parseFloat(e.target.value);
        updateUI();
        applyParams();
    });
    document.getElementById('iEdge').addEventListener('input', e => {
        P.edgeOp = parseFloat(e.target.value);
        updateUI();
        applyParams();
    });
    document.getElementById('iStar').addEventListener('input', e => {
        P.starOp = parseFloat(e.target.value);
        updateUI();
        applyParams();
    });
    document.getElementById('cEdge').addEventListener('change', e => {
        P.showEdge = e.target.checked;
        applyParams();
    });
    document.getElementById('cConn').addEventListener('change', e => {
        P.showConn = e.target.checked;
        applyParams();
    });
    document.getElementById('cRot').addEventListener('change', e => {
        P.autoRot = e.target.checked;
        applyParams();
    });
    document.getElementById('cLabel').addEventListener('change', e => {
        P.showLabel = e.target.checked;
        applyParams();
    });
}

export function updateUI() {
    document.getElementById('vSize').textContent = P.size.toFixed(2);
    document.getElementById('vBloom').textContent = P.bloom.toFixed(1);
    document.getElementById('vSpread').textContent = P.spread.toFixed(2);
    document.getElementById('vConn').textContent = P.conn.toFixed(1);
    document.getElementById('vConnOp').textContent = P.connOp.toFixed(2);
    document.getElementById('vEdge').textContent = P.edgeOp.toFixed(2);
    document.getElementById('vStar').textContent = P.starOp.toFixed(2);
}
