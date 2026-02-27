/**
 * ╔══════════════════════════════════════════════════════╗
 * ║  Toonify AR Lens Library v2.1 — All 10 Lenses       ║
 * ║  Pure Canvas 2D · Particle System · EMA-Tracked     ║
 * ╚══════════════════════════════════════════════════════╝
 */

/* ─── Particle System ────────────────────────────────── */
class ARParticle {
    constructor(x, y, cfg) {
        this.x = x; this.y = y;
        this.vx = (Math.random() - 0.5) * (cfg.speed || 3);
        this.vy = -(Math.random() * (cfg.rise || 2) + 0.5);
        this.life = 1;
        this.decay = 0.014 + Math.random() * 0.016;
        this.size = (cfg.size || 16) * (0.65 + Math.random() * 0.7);
        this.emoji = cfg.emoji || '✨';
        this.angle = Math.random() * Math.PI * 2;
        this.spin = (Math.random() - 0.5) * 0.1;
    }
    tick() { this.x += this.vx; this.y += this.vy; this.vy -= 0.03; this.life -= this.decay; this.angle += this.spin; }
    draw(ctx) {
        ctx.save(); ctx.globalAlpha = Math.max(0, this.life);
        ctx.translate(this.x, this.y); ctx.rotate(this.angle);
        ctx.font = `${this.size}px serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText(this.emoji, 0, 0); ctx.restore();
    }
    get dead() { return this.life <= 0; }
}
class ARParticleSystem {
    constructor() { this.pool = []; }
    emit(x, y, n, cfg) { for (let i = 0; i < n && this.pool.length < 100; i++) this.pool.push(new ARParticle(x, y, cfg)); }
    tick(ctx) { this.pool = this.pool.filter(p => { p.tick(); p.draw(ctx); return !p.dead; }); }
    clear() { this.pool = []; }
}
const _ps = new ARParticleSystem();
let _t = 0;

/* ─── Utility ─────────────────────────────────────────── */
function txt(ctx, e, x, y, size, angle = 0) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(angle);
    ctx.font = `${size}px serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(e, 0, 0); ctx.restore();
}

/* ══════════════════════════════════════════════════════
   1. DOG LENS  —  drawn ears, oval nose, tongue trigger
═══════════════════════════════════════════════════════ */
function renderDog(f, cv, ctx) {
    const { faceScale: s, roll, forehead, noseTip, leftTemple, rightTemple, mouthOpen, mouthCenter, leftEye, rightEye } = f;
    const ew = 80 * s, eh = 106 * s;

    // ── ears ──
    [[-1, leftTemple], [1, rightTemple]].forEach(([sign, t]) => {
        ctx.save();
        ctx.translate(t.x + sign * ew * 0.0, t.y - eh * 0.42);
        ctx.rotate(roll + sign * 0.2);
        // outer (brown)
        ctx.beginPath(); ctx.ellipse(0, 0, ew / 2, eh / 2, 0, 0, Math.PI * 2);
        ctx.fillStyle = '#8B4513'; ctx.fill();
        // inner (tan)
        ctx.beginPath(); ctx.ellipse(0, eh * 0.04, ew / 3.8, eh / 3.8, 0, 0, Math.PI * 2);
        ctx.fillStyle = '#D2691E'; ctx.fill();
        ctx.restore();
    });

    // ── dog nose (black oval) ──
    ctx.save();
    ctx.translate(noseTip.x, noseTip.y + 6 * s); ctx.rotate(roll);
    const nw = 34 * s, nh = 22 * s;
    ctx.beginPath(); ctx.ellipse(0, 0, nw / 2, nh / 2, 0, 0, Math.PI * 2);
    ctx.fillStyle = '#1a1a1a'; ctx.fill();
    ctx.beginPath(); ctx.ellipse(-nw * 0.16, -nh * 0.22, nw * 0.12, nh * 0.13, 0, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,255,255,0.45)'; ctx.fill();
    ctx.restore();

    // ── cheek blush ──
    [[leftEye.x - 26 * s, leftEye.y + 28 * s], [rightEye.x + 26 * s, rightEye.y + 28 * s]].forEach(([bx, by]) => {
        const g = ctx.createRadialGradient(bx, by, 0, bx, by, 24 * s);
        g.addColorStop(0, 'rgba(255,120,120,0.45)'); g.addColorStop(1, 'rgba(255,120,120,0)');
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(bx, by, 24 * s, 0, Math.PI * 2); ctx.fill();
    });

    // ── tongue when mouth open ──
    if (mouthOpen) {
        const wag = Math.sin(_t * 9) * 8 * s;
        const tw = 38 * s, th = 52 * s;
        ctx.save(); ctx.translate(mouthCenter.x + wag, mouthCenter.y + 10 * s);
        ctx.beginPath(); ctx.moveTo(-tw / 2, 0); ctx.quadraticCurveTo(-tw / 2, th, 0, th);
        ctx.quadraticCurveTo(tw / 2, th, tw / 2, 0); ctx.closePath();
        ctx.fillStyle = '#e05570'; ctx.fill();
        ctx.beginPath(); ctx.moveTo(0, 4); ctx.lineTo(0, th * 0.88);
        ctx.strokeStyle = 'rgba(0,0,0,0.12)'; ctx.lineWidth = 2.5 * s; ctx.stroke();
        ctx.restore();
    }
}

/* ══════════════════════════════════════════════════════
   2. CAT LENS  —  pointy ears, whiskers, slit pupils
═══════════════════════════════════════════════════════ */
function renderCat(f, cv, ctx) {
    const { faceScale: s, roll, noseTip, leftTemple, rightTemple, leftEye, rightEye } = f;

    // ── ears ──
    [[-1, leftTemple], [1, rightTemple]].forEach(([sign, t]) => {
        const es = 52 * s;
        ctx.save(); ctx.translate(t.x + sign * 6 * s, t.y - 50 * s); ctx.rotate(roll + sign * 0.15);
        // outer
        ctx.beginPath(); ctx.moveTo(0, -es); ctx.lineTo(es * 0.58, es * 0.28); ctx.lineTo(-es * 0.58, es * 0.28); ctx.closePath();
        ctx.fillStyle = '#2d2d2d'; ctx.fill();
        // inner pink
        ctx.beginPath(); ctx.moveTo(0, -es * 0.68); ctx.lineTo(es * 0.3, es * 0.08); ctx.lineTo(-es * 0.3, es * 0.08); ctx.closePath();
        ctx.fillStyle = '#ff9eb5'; ctx.fill();
        ctx.restore();
    });

    // ── nose ──
    ctx.save(); ctx.translate(noseTip.x, noseTip.y + 4 * s);
    const nw = 14 * s, nh = 10 * s;
    ctx.beginPath(); ctx.moveTo(0, -nh); ctx.lineTo(nw, nh); ctx.lineTo(-nw, nh); ctx.closePath();
    ctx.fillStyle = '#ffb7c5'; ctx.fill();
    ctx.restore();

    // ── whiskers ──
    const wag = Math.sin(_t * 2) * 2;
    ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.88)'; ctx.lineWidth = 1.5; ctx.lineCap = 'round';
    [[-1, noseTip.x - 14 * s], [1, noseTip.x + 14 * s]].forEach(([dir, bx]) => {
        for (let i = 0; i < 3; i++) {
            const by = noseTip.y + (i - 1) * 9 * s;
            ctx.beginPath(); ctx.moveTo(bx, by + wag);
            ctx.lineTo(bx + dir * 78 * s, by + (i - 1) * 4 * s + wag); ctx.stroke();
        }
    });
    ctx.restore();

