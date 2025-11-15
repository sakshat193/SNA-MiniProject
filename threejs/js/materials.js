import * as THREE from 'three';

export function createGradientEdgeMaterial(color1, color2, opacity = 0.6) {
    return new THREE.ShaderMaterial({
        uniforms: {
            uColor1: { value: color1 },
            uColor2: { value: color2 },
            uBloom: { value: 1.0 },
            uOpacity: { value: opacity }
        },
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform vec3 uColor1;
            uniform vec3 uColor2;
            uniform float uBloom;
            uniform float uOpacity;
            varying vec2 vUv;

            void main() {
                vec3 color = mix(uColor1, uColor2, vUv.y);
                gl_FragColor = vec4(color * uBloom, uOpacity);
            }
        `,
        transparent: true,
        blending: THREE.AdditiveBlending,
        side: THREE.DoubleSide
    });
}

export function makeTex(hex) {
    const sz = 128;
    const cvs = document.createElement('canvas');
    cvs.width = cvs.height = sz;
    const ctx = cvs.getContext('2d');
    const col = new THREE.Color(hex);
    const grad = ctx.createRadialGradient(sz/2, sz/2, 0, sz/2, sz/2, sz/2);
    grad.addColorStop(0.0, '#fff');
    grad.addColorStop(0.35, '#fff');
    grad.addColorStop(1.0, '#' + col.getHexString());
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, sz, sz);
    const tex = new THREE.CanvasTexture(cvs);
    tex.needsUpdate = true;
    return tex;
}
