/**
 * ╔══════════════════════════════════════════════════════╗
 * ║  Toonify AR Lens Library v2.2                       ║
 * ║  Fixed positioning · 10 face lenses · 5 backgrounds ║
 * ╚══════════════════════════════════════════════════════╝
 *
 * COORDINATE SYSTEM NOTE:
 *  - Both video and arCanvas have CSS scaleX(-1) applied.
 *  - MediaPipe landmarks are in the RAW (unmirrored) frame.
 *  - Drawing at landmark(x,y) on canvas → after CSS mirror
 *    → appears correctly at the matching face position on screen.
 *  - "Left ear" in code = smaller x in raw space → appears on
 *    the RIGHT side of the mirrored selfie view (correct for user).
 */

/* ─── Particles ──────────────────────────────────────── */
class ARParticle {
    constructor(x, y, cfg) {
        this.x = x; this.y = y;
        this.vx = (Math.random() - 0.5) * (cfg.speed || 2.5);
        this.vy = -(Math.random() * (cfg.rise || 2) + 0.5);
        this.life = 1;
        this.decay = 0.013 + Math.random() * 0.015;
        this.size = (cfg.size || 16) * (0.65 + Math.random() * 0.7);
        this.emoji = cfg.emoji || '✨';
        this.angle = Math.random() * Math.PI * 2;
        this.spin = (Math.random() - 0.5) * 0.1;
    }
    tick() {
        this.x += this.vx; this.y += this.vy; this.vy -= 0.03;
        this.life -= this.decay; this.angle += this.spin;
    }
    draw(ctx) {
        if (this.life <= 0) return;
        ctx.save(); ctx.globalAlpha = Math.max(0, this.life);
        ctx.translate(this.x, this.y); ctx.rotate(this.angle);
        ctx.font = `${this.size}px serif`;
        ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText(this.emoji, 0, 0); ctx.restore();
    }
    get dead() { return this.life <= 0; }
}

class ARParticleSystem {
    constructor() { this.pool = []; }
    emit(x, y, n, cfg) {
        for (let i = 0; i < n && this.pool.length < 100; i++)
            this.pool.push(new ARParticle(x, y, cfg));
    }
    tick(ctx) {
        this.pool = this.pool.filter(p => { p.tick(); p.draw(ctx); return !p.dead; });
    }
    clear() { this.pool = []; }
}

const _ps = new ARParticleSystem();
let _t = 0;