    // ── slit pupil glow ──
    [leftEye, rightEye].forEach(eye => {
        ctx.save(); ctx.beginPath(); ctx.ellipse(eye.x, eye.y, 3 * s, 11 * s, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(40,255,90,0.38)'; ctx.fill(); ctx.restore();
    });
}

/* ══════════════════════════════════════════════════════
   3. GLASSES LENS  —  drawn frames aligned to eyes
═══════════════════════════════════════════════════════ */
function renderGlasses(f, cv, ctx) {
    const { faceScale: s, roll, center, eyeDist } = f;
    const lw = eyeDist * 0.7, lh = lw * 0.62, r = lh * 0.34;

    ctx.save(); ctx.translate(center.x, center.y + 4 * s); ctx.rotate(roll);

    const drawFrame = (cx) => {
        const x = cx - lw / 2, y = -lh / 2;
        // tinted fill
        ctx.beginPath(); ctx.moveTo(x + r, y); ctx.lineTo(x + lw - r, y); ctx.arcTo(x + lw, y, x + lw, y + r, r);
        ctx.lineTo(x + lw, y + lh - r); ctx.arcTo(x + lw, y + lh, x + lw - r, y + lh, r);
        ctx.lineTo(x + r, y + lh); ctx.arcTo(x, y + lh, x, y + lh - r, r);
        ctx.lineTo(x, y + r); ctx.arcTo(x, y, x + r, y, r); ctx.closePath();
        ctx.fillStyle = 'rgba(15,15,50,0.58)'; ctx.fill();
        ctx.strokeStyle = '#1a1a1a'; ctx.lineWidth = 3.5 * s; ctx.stroke();
        // glare
        ctx.save(); ctx.beginPath(); ctx.ellipse(cx - lw * 0.22, -lh * 0.2, lw * 0.1, lh * 0.12, -0.45, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255,255,255,0.3)'; ctx.fill(); ctx.restore();
    };

    drawFrame(-eyeDist / 2); drawFrame(eyeDist / 2);

    // bridge
    ctx.beginPath(); ctx.moveTo(-eyeDist / 2 + lw / 2, 0); ctx.lineTo(eyeDist / 2 - lw / 2, 0);
    ctx.strokeStyle = '#111'; ctx.lineWidth = 4 * s; ctx.stroke();

    // temples (arms)
    [[-eyeDist / 2 - lw / 2, -1], [eyeDist / 2 + lw / 2, 1]].forEach(([bx, d]) => {
        ctx.beginPath(); ctx.moveTo(bx, 0); ctx.lineTo(bx + d * 55 * s, -8 * s);
        ctx.strokeStyle = '#111'; ctx.lineWidth = 3.5 * s; ctx.stroke();
    });
    ctx.restore();
}

/* ══════════════════════════════════════════════════════
   4. CROWN LENS  —  vector crown with animated jewels
═══════════════════════════════════════════════════════ */
function renderCrown(f, cv, ctx) {
    const { faceScale: s, roll, forehead, eyeDist } = f;
    const bob = Math.sin(_t * 2.2) * 4 * s;
    const w = eyeDist * 1.9, h = w * 0.58;

    ctx.save(); ctx.translate(forehead.x, forehead.y + bob); ctx.rotate(roll);
    const x = -w / 2, y = -h * 1.1;

    // gradient fill
    const gr = ctx.createLinearGradient(x, y, x, y + h);
    gr.addColorStop(0, '#FFE234'); gr.addColorStop(0.6, '#FFA500'); gr.addColorStop(1, '#FF8C00');

    // crown silhouette (5 spikes)
    ctx.beginPath(); ctx.moveTo(x, y + h);
    const pts = [0, h * 0.55, 0, h * 0.55, 0].map((py, i) => ({ px: x + (i / 4) * w, py: i % 2 === 0 ? y : y + py }));
    pts.forEach(p => ctx.lineTo(p.px, p.py));
    ctx.lineTo(x + w, y + h); ctx.closePath();
    ctx.fillStyle = gr; ctx.fill(); ctx.strokeStyle = '#b8860b'; ctx.lineWidth = 2.5; ctx.stroke();

    // jewels
    ['#e74c3c', '#9b59b6', '#3498db', '#e74c3c'].forEach((col, i) => {
        const jx = x + ((i * 2 + 1) / 8) * w;
        const jy = y + h * 0.3 + Math.sin(_t * 3 + i) * 2;
        const jr = 7 * s;
        ctx.save(); ctx.beginPath(); ctx.arc(jx, jy, jr, 0, Math.PI * 2);
        ctx.fillStyle = col; ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,0.5)'; ctx.lineWidth = 1; ctx.stroke();
        // sparkle on jewel
        ctx.globalAlpha = 0.5 + 0.5 * Math.sin(_t * 5 + i);
        ctx.fillStyle = 'white'; ctx.beginPath(); ctx.arc(jx - jr * 0.3, jy - jr * 0.3, jr * 0.25, 0, Math.PI * 2); ctx.fill();
        ctx.restore();
    });

