import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { P, COLORS } from './config.js';
import { createGradientEdgeMaterial } from './materials.js';

// Globals
let scene, cam, rend, ctrl, comp, bloom;
let meshNodes = [], meshReps = [], meshEdges = [], meshLabels = [], meshStars;

function init() {
    // Scene setup
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x0a0a15, 0.002);
    
    cam = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
    cam.position.set(35, 35, 35);
    
    rend = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    rend.setSize(window.innerWidth, window.innerHeight);
    rend.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    rend.toneMapping = THREE.ACESFilmicToneMapping;
    rend.toneMappingExposure = 0.7;
    document.body.appendChild(rend.domElement);

    // Orbit controls
    ctrl = new OrbitControls(cam, rend.domElement);
    ctrl.enableDamping = true;
    ctrl.dampingFactor = 0.05;
    ctrl.minDistance = 10;
    ctrl.maxDistance = 150;
    ctrl.autoRotate = P.autoRot;
    ctrl.autoRotateSpeed = 0.4;

    // Post-processing
    comp = new EffectComposer(rend);
    const renderPass = new RenderPass(scene, cam);
    comp.addPass(renderPass);

    bloom = new UnrealBloomPass(
        new THREE.Vector2(window.innerWidth, window.innerHeight),
        P.bloom,
        0.4,
        0.0
    );
    comp.addPass(bloom);

    // Lighting
    const aLight = new THREE.AmbientLight(0x505060, 0.6);
    scene.add(aLight);

    const pLight1 = new THREE.PointLight(0x4488ff, 0.8, 100);
    pLight1.position.set(25, 25, 25);
    scene.add(pLight1);

    const pLight2 = new THREE.PointLight(0x8844ff, 0.8, 100);
    pLight2.position.set(-25, -25, -25);
    scene.add(pLight2);
}

function animate() {
    requestAnimationFrame(animate);
    ctrl.update();
    comp.render();
}