/* ─── Utility ─────────────────────────────────────────── */
const txt = (ctx, e, x, y, size, angle = 0) => {
    ctx.save(); ctx.translate(x, y); ctx.rotate(angle);
    ctx.font = `${size}px serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(e, 0, 0); ctx.restore();
};

/* ══════════════════════════════════════════════════════
   1. DOG LENS
   Ears anchored ABOVE forehead, offset left/right by eyeDist
   Nose oval on noseTip, tongue appears if mouth open
═══════════════════════════════════════════════════════ */
function renderDog(f, cv, ctx) {
    const { faceScale: s, roll, forehead, noseTip, center, eyeDist,
        mouthOpen, mouthCenter, leftEye, rightEye } = f;

    // ── Ear positions: above forehead, left/right of center ──
    const earW = 70 * s, earH = 90 * s;
    const earY = forehead.y - earH * 0.45; // above forehead

    [
        [center.x - eyeDist * 0.55, roll + 0.2, -1],   // raw-left ear
        [center.x + eyeDist * 0.55, roll - 0.2, 1],   // raw-right ear
    ].forEach(([ex, ang]) => {
        ctx.save(); ctx.translate(ex, earY); ctx.rotate(ang);
        // outer (brown)
        ctx.beginPath(); ctx.ellipse(0, 0, earW / 2, earH / 2, 0, 0, Math.PI * 2);
        ctx.fillStyle = '#8B4513'; ctx.fill();
        // inner (tan)
        ctx.beginPath(); ctx.ellipse(0, earH * 0.04, earW / 3.6, earH / 3.6, 0, 0, Math.PI * 2);
        ctx.fillStyle = '#D2691E'; ctx.fill();
        ctx.restore();
    });

    // ── Nose (black oval on nose tip) ──
    const nw = 38 * s, nh = 25 * s;
    ctx.save(); ctx.translate(noseTip.x, noseTip.y + 4 * s); ctx.rotate(roll);
    ctx.beginPath(); ctx.ellipse(0, 0, nw / 2, nh / 2, 0, 0, Math.PI * 2);
    ctx.fillStyle = '#111'; ctx.fill();
    // highlight
    ctx.beginPath(); ctx.ellipse(-nw * 0.16, -nh * 0.22, nw * 0.12, nh * 0.15, 0, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,255,255,0.45)'; ctx.fill();
    ctx.restore();

    // ── Cheek blush ──
    [[leftEye.x - 24 * s, leftEye.y + 30 * s], [rightEye.x + 24 * s, rightEye.y + 30 * s]].forEach(([bx, by]) => {
        const g = ctx.createRadialGradient(bx, by, 0, bx, by, 26 * s);
        g.addColorStop(0, 'rgba(255,110,110,0.45)'); g.addColorStop(1, 'rgba(255,110,110,0)');
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(bx, by, 26 * s, 0, Math.PI * 2); ctx.fill();
    });

    // ── Tongue when mouth open ──
    if (mouthOpen) {
        const wag = Math.sin(_t * 9) * 9 * s;
        const tw = 40 * s, th = 56 * s;
        ctx.save(); ctx.translate(mouthCenter.x + wag, mouthCenter.y + 8 * s);
        ctx.beginPath(); ctx.moveTo(-tw / 2, 0); ctx.quadraticCurveTo(-tw / 2, th, 0, th);
        ctx.quadraticCurveTo(tw / 2, th, tw / 2, 0); ctx.closePath();
        ctx.fillStyle = '#e0557a'; ctx.fill();
        ctx.beginPath(); ctx.moveTo(0, 4); ctx.lineTo(0, th * 0.88);
        ctx.strokeStyle = 'rgba(0,0,0,0.12)'; ctx.lineWidth = 2.5 * s; ctx.stroke();
        ctx.restore();
    }
}

/* ══════════════════════════════════════════════════════
   2. CAT LENS
   Pointy ears above forehead, drawn whiskers, slit pupils
═══════════════════════════════════════════════════════ */
function renderCat(f, cv, ctx) {
    const { faceScale: s, roll, forehead, noseTip, center, eyeDist, leftEye, rightEye } = f;

    const es = 55 * s;
    const earY = forehead.y - es * 0.5;

    [
        [center.x - eyeDist * 0.42, roll + 0.15],  // left ear
        [center.x + eyeDist * 0.42, roll - 0.15],  // right ear
    ].forEach(([ex, ang]) => {
        ctx.save(); ctx.translate(ex, earY); ctx.rotate(ang);
        // outer dark triangle
        ctx.beginPath(); ctx.moveTo(0, -es); ctx.lineTo(es * 0.58, es * 0.3); ctx.lineTo(-es * 0.58, es * 0.3); ctx.closePath();
        ctx.fillStyle = '#2d2d2d'; ctx.fill();
        // inner pink
        ctx.beginPath(); ctx.moveTo(0, -es * 0.68); ctx.lineTo(es * 0.3, es * 0.08); ctx.lineTo(-es * 0.3, es * 0.08); ctx.closePath();
        ctx.fillStyle = '#ff9eb5'; ctx.fill();
        ctx.restore();
    });

    // nose triangle
    ctx.save(); ctx.translate(noseTip.x, noseTip.y + 3 * s);
    const nw = 14 * s, nh = 10 * s;
    ctx.beginPath(); ctx.moveTo(0, -nh); ctx.lineTo(nw, nh); ctx.lineTo(-nw, nh); ctx.closePath();
    ctx.fillStyle = '#ffb7c5'; ctx.fill(); ctx.restore();

    // whiskers (3 per side)
    const wag = Math.sin(_t * 2) * 2.5;
    ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.9)'; ctx.lineWidth = 1.6; ctx.lineCap = 'round';
    for (let i = 0; i < 3; i++) {
        const oy = (i - 1) * 10 * s;
        // left side whiskers
        ctx.beginPath(); ctx.moveTo(noseTip.x - 12 * s, noseTip.y + oy + wag);
        ctx.lineTo(noseTip.x - 12 * s - 80 * s, noseTip.y + oy - (i - 1) * 5 * s + wag); ctx.stroke();
        // right side whiskers
        ctx.beginPath(); ctx.moveTo(noseTip.x + 12 * s, noseTip.y + oy + wag);
        ctx.lineTo(noseTip.x + 12 * s + 80 * s, noseTip.y + oy - (i - 1) * 5 * s + wag); ctx.stroke();
    }
    ctx.restore();

    // slit pupils (green glow)
    [leftEye, rightEye].forEach(eye => {
        ctx.save(); ctx.beginPath(); ctx.ellipse(eye.x, eye.y, 3.5 * s, 12 * s, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(40,255,90,0.38)'; ctx.fill(); ctx.restore();
    });
}

/* ══════════════════════════════════════════════════════
   3. GLASSES LENS  —  aligned to eye corners
═══════════════════════════════════════════════════════ */
function renderGlasses(f, cv, ctx) {
    const { faceScale: s, roll, center, eyeDist, leftEyeCorner, rightEyeCorner } = f;
    // Frame sized to inter-eye-corner distance
    const lw = eyeDist * 0.72, lh = lw * 0.6, r = lh * 0.32;

    ctx.save(); ctx.translate(center.x, center.y + 4 * s); ctx.rotate(roll);

    const drawFrame = (cx) => {
        const x = cx - lw / 2, y = -lh / 2;
        ctx.beginPath();
        ctx.moveTo(x + r, y); ctx.lineTo(x + lw - r, y); ctx.arcTo(x + lw, y, x + lw, y + r, r);
        ctx.lineTo(x + lw, y + lh - r); ctx.arcTo(x + lw, y + lh, x + lw - r, y + lh, r);
        ctx.lineTo(x + r, y + lh); ctx.arcTo(x, y + lh, x, y + lh - r, r);
        ctx.lineTo(x, y + r); ctx.arcTo(x, y, x + r, y, r); ctx.closePath();
        ctx.fillStyle = 'rgba(10,10,50,0.62)'; ctx.fill();
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
   4. CROWN LENS
═══════════════════════════════════════════════════════ */
function renderCrown(f, cv, ctx) {
    const { faceScale: s, roll, forehead, templeSpan } = f;
    const bob = Math.sin(_t * 2.2) * 4 * s;
    const w = templeSpan * 1.05, h = w * 0.55;

    ctx.save(); ctx.translate(forehead.x, forehead.y + bob); ctx.rotate(roll);
    const x = -w / 2, y = -h * 1.05;

    const gr = ctx.createLinearGradient(x, y, x, y + h);
    gr.addColorStop(0, '#FFE234'); gr.addColorStop(0.6, '#FFA500'); gr.addColorStop(1, '#FF8C00');

    ctx.beginPath(); ctx.moveTo(x, y + h);
    // 5 spikes
    for (let i = 0; i <= 4; i++) {
        const px = x + (i / 4) * w;
        const py = i % 2 === 0 ? y : y + h * 0.52;
        ctx.lineTo(px, py);
    }
    ctx.lineTo(x + w, y + h); ctx.closePath();
    ctx.fillStyle = gr; ctx.fill(); ctx.strokeStyle = '#b8860b'; ctx.lineWidth = 2.5; ctx.stroke();

    // Jewels
    ['#e74c3c', '#9b59b6', '#3498db', '#2ecc71'].forEach((col, i) => {
        const jx = x + ((i * 2 + 1) / 8) * w;
        const jy = y + h * 0.3 + Math.sin(_t * 3 + i) * 2;
        ctx.save(); ctx.beginPath(); ctx.arc(jx, jy, 7 * s, 0, Math.PI * 2);
        ctx.fillStyle = col; ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,0.5)'; ctx.lineWidth = 1; ctx.stroke();
        // sparkle
        ctx.globalAlpha = 0.5 + 0.5 * Math.sin(_t * 5 + i);
        ctx.fillStyle = 'white'; ctx.beginPath(); ctx.arc(jx - 2.5 * s, jy - 2.5 * s, 2 * s, 0, Math.PI * 2); ctx.fill();
        ctx.restore();
    });
    ctx.restore();
}

/* ══════════════════════════════════════════════════════
   5. SPARKLES
═══════════════════════════════════════════════════════ */
function renderSparkles(f, cv, ctx) {
    const { faceScale: s, center } = f;
    const em = ['✨', '💫', '⭐', '🌟'];
    if (Math.random() < 0.5) {
        const a = Math.random() * Math.PI * 2, r = (70 + Math.random() * 80) * s;
        _ps.emit(center.x + Math.cos(a) * r, center.y + Math.sin(a) * r * 0.4, 1,
            { emoji: em[Math.floor(Math.random() * 4)], size: 17 * s, speed: 1.8, rise: 0.9 });
    }
    for (let i = 0; i < 6; i++) {
        const a = _t * 1.5 + i * (Math.PI / 3), r = 110 * s;
        ctx.save(); ctx.globalAlpha = 0.65 + 0.35 * Math.sin(_t * 3 + i);
        txt(ctx, em[i % 4], center.x + Math.cos(a) * r, center.y + Math.sin(a) * r * 0.38, 25 * s);
        ctx.globalAlpha = 1; ctx.restore();
    }
}

/* ══════════════════════════════════════════════════════
   6. BEAUTY
═══════════════════════════════════════════════════════ */
function renderBeauty(f, cv, ctx) {
    const { faceScale: s, center, forehead, leftEye, rightEye } = f;
    // glow
    const g = ctx.createRadialGradient(center.x, center.y, 0, center.x, center.y, 200 * s);
    g.addColorStop(0, 'rgba(255,200,200,0.22)'); g.addColorStop(1, 'rgba(255,182,193,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(center.x, center.y, 200 * s, 0, Math.PI * 2); ctx.fill();
    // eye shimmer
    [leftEye, rightEye].forEach((eye, i) => {
        const g2 = ctx.createRadialGradient(eye.x, eye.y, 0, eye.x, eye.y, 30 * s);
        g2.addColorStop(0, `rgba(255,145,200,${0.3 + 0.1 * Math.sin(_t * 4 + i)})`);
        g2.addColorStop(1, 'rgba(255,145,200,0)');
        ctx.save(); ctx.fillStyle = g2; ctx.beginPath(); ctx.arc(eye.x, eye.y, 30 * s, 0, Math.PI * 2); ctx.fill(); ctx.restore();
    });
    ctx.save(); ctx.globalAlpha = 0.8 + 0.2 * Math.sin(_t * 1.5);
    txt(ctx, '🌸', leftEye.x - 28 * s, leftEye.y + 28 * s, 24 * s);
    txt(ctx, '🌸', rightEye.x + 28 * s, rightEye.y + 28 * s, 24 * s);
    txt(ctx, '💕', forehead.x, forehead.y - 28 * s, 20 * s);
    ctx.globalAlpha = 1; ctx.restore();
}

/* ══════════════════════════════════════════════════════
   7. RAINBOW
═══════════════════════════════════════════════════════ */
function renderRainbow(f, cv, ctx) {
    const { faceScale: s, forehead, leftTemple, rightTemple, roll, templeSpan } = f;
    const OR = templeSpan * 0.72, IR = OR * 0.6;
    const colors = ['#FF0000', '#FF7700', '#FFFF00', '#00CC00', '#0077FF', '#8800FF'];
    const bw = (OR - IR) / colors.length;

    ctx.save(); ctx.translate(forehead.x, forehead.y + 10 * s); ctx.rotate(roll);
    colors.forEach((col, i) => {
        const r1 = IR + i * bw, r2 = r1 + bw;
        const p = 1 + 0.025 * Math.sin(_t * 3 + i);
        ctx.beginPath(); ctx.arc(0, 0, r2 * p, Math.PI, 0);
        ctx.arc(0, 0, r1 * p, 0, Math.PI, true); ctx.closePath();
        ctx.fillStyle = col; ctx.globalAlpha = 0.72; ctx.fill();
    });
    ctx.globalAlpha = 1; ctx.restore();

    txt(ctx, '☁️', leftTemple.x - 18 * s, leftTemple.y - 50 * s, 36 * s, roll);
    txt(ctx, '☁️', rightTemple.x + 18 * s, rightTemple.y - 50 * s, 36 * s, roll);
}

/* ══════════════════════════════════════════════════════
   8. CYBORG
═══════════════════════════════════════════════════════ */
function renderCyborg(f, cv, ctx) {
    const { faceScale: s, center, leftEye, rightEye, forehead } = f;
    const scanY = forehead.y + ((_t * 120 * s) % (220 * s));

    ctx.save();
    ctx.fillStyle = `rgba(0,255,200,${0.14 + 0.06 * Math.sin(_t * 10)})`;
    ctx.fillRect(center.x - 112 * s, scanY, 224 * s, 3);

    ctx.strokeStyle = `rgba(0,255,200,${0.22 + 0.1 * Math.sin(_t * 5)})`;
    ctx.lineWidth = 1.2; ctx.setLineDash([5, 7]);
    ctx.beginPath(); ctx.arc(center.x, center.y, 110 * s, 0, Math.PI * 2); ctx.stroke();
    ctx.setLineDash([]); ctx.restore();

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

    ctx.fillStyle = `rgba(0,255,200,${0.8 + 0.2 * Math.sin(_t * 2)})`;
    ctx.font = `${Math.max(10, 11 * s)}px monospace`; ctx.textAlign = 'left';
    const pct = (Math.floor(_t * 37) % 100).toString().padStart(2, '0');
    ctx.fillText(`FACE ID: 99.${pct}%`, center.x - 92 * s, forehead.y - 28 * s);
    ctx.fillText('AR: TRACKING', center.x - 92 * s, forehead.y - 14 * s);
}

/* ══════════════════════════════════════════════════════
   9. FIRE
═══════════════════════════════════════════════════════ */
function renderFire(f, cv, ctx) {
    const { faceScale: s, forehead, leftTemple, rightTemple, center } = f;
    const em = ['🔥', '💥', '✨'];
    if (Math.random() < 0.75) {
        const px = leftTemple.x + Math.random() * (rightTemple.x - leftTemple.x);
        _ps.emit(px, forehead.y, 1,
            { emoji: em[Math.floor(Math.random() * 3)], size: (22 + Math.random() * 13) * s, speed: 2.5, rise: 2.8 });
    }
    const g = ctx.createRadialGradient(center.x, center.y - 15 * s, 0, center.x, center.y, 130 * s);
    g.addColorStop(0, `rgba(255,80,0,${0.1 + 0.05 * Math.sin(_t * 8)})`);
    g.addColorStop(1, 'rgba(255,40,0,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(center.x, center.y, 130 * s, 0, Math.PI * 2); ctx.fill();
}

/* ══════════════════════════════════════════════════════
   10. ASTRONAUT
═══════════════════════════════════════════════════════ */
function renderAstronaut(f, cv, ctx) {
    const { center, faceScale: s, roll, templeSpan } = f;
    const r = templeSpan * 0.62;

    ctx.save(); ctx.translate(center.x, center.y); ctx.rotate(roll);

    const hg = ctx.createRadialGradient(-r * 0.22, -r * 0.22, r * 0.08, 0, 0, r * 1.25);
    hg.addColorStop(0, 'rgba(210,210,240,0.28)');
    hg.addColorStop(0.7, 'rgba(180,180,215,0.22)');
    hg.addColorStop(1, 'rgba(100,100,150,0.45)');
    ctx.beginPath(); ctx.arc(0, 0, r * 1.18, 0, Math.PI * 2);
    ctx.fillStyle = hg; ctx.fill();
    ctx.strokeStyle = 'rgba(200,200,255,0.65)'; ctx.lineWidth = 5 * s; ctx.stroke();

    ctx.beginPath(); ctx.ellipse(-r * 0.28, -r * 0.32, r * 0.24, r * 0.11, -0.5, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,255,255,0.22)'; ctx.fill();

    ctx.globalAlpha = 0.55;
    for (let i = 0; i < 7; i++) {
        const a = _t * 0.28 + i * 0.898, sr = r * (0.4 + (i % 3) * 0.16);
        ctx.beginPath(); ctx.arc(Math.cos(a) * sr, Math.sin(a) * sr, 2, 0, Math.PI * 2);
        ctx.fillStyle = '#fff'; ctx.fill();
    }
    ctx.globalAlpha = 1; ctx.restore();
}

/* ══════════════════════════════════════════════════════
   VIRTUAL BACKGROUNDS  (drawn under the user's face)
   These fill the FULL canvas before the face overlay.
   bg_beach · bg_city · bg_space · bg_forest · bg_neon
═══════════════════════════════════════════════════════ */
function drawBackground_beach(ctx, W, H) {
    // Sky gradient
    const sky = ctx.createLinearGradient(0, 0, 0, H * 0.55);
    sky.addColorStop(0, '#1e90ff'); sky.addColorStop(1, '#87ceeb');
    ctx.fillStyle = sky; ctx.fillRect(0, 0, W, H * 0.55);
    // Sun
    ctx.save(); ctx.beginPath(); ctx.arc(W * 0.82, H * 0.12, 36, 0, Math.PI * 2);
    ctx.fillStyle = '#FFE03D'; ctx.fill();
    ctx.shadowColor = '#FFE03D'; ctx.shadowBlur = 30; ctx.fill(); ctx.restore();
    // Sea
    const sea = ctx.createLinearGradient(0, H * 0.55, 0, H * 0.72);
    sea.addColorStop(0, '#006994'); sea.addColorStop(1, '#0099bb');
    ctx.fillStyle = sea; ctx.fillRect(0, H * 0.55, W, H * 0.18);
    // Waves
    ctx.strokeStyle = 'rgba(255,255,255,0.45)'; ctx.lineWidth = 2;
    for (let i = 0; i < 4; i++) {
        const wy = H * (0.57 + i * 0.03);
        ctx.beginPath(); ctx.moveTo(0, wy);
        for (let x = 0; x < W; x += 30) ctx.sineTo ? 0 : ctx.quadraticCurveTo(x + 15, wy - 4, x + 30, wy);
        ctx.stroke();
    }
    // Sand
    const sand = ctx.createLinearGradient(0, H * 0.72, 0, H);
    sand.addColorStop(0, '#f0c060'); sand.addColorStop(1, '#d4a017');
    ctx.fillStyle = sand; ctx.fillRect(0, H * 0.72, W, H * 0.28);
    // Animated palm leaf hint
    ctx.save(); ctx.translate(W * 0.05, H * 0.7); ctx.rotate(-0.2 + Math.sin(_t) * 0.05);
    ctx.fillStyle = '#2d7a22'; ctx.font = `${80}px serif`; ctx.fillText('🌴', 0, 0);
    ctx.restore();
}

function drawBackground_city(ctx, W, H) {
    // Night sky
    const sky = ctx.createLinearGradient(0, 0, 0, H * 0.55);
    sky.addColorStop(0, '#0a0014'); sky.addColorStop(1, '#190028');
    ctx.fillStyle = sky; ctx.fillRect(0, 0, W, H);
    // Stars
    for (let i = 0; i < 60; i++) {
        const sx = (i * 137.5) % W, sy = (i * 67) % (H * 0.5);
        ctx.fillStyle = `rgba(255,255,255,${0.4 + 0.6 * Math.sin(_t * 2 + i)})`;
        ctx.fillRect(sx, sy, 1.5, 1.5);
    }
    // Buildings silhouette
    const buildColors = ['#1a0030', '#200040', '#150025'];
    const buildings = [[0, 0.45, 0.18, 0.55], [0.12, 0.35, 0.14, 0.65], [0.22, 0.4, 0.12, 0.6], [0.32, 0.3, 0.16, 0.7],
    [0.45, 0.38, 0.1, 0.62], [0.52, 0.28, 0.18, 0.72], [0.68, 0.35, 0.12, 0.65], [0.78, 0.42, 0.16, 0.58], [0.9, 0.36, 0.14, 0.64]];
    buildings.forEach(([bx, by, bw, bh], i) => {
        ctx.fillStyle = buildColors[i % 3];
        ctx.fillRect(bx * W, by * H, bw * W, bh * H);
        // windows
        ctx.fillStyle = `rgba(255,200,50,${0.3 + 0.4 * ((i * 3 + Math.floor(_t)) % 3 === 0 ? 1 : 0.3)})`;
        for (let r = 0; r < 4; r++) for (let c = 0; c < 3; c++) {
            ctx.fillRect((bx + 0.01 + c * bw / 3.5) * W, (by + 0.03 + r * bh / 5.5) * H, 4, 5);
        }
    });
    // Purple ground glow
    const glow = ctx.createLinearGradient(0, H * 0.7, 0, H);
    glow.addColorStop(0, 'rgba(100,0,200,0.4)'); glow.addColorStop(1, 'rgba(60,0,120,0.7)');
    ctx.fillStyle = glow; ctx.fillRect(0, H * 0.7, W, H * 0.3);
}

function drawBackground_space(ctx, W, H) {
    // Deep space
    ctx.fillStyle = '#000010'; ctx.fillRect(0, 0, W, H);
    // Stars
    for (let i = 0; i < 120; i++) {
        const sx = (i * 97.3) % W, sy = (i * 53.7) % H;
        const br = 0.3 + 0.7 * Math.sin(_t * 1.5 + i * 0.5);
        ctx.fillStyle = `rgba(255,255,255,${br})`;
        ctx.fillRect(sx, sy, i % 5 === 0 ? 2 : 1, i % 5 === 0 ? 2 : 1);
    }
    // Nebula 1
    const neb1 = ctx.createRadialGradient(W * 0.2, H * 0.25, 0, W * 0.2, H * 0.25, W * 0.35);
    neb1.addColorStop(0, 'rgba(120,0,200,0.22)'); neb1.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = neb1; ctx.fillRect(0, 0, W, H);
    // Nebula 2
    const neb2 = ctx.createRadialGradient(W * 0.8, H * 0.6, 0, W * 0.8, H * 0.6, W * 0.3);
    neb2.addColorStop(0, 'rgba(0,80,200,0.2)'); neb2.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = neb2; ctx.fillRect(0, 0, W, H);
    // Animated planet
    const px = W * 0.82, py = H * 0.18, pr = 45;
    ctx.save(); ctx.beginPath(); ctx.arc(px, py, pr, 0, Math.PI * 2);
    const pg = ctx.createRadialGradient(px - pr * 0.3, py - pr * 0.3, 0, px, py, pr);
    pg.addColorStop(0, '#ff6600'); pg.addColorStop(1, '#cc2200');
    ctx.fillStyle = pg; ctx.fill();
    // ring
    ctx.beginPath(); ctx.ellipse(px, py, pr * 1.8, pr * 0.35, 0.3, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(255,150,50,0.5)'; ctx.lineWidth = 4; ctx.stroke();
    ctx.restore();
}

function drawBackground_forest(ctx, W, H) {
    // Gradient sky
    const sky = ctx.createLinearGradient(0, 0, 0, H * 0.4);
    sky.addColorStop(0, '#87ceeb'); sky.addColorStop(1, '#c8e8a0');
    ctx.fillStyle = sky; ctx.fillRect(0, 0, W, H * 0.4);
    // Ground
    const gr = ctx.createLinearGradient(0, H * 0.4, 0, H);
    gr.addColorStop(0, '#3d7a2d'); gr.addColorStop(1, '#1a4a0d');
    ctx.fillStyle = gr; ctx.fillRect(0, H * 0.4, W, H * 0.6);
    // Trees (emoji)
    const treePos = [0.05, 0.18, 0.75, 0.88];
    const treeSize = [90, 110, 100, 85];
    const swayAng = Math.sin(_t * 0.8) * 0.04;
    treePos.forEach((tx, i) => {
        ctx.save(); ctx.translate(tx * W, H * 0.42);
        ctx.rotate(swayAng * (i % 2 === 0 ? 1 : -1));
        ctx.font = `${treeSize[i]}px serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
        ctx.fillText('🌲', 0, 0); ctx.restore();
    });
    // Floating particles (fireflies)
    ctx.fillStyle = `rgba(255,255,100,${0.6 + 0.4 * Math.sin(_t * 3)})`;
    for (let i = 0; i < 8; i++) {
        const fx = W * (0.1 + 0.8 * ((i * 0.137 + _t * 0.02) % 1));
        const fy = H * (0.45 + 0.4 * ((i * 0.263 + _t * 0.015) % 1));
        ctx.beginPath(); ctx.arc(fx, fy, 3, 0, Math.PI * 2); ctx.fill();
    }
}