    ctx.restore();
}

/* ══════════════════════════════════════════════════════
   5. SPARKLES LENS  —  particle system + orbit
═══════════════════════════════════════════════════════ */
function renderSparkles(f, cv, ctx) {
    const { faceScale: s, center } = f;
    const em = ['✨', '💫', '⭐', '🌟'];

    if (Math.random() < 0.5) {
        const a = Math.random() * Math.PI * 2;
        const r = (75 + Math.random() * 85) * s;
        _ps.emit(center.x + Math.cos(a) * r, center.y + Math.sin(a) * r * 0.4, 1,
            { emoji: em[Math.floor(Math.random() * 4)], size: 17 * s, speed: 1.8, rise: 0.9 });
    }

    // 6 orbiting icons
    for (let i = 0; i < 6; i++) {
        const a = _t * 1.5 + i * (Math.PI / 3);
        const r = 112 * s;
        ctx.save(); ctx.globalAlpha = 0.65 + 0.35 * Math.sin(_t * 3 + i);
        txt(ctx, em[i % 4], center.x + Math.cos(a) * r, center.y + Math.sin(a) * r * 0.38, 26 * s);
        ctx.globalAlpha = 1; ctx.restore();
    }
}

/* ══════════════════════════════════════════════════════
   6. BEAUTY LENS  —  soft glow + eye shimmer + roses
═══════════════════════════════════════════════════════ */
function renderBeauty(f, cv, ctx) {
    const { faceScale: s, center, leftEye, rightEye } = f;

    // face glow
    const g = ctx.createRadialGradient(center.x, center.y, 0, center.x, center.y, 200 * s);
    g.addColorStop(0, 'rgba(255,200,200,0.2)'); g.addColorStop(1, 'rgba(255,182,193,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(center.x, center.y, 200 * s, 0, Math.PI * 2); ctx.fill();

    // eye shimmer
    [leftEye, rightEye].forEach((eye, i) => {
        const g2 = ctx.createRadialGradient(eye.x, eye.y, 0, eye.x, eye.y, 28 * s);
        g2.addColorStop(0, `rgba(255,150,200,${0.28 + 0.1 * Math.sin(_t * 4 + i)})`);
        g2.addColorStop(1, 'rgba(255,150,200,0)');
        ctx.save(); ctx.fillStyle = g2;
        ctx.beginPath(); ctx.arc(eye.x, eye.y, 28 * s, 0, Math.PI * 2); ctx.fill(); ctx.restore();
    });

    // roses + hearts
    ctx.save(); ctx.globalAlpha = 0.8 + 0.2 * Math.sin(_t * 1.5);
    txt(ctx, '🌸', leftEye.x - 26 * s, leftEye.y + 26 * s, 24 * s);
    txt(ctx, '🌸', rightEye.x + 26 * s, rightEye.y + 26 * s, 24 * s);
    txt(ctx, '💕', center.x, f.forehead.y - 30 * s, 22 * s);
    ctx.globalAlpha = 1; ctx.restore();
}

/* ══════════════════════════════════════════════════════
   7. RAINBOW LENS  —  arc above head + clouds
═══════════════════════════════════════════════════════ */
function renderRainbow(f, cv, ctx) {
    const { faceScale: s, forehead, leftTemple, rightTemple, roll, eyeDist } = f;
    const cx = forehead.x, cy = forehead.y + 10 * s;
    const OR = eyeDist * 1.35, IR = OR * 0.6;
    const colors = ['#FF0000', '#FF7700', '#FFFF00', '#00CC00', '#0077FF', '#8800FF'];
    const bw = (OR - IR) / colors.length;

    ctx.save(); ctx.translate(cx, cy); ctx.rotate(roll);
    colors.forEach((col, i) => {
        const r1 = IR + i * bw, r2 = r1 + bw;
        const p = 1 + 0.025 * Math.sin(_t * 3 + i);
        ctx.beginPath(); ctx.arc(0, 0, r2 * p, Math.PI, 0);
        ctx.arc(0, 0, r1 * p, 0, Math.PI, true); ctx.closePath();
        ctx.fillStyle = col; ctx.globalAlpha = 0.72; ctx.fill();
    });
    ctx.globalAlpha = 1; ctx.restore();

    txt(ctx, '☁️', leftTemple.x - 20 * s, leftTemple.y - 50 * s, 38 * s, roll);
    txt(ctx, '☁️', rightTemple.x + 20 * s, rightTemple.y - 50 * s, 38 * s, roll);
}

/* ══════════════════════════════════════════════════════
   8. CYBORG LENS  —  HUD scan + rotating reticles
═══════════════════════════════════════════════════════ */
function renderCyborg(f, cv, ctx) {
    const { faceScale: s, center, leftEye, rightEye, forehead } = f;

    // scan line
    const sy = forehead.y + ((_t * 120 * s) % (220 * s));
    ctx.fillStyle = `rgba(0,255,200,${0.14 + 0.06 * Math.sin(_t * 10)})`;
    ctx.fillRect(center.x - 110 * s, sy, 220 * s, 3);

    // face circle
    ctx.save(); ctx.strokeStyle = `rgba(0,255,200,${0.22 + 0.1 * Math.sin(_t * 5)})`;
    ctx.lineWidth = 1.2; ctx.setLineDash([5, 7]);
    ctx.beginPath(); ctx.arc(center.x, center.y, 108 * s, 0, Math.PI * 2); ctx.stroke();
    ctx.setLineDash([]); ctx.restore();

    // reticles
    [leftEye, rightEye].forEach((eye, idx) => {
        ctx.save(); ctx.translate(eye.x, eye.y); ctx.rotate(_t * 1.5 + idx * Math.PI);
        ctx.strokeStyle = 'rgba(0,255,200,0.9)'; ctx.lineWidth = 2;
        for (let i = 0; i < 4; i++) {
            const a = (i / 4) * Math.PI * 2;
            ctx.beginPath(); ctx.arc(0, 0, 22 * s, a + 0.2, a + Math.PI / 2 - 0.2); ctx.stroke();
        }
        ctx.beginPath(); ctx.arc(0, 0, 3 * s, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(0,255,200,1)'; ctx.fill();
        ctx.restore();
    });

    // HUD text
    ctx.fillStyle = `rgba(0,255,200,${0.8 + 0.2 * Math.sin(_t * 2)})`;
    ctx.font = `${11 * s}px monospace`; ctx.textAlign = 'left';
    const pct = ((_t * 37) % 100).toFixed(0).padStart(2, '0');
    ctx.fillText(`FACE ID: 99.${pct}%`, center.x - 92 * s, forehead.y - 28 * s);
    ctx.fillText('AR: TRACKING', center.x - 92 * s, forehead.y - 14 * s);
}

/* ══════════════════════════════════════════════════════
   9. FIRE LENS  —  particles from hairline + face glow
═══════════════════════════════════════════════════════ */
function renderFire(f, cv, ctx) {
    const { faceScale: s, forehead, leftTemple, rightTemple, center } = f;
    const em = ['🔥', '💥', '✨'];

    if (Math.random() < 0.75) {
        const px = leftTemple.x + Math.random() * (rightTemple.x - leftTemple.x);
        _ps.emit(px, forehead.y - 5 * s, 1,
            { emoji: em[Math.floor(Math.random() * 3)], size: (22 + Math.random() * 14) * s, speed: 2.5, rise: 2.8 });
    }

    // warm face glow
    const g = ctx.createRadialGradient(center.x, center.y - 15 * s, 0, center.x, center.y, 130 * s);
    g.addColorStop(0, `rgba(255,80,0,${0.1 + 0.05 * Math.sin(_t * 8)})`);
    g.addColorStop(1, 'rgba(255,40,0,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(center.x, center.y, 130 * s, 0, Math.PI * 2); ctx.fill();
}

/* ══════════════════════════════════════════════════════
   10. ASTRONAUT LENS  —  glass helmet + stars
═══════════════════════════════════════════════════════ */
function renderAstronaut(f, cv, ctx) {
    const { center, faceScale: s, roll, leftTemple, rightTemple } = f;
    const r = Math.hypot(rightTemple.x - leftTemple.x, rightTemple.y - leftTemple.y) * 0.73;

    ctx.save(); ctx.translate(center.x, center.y); ctx.rotate(roll);

    // helmet
    const hg = ctx.createRadialGradient(-r * 0.22, -r * 0.22, r * 0.08, 0, 0, r * 1.25);
    hg.addColorStop(0, 'rgba(210,210,240,0.28)');
    hg.addColorStop(0.7, 'rgba(180,180,210,0.22)');
    hg.addColorStop(1, 'rgba(100,100,150,0.45)');
    ctx.beginPath(); ctx.arc(0, 0, r * 1.2, 0, Math.PI * 2);
    ctx.fillStyle = hg; ctx.fill();
    ctx.strokeStyle = 'rgba(200,200,255,0.65)'; ctx.lineWidth = 5 * s; ctx.stroke();

    // visor glare
    ctx.beginPath(); ctx.ellipse(-r * 0.28, -r * 0.32, r * 0.24, r * 0.11, -0.5, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,255,255,0.22)'; ctx.fill();

    // stars through visor
    ctx.globalAlpha = 0.55;
    for (let i = 0; i < 7; i++) {
        const a = _t * 0.28 + i * 0.898;
        const sr = r * (0.42 + (i % 3) * 0.16);
        ctx.beginPath(); ctx.arc(Math.cos(a) * sr, Math.sin(a) * sr, 2, 0, Math.PI * 2);
        ctx.fillStyle = '#fff'; ctx.fill();
    }
    ctx.globalAlpha = 1;
    ctx.restore();
}

/* ─── Lens Registry ─────────────────────────────────── */
window.ARLenses = {
    _map: {
        dog: renderDog, cat: renderCat, sunglasses: renderGlasses,
        heart_crown: renderCrown, sparkles: renderSparkles, beauty: renderBeauty,
        rainbow: renderRainbow, cyborg: renderCyborg, fire: renderFire, astronaut: renderAstronaut,
    },
    render(id, face, canvas, ctx) {
        _t += 0.016;
        const fn = this._map[id];
        if (fn) { ctx.save(); fn(face, canvas, ctx); ctx.restore(); }
        _ps.tick(ctx);
    },
    reset() { _t = 0; _ps.clear(); }
};