function buildVis(d) {
    console.log('Building starfield...');
    mkStars();
    
    // Faint edges
    console.log('Building edges...');
    const eGeo = new THREE.BufferGeometry();
    const ePos = [];
    d.edges.forEach(e => {
        ePos.push(e.source[0], e.source[1], e.source[2]);
        ePos.push(e.target[0], e.target[1], e.target[2]);
    });
    eGeo.setAttribute('position', new THREE.Float32BufferAttribute(ePos, 3));
    const eMat = new THREE.LineBasicMaterial({
        color: 0x5588aa,
        transparent: true,
        opacity: P.edgeOp,
        blending: THREE.AdditiveBlending
    });
    const edges = new THREE.LineSegments(eGeo, eMat);
    edges.userData = { type: 'edges' };
    edges.visible = P.showEdge;
    scene.add(edges);
    meshEdges.push(edges);

    // Location nodes
    console.log('Building location nodes...');
    const nGeo = new THREE.SphereGeometry(P.locNodeSize * P.size, 16, 16);
    d.locations.forEach(loc => {
        const ci = loc.community % COLORS.length;
        const mat = new THREE.MeshStandardMaterial({
            color: 0xffffff,
            map: TEX[ci],
            emissive: COLORS[ci],
            emissiveIntensity: computeEmissiveIntensity(COLORS[ci], 0.6),
            metalness: 0.2,
            roughness: 0.7,
            transparent: true,
            opacity: 0.7
        });
        const m = new THREE.Mesh(nGeo, mat);
        m.position.set(loc.position[0] * P.spread, loc.position[1] * P.spread, loc.position[2] * P.spread);
        m.userData = { type: 'location', data: loc };
        scene.add(m);
        meshNodes.push(m);
    });

    // Community representatives
    console.log('Building community representatives...');
    d.communities.forEach(comm => {
        const ci = comm.id % COLORS.length;
        const cc = COLORS[ci];
        
        const norm = (comm.size - 34) / (122 - 34);
        const sz = (P.commSizeMin + norm * P.commSizeRange) * P.size;
        
        const cGeo = new THREE.SphereGeometry(sz, 24, 24);
        const cMat = new THREE.MeshStandardMaterial({
            color: cc,
            emissive: cc,
            emissiveIntensity: computeEmissiveIntensity(cc, 1.2),
            metalness: 0.1,
            roughness: 0.3
        });
        const core = new THREE.Mesh(cGeo, cMat);
        core.position.set(comm.position[0] * P.spread, comm.position[1] * P.spread, comm.position[2] * P.spread);
        core.userData = { type: 'representative', data: comm };
        scene.add(core);
        meshReps.push(core);
        
        const gGeo = new THREE.SphereGeometry(sz * 1.3, 20, 20);
        const gMat = new THREE.MeshBasicMaterial({
            color: cc,
            transparent: true,
            opacity: 0.2,
            side: THREE.BackSide,
            blending: THREE.AdditiveBlending
        });
        const glow = new THREE.Mesh(gGeo, gMat);
        glow.position.copy(core.position);
        glow.userData = { type: 'representative', data: comm };
        scene.add(glow);
        meshReps.push(glow);
        
        // Label
        const cvs = document.createElement('canvas');
        cvs.width = 64; cvs.height = 32;
        const ctx = cvs.getContext('2d');
        const col = new THREE.Color(cc);
        ctx.fillStyle = '#' + col.getHexString();
        ctx.font = 'Bold 20px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`C${comm.id}`, 32, 22);
        const tex = new THREE.CanvasTexture(cvs);
        const sMat = new THREE.SpriteMaterial({ map: tex, transparent: true, opacity: 0.85 });
        const sprite = new THREE.Sprite(sMat);
        sprite.position.set(core.position.x, core.position.y + sz + 0.8, core.position.z);
        sprite.scale.set(1.5, 0.75, 1);
        sprite.userData = { type: 'representative', data: comm };
        sprite.visible = P.showLabel;
        scene.add(sprite);
        meshLabels.push(sprite);
    });

    // Community connections
    console.log('Building community connections...');
    d.communities.forEach(comm => {
        comm.connections.forEach(connId => {
            const tgt = d.communities.find(c => c.id === connId);
            if (!tgt || comm.id >= connId) return;
            
            const c1 = new THREE.Color(COLORS[comm.id % COLORS.length]);
            const c2 = new THREE.Color(COLORS[tgt.id % COLORS.length]);

            const st = new THREE.Vector3(comm.position[0] * P.spread, comm.position[1] * P.spread, comm.position[2] * P.spread);
            const en = new THREE.Vector3(tgt.position[0] * P.spread, tgt.position[1] * P.spread, tgt.position[2] * P.spread);
            const dir = new THREE.Vector3().subVectors(en, st);
            const len = dir.length();
            const mid = new THREE.Vector3().addVectors(st, en).multiplyScalar(0.5);
            
            const szF = Math.max(0, comm.size + tgt.size);
            const rad = 0.0003 * szF * P.conn;
            if (rad <= 0) return;
            
            const geo = new THREE.CylinderGeometry(rad, rad, len, 12, 1, true);
            const mat = createGradientEdgeMaterial(c1, c2);
            
            const beam = new THREE.Mesh(geo, mat);
            beam.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().normalize());
            beam.position.copy(mid);
            beam.userData = { type: 'community_edge', data: { from: comm.id, to: connId, fromSize: comm.size, toSize: tgt.size }};
            beam.visible = P.showConn;
            scene.add(beam);
            meshEdges.push(beam);
        });
    });
    
    console.log('Visualization build complete');
}

function onMouse(e) {
    const rc = new THREE.Raycaster();
    const ms = new THREE.Vector2();
    const tip = document.getElementById('tooltip');

    ms.x = (e.clientX / window.innerWidth) * 2 - 1;
    ms.y = -(e.clientY / window.innerHeight) * 2 + 1;

    rc.setFromCamera(ms, cam);
    const hits = rc.intersectObjects(scene.children, true);

    let pk = null;
    for (const h of hits) {
        const t = h.object?.userData?.type;
        if (!t || t === 'edges' || t === 'bg') continue;
        pk = h.object;
        break;
    }

    if (pk && pk.userData.data) {
        const d = pk.userData.data;
        tip.style.display = 'block';
        tip.style.left = (e.clientX + 15) + 'px';
        tip.style.top = (e.clientY + 15) + 'px';
        
        if (pk.userData.type === 'representative') {
            const retweets = d.retweets ? d.retweets.toLocaleString() : 'N/A';
            const likes = d.likes ? d.likes.toLocaleString() : 'N/A';
            tip.innerHTML = `
                <strong>Community ${d.id}</strong><br>
                ━━━━━━━━━━━━━━━<br>
                Locations: ${d.size}<br>
                Total Reach: ${d.reach.toLocaleString()}<br>
                ${d.retweets ? `Retweets: ${retweets}<br>` : ''}
                ${d.likes ? `Likes: ${likes}` : ''}
            `.trim();
        } else if (pk.userData.type === 'location') {
            tip.innerHTML = `
                <strong>Location ${d.id}</strong><br>
                Community: ${d.community}<br>
                Reach: ${d.reach.toLocaleString()}
            `;
        } else if (pk.userData.type === 'community_edge') {
            tip.innerHTML = `
                <strong>Connection</strong><br>
                C${d.from} ↔ C${d.to}<br>
                Members: ${d.fromSize} + ${d.toSize}
            `;
        }
    } else {
        tip.style.display = 'none';
    }
}