function drawBackground_neon(ctx, W, H) {
    // Dark bg
    ctx.fillStyle = '#080010'; ctx.fillRect(0, 0, W, H);
    // Grid lines
    ctx.strokeStyle = 'rgba(255,0,255,0.18)'; ctx.lineWidth = 1;
    for (let x = 0; x < W; x += 40) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    }
    for (let y = 0; y < H; y += 40) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }
    // Neon circles (animated)
    [[W * 0.15, H * 0.3, 80], [W * 0.85, H * 0.7, 65], [W * 0.5, H * 0.15, 50]].forEach(([cx, cy, cr], i) => {
        const a = 0.5 + 0.5 * Math.sin(_t * 2 + i);
        ctx.save();
        ctx.shadowColor = ['#ff00ff', '#00ffff', '#ffff00'][i];
        ctx.shadowBlur = 20;
        ctx.strokeStyle = `rgba(${['255,0,255', '0,255,255', '255,255,0'][i]},${a})`;
        ctx.lineWidth = 3;
        ctx.beginPath(); ctx.arc(cx, cy, cr + Math.sin(_t * 3 + i) * 8, 0, Math.PI * 2); ctx.stroke();
        ctx.restore();
    });
    // Ground reflection
    const gnd = ctx.createLinearGradient(0, H * 0.7, 0, H);
    gnd.addColorStop(0, 'rgba(255,0,255,0.15)'); gnd.addColorStop(1, 'rgba(0,255,255,0.08)');
    ctx.fillStyle = gnd; ctx.fillRect(0, H * 0.7, W, H * 0.3);
}

/* ─── Background renderer map ─────────────────────────── */
const _bgMap = {
    bg_beach: drawBackground_beach,
    bg_city: drawBackground_city,
    bg_space: drawBackground_space,
    bg_forest: drawBackground_forest,
    bg_neon: drawBackground_neon,
};

/* ─── Lens Registry ─────────────────────────────────── */
window.ARLenses = {
    _faceMap: {
        dog: renderDog,
        cat: renderCat,
        sunglasses: renderGlasses,
        heart_crown: renderCrown,
        sparkles: renderSparkles,
        beauty: renderBeauty,
        rainbow: renderRainbow,
        cyborg: renderCyborg,
        fire: renderFire,
        astronaut: renderAstronaut,
    },

    render(id, face, canvas, ctx) {
        _t += 0.016;

        // Background lenses: draw full-canvas background first
        if (_bgMap[id]) {
            _bgMap[id](ctx, canvas.width, canvas.height);
            // Then draw face dot to indicate working (no segmentation)
            return;
        }

        // Face lenses
        const fn = this._faceMap[id];
        if (fn) { ctx.save(); fn(face, canvas, ctx); ctx.restore(); }
        _ps.tick(ctx);
    },

    reset() { _t = 0; _ps.clear(); }
};