function mkStars() {
    const geo = new THREE.BufferGeometry();
    const cnt = 3000;
    const pos = new Float32Array(cnt * 3);
    const col = new Float32Array(cnt * 3);
    
    for (let i = 0; i < cnt; i++) {
        const i3 = i * 3;
        const r = 80 + Math.random() * 180;
        const th = Math.random() * Math.PI * 2;
        const ph = Math.acos(2 * Math.random() - 1);
        
        pos[i3] = r * Math.sin(ph) * Math.cos(th);
        pos[i3 + 1] = r * Math.sin(ph) * Math.sin(th);
        pos[i3 + 2] = r * Math.cos(ph);
        
        const b = 0.4 + Math.random() * 0.5;
        col[i3] = col[i3 + 1] = col[i3 + 2] = b;
    }
    
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
    
    const mat = new THREE.PointsMaterial({
        size: 0.4,
        vertexColors: true,
        transparent: true,
        opacity: P.starOp,
        sizeAttenuation: true
    });
    
    meshStars = new THREE.Points(geo, mat);
    meshStars.userData = { type: 'bg' };
    scene.add(meshStars);
}

function computeEmissiveIntensity(col, base=1.0) {
    const c = new THREE.Color(col);
    const lum = 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b;
    const boost = 1.0 / Math.max(0.12, lum);
    const intensity = Math.min(6.0, P.bloom * 0.5 * boost * base);
    return intensity;
}

function applyParams() {
    if (bloom) bloom.strength = P.bloom;
    if (ctrl) ctrl.autoRotate = P.autoRot;
    if (meshStars) meshStars.material.opacity = P.starOp;
    meshLabels.forEach(m => m.visible = P.showLabel);
    
    meshEdges.forEach(m => {
        if (m.userData.type === 'edges') {
            m.visible = P.showEdge;
            if (m.material) m.material.opacity = P.edgeOp;
        } else if (m.userData.type === 'community_edge') {
            m.visible = P.showConn;
            if (m.material) m.material.opacity = P.connOp;
        }
    });

    try {
        meshNodes.forEach(m => {
            if (m.material && 'emissive' in m.material) {
                m.material.emissiveIntensity = computeEmissiveIntensity(m.material.emissive, 0.6);
                m.material.needsUpdate = true;
            }
        });

        meshReps.forEach((m, i) => {
            if (m.material && 'emissive' in m.material) {
                m.material.emissiveIntensity = computeEmissiveIntensity(m.material.emissive, 1.2);
                m.material.needsUpdate = true;
            }
        });

        meshEdges.forEach(m => {
            if (m.userData.type === 'community_edge' && m.material.uniforms) {
                m.material.uniforms.uBloom.value = P.bloom;
            }
        });
    } catch (e) {
        console.warn('applyParams: failed to update emissive intensities', e);
    }
}

function updateNodePositions() {
    // ... (implementation in main.js)
}

function clearMeshes() {
    [...meshNodes, ...meshReps, ...meshEdges, ...meshLabels].forEach(m => {
        scene.remove(m);
        if (m.geometry) m.geometry.dispose();
        if (m.material) {
            if (m.material.map) m.material.map.dispose();
            m.material.dispose();
        }
    });
    meshNodes = []; meshReps = []; meshEdges = []; meshLabels = [];
}

export { init, animate, buildVis, onMouse, applyParams, updateNodePositions, clearMeshes };
