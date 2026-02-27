/**
 * ╔══════════════════════════════════════════════════════╗
 * ║  Toonify AR Lens Library v2.0                       ║
 * ║  10 modular lens effects using Canvas 2D            ║
 * ╚══════════════════════════════════════════════════════╝
 */

/* ── Particle System ──────────────────────────────────── */
class Particle {
    constructor(x, y, cfg = {}) {
        this.x = x; this.y = y;
        this.vx = (Math.random() - 0.5) * (cfg.speed || 3);
        this.vy = (Math.random() - 0.5) * (cfg.speed || 3) - (cfg.rise || 1.5);
        this.life = 1.0;
        this.decay = 0.012 + Math.random() * 0.018;
        this.size = (cfg.size || 18) * (0.6 + Math.random() * 0.6);
        this.emoji = cfg.emoji || '✨';
        this.angle = Math.random() * Math.PI * 2;
        this.spin = (Math.random() - 0.5) * 0.12;
    }
    update() {
        this.x += this.vx; this.y += this.vy;
        this.vy -= 0.04; this.life -= this.decay; this.angle += this.spin;
    }
    draw(ctx) {
        if (this.life <= 0) return;
        ctx.save();
        ctx.globalAlpha = Math.max(0, this.life);
        ctx.font = `${this.size}px serif`;
        ctx.translate(this.x, this.y); ctx.rotate(this.angle);
        ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText(this.emoji, 0, 0);
        ctx.restore();
    }
    get dead() { return this.life <= 0; }
}

class ParticleSystem {
    constructor(max = 120) { this.pool = []; this.max = max; }
    emit(x, y, n = 1, cfg = {}) {
        for (let i = 0; i < n && this.pool.length < this.max; i++)
            this.pool.push(new Particle(x, y, cfg));
    }
    tick(ctx) {
        this.pool = this.pool.filter(p => { p.update(); p.draw(ctx); return !p.dead; });
    }
    clear() { this.pool = []; }
}

/* ── Shared particle pool (one instance) ─────────────── */
const _ps = new ParticleSystem();
let _time = 0; // global animation timer

/* ── Utility helpers ──────────────────────────────────── */
function emoji(ctx, e, x, y, size, angle = 0) {
    ctx.save();
    ctx.translate(x, y); ctx.rotate(angle);
    ctx.font = `${size}px serif`;
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(e, 0, 0);
    ctx.restore();
}

function roundRect(ctx, x, y, w, h, r, fill, stroke, lw = 3) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y); ctx.arcTo(x + w, y, x + w, y + r, r);
    ctx.lineTo(x + w, y + h - r); ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
    ctx.lineTo(x + r, y + h); ctx.arcTo(x, y + h, x, y + h - r, r);
    ctx.lineTo(x, y + r); ctx.arcTo(x, y, x + r, y, r);
    ctx.closePath();
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); }
}

/* ── DOG LENS ─────────────────────────────────────────── */
function renderDog(face, canvas, ctx, t) {
    const { faceScale: s, roll, forehead, noseTip, leftTemple, rightTemple, mouthOpen, mouthCenter } = face;

    // Ears
    [['left', leftTemple], ['right', rightTemple]].forEach(([side, temple]) => {
        const sign = side === 'left' ? -1 : 1;
        const ew = 80 * s, eh = 100 * s;
        ctx.save();
        ctx.translate(temple.x + sign * ew * 0.05, temple.y - eh * 0.45);
        ctx.rotate(roll + sign * 0.18);
        ctx.beginPath(); ctx.ellipse(0, 0, ew / 2, eh / 2, 0, 0, Math.PI * 2);
        ctx.fillStyle = '#8B4513'; ctx.fill();
        ctx.beginPath(); ctx.ellipse(0, 4, ew / 3.5, eh / 3.5, 0, 0, Math.PI * 2);
        ctx.fillStyle = '#D2691E'; ctx.fill();
        ctx.restore();
    });

    // Dog nose
    ctx.save();
    ctx.translate(noseTip.x, noseTip.y + 5 * s); ctx.rotate(roll);
    const nw = 32 * s, nh = 20 * s;
    ctx.beginPath(); ctx.ellipse(0, 0, nw / 2, nh / 2, 0, 0, Math.PI * 2);
    ctx.fillStyle = '#111'; ctx.fill();
    ctx.beginPath(); ctx.ellipse(-nw * 0.15, -nh * 0.2, nw * 0.12, nh * 0.15, 0, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,255,255,0.45)'; ctx.fill();
    ctx.restore();

    // Cheek blush
    [[face.leftEye.x - 22 * s, face.leftEye.y + 28 * s], [face.rightEye.x + 22 * s, face.rightEye.y + 28 * s]].forEach(([x, y]) => {
        ctx.save();
        const g = ctx.createRadialGradient(x, y, 0, x, y, 22 * s);
        g.addColorStop(0, 'rgba(255,130,130,0.45)'); g.addColorStop(1, 'rgba(255,130,130,0)');
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, 22 * s, 0, Math.PI * 2); ctx.fill();
        ctx.restore();
    });

    // Tongue when mouth open
    if (mouthOpen) {
        const wag = Math.sin(t * 9) * 7;
        const tx = mouthCenter.x, ty = mouthCenter.y + 8 * s;
        const tw = 36 * s, th = 50 * s;
        ctx.save(); ctx.translate(tx + wag, ty);
        ctx.beginPath(); ctx.moveTo(-tw / 2, 0); ctx.quadraticCurveTo(-tw / 2, th, 0, th);
        ctx.quadraticCurveTo(tw / 2, th, tw / 2, 0); ctx.closePath();
        ctx.fillStyle = '#e05570'; ctx.fill();
        ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, th * 0.9);
        ctx.strokeStyle = 'rgba(0,0,0,0.12)'; ctx.lineWidth = 2.5 * s; ctx.stroke();
        ctx.restore();
    }
}

/* ── CAT LENS ─────────────────────────────────────────── */
function renderCat(face, canvas, ctx, t) {
    const { faceScale: s, roll, noseTip, leftTemple, rightTemple, leftEye, rightEye } = face;

    // Ears
    [['left', leftTemple, -1], ['right', rightTemple, 1]].forEach(([side, t2, sign]) => {
        const es = 48 * s;
        ctx.save(); ctx.translate(t2.x + sign * 8 * s, t2.y - 55 * s); ctx.rotate(roll + sign * 0.14);
        ctx.beginPath(); ctx.moveTo(0, -es); ctx.lineTo(es * 0.55, es * 0.3); ctx.lineTo(-es * 0.55, es * 0.3); ctx.closePath();
        ctx.fillStyle = '#2d2d2d'; ctx.fill();
        ctx.beginPath(); ctx.moveTo(0, -es * 0.65); ctx.lineTo(es * 0.28, es * 0.1); ctx.lineTo(-es * 0.28, es * 0.1); ctx.closePath();
        ctx.fillStyle = '#ff9eb5'; ctx.fill();
        ctx.restore();
    });

    // Nose
    emoji(ctx, '🐾', noseTip.x, noseTip.y + 4 * s, 26 * s, roll);

    // Whiskers
    const wag = Math.sin(t * 2) * 3;
    ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.9)'; ctx.lineWidth = 1.5; ctx.lineCap = 'round';
    for (let i = 0; i < 3; i++) {
        const oy = (i - 1) * 10 * s;
        // Left
        ctx.beginPath(); ctx.moveTo(noseTip.x - 12 * s, noseTip.y + oy + wag);
        ctx.lineTo(noseTip.x - 12 * s - 75 * s, noseTip.y + oy - (i - 1) * 6 * s + wag); ctx.stroke();
        // Right
        ctx.beginPath(); ctx.moveTo(noseTip.x + 12 * s, noseTip.y + oy + wag);
        ctx.lineTo(noseTip.x + 12 * s + 75 * s, noseTip.y + oy - (i - 1) * 6 * s + wag); ctx.stroke();
    }
    ctx.restore();

    // Slit pupils glow
    [leftEye, rightEye].forEach(eye => {
        ctx.save();
        ctx.beginPath(); ctx.ellipse(eye.x, eye.y, 3.5 * s, 11 * s, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(50,255,100,0.4)'; ctx.fill();
        ctx.restore();
    });
}

/* ── GLASSES LENS ─────────────────────────────────────── */
function renderGlasses(face, canvas, ctx, t) {
    const { faceScale: s, roll, center, eyeDist } = face;
    const lw = eyeDist * 0.68;
    const lh = lw * 0.6;

    ctx.save();
    ctx.translate(center.x, center.y + 5 * s); ctx.rotate(roll);

    const drawLens = (cx) => {
        roundRect(ctx, cx - lw / 2, -lh / 2, lw, lh, lh * 0.35,
            'rgba(20,20,50,0.55)', '#1a1a1a', 3.5);
        ctx.save();
        ctx.beginPath(); ctx.ellipse(cx - lw * 0.22, -lh * 0.18, lw * 0.1, lh * 0.12, -0.4, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255,255,255,0.3)'; ctx.fill();
        ctx.restore();
    };

    drawLens(-eyeDist / 2);
    drawLens(eyeDist / 2);

    // Bridge
    ctx.beginPath(); ctx.moveTo(-eyeDist / 2 + lw / 2, 0); ctx.lineTo(eyeDist / 2 - lw / 2, 0);
    ctx.strokeStyle = '#111'; ctx.lineWidth = 4 * s; ctx.stroke();

    // Arms
    [[-(eyeDist / 2 + lw / 2), -1], [eyeDist / 2 + lw / 2, 1]].forEach(([bx, d]) => {
        ctx.beginPath(); ctx.moveTo(bx, 0); ctx.lineTo(bx + d * 55 * s, -8 * s);
        ctx.strokeStyle = '#1a1a1a'; ctx.lineWidth = 3.5 * s; ctx.stroke();
    });

    ctx.restore();
}

/* ── CROWN LENS ───────────────────────────────────────── */
function renderCrown(face, canvas, ctx, t) {
    const { faceScale: s, roll, forehead, eyeDist } = face;
    const bob = Math.sin(t * 2.2) * 4;
    const w = eyeDist * 1.85, h = w * 0.58;

    ctx.save();
    ctx.translate(forehead.x, forehead.y + bob); ctx.rotate(roll);

    const x = -w / 2, y = -h * 1.1;

    // Crown gradient fill
    const gr = ctx.createLinearGradient(x, y, x, y + h);
    gr.addColorStop(0, '#FFD700'); gr.addColorStop(0.55, '#FFA500'); gr.addColorStop(1, '#FF8C00');

    ctx.beginPath();
    ctx.moveTo(x, y + h);
    for (let i = 0; i <= 4; i++) {
        const px = x + (i / 4) * w;
        const py = i % 2 === 0 ? y : y + h * 0.52;
        ctx.lineTo(px, py);
    }
    ctx.lineTo(x + w, y + h); ctx.closePath();
    ctx.fillStyle = gr; ctx.fill();
    ctx.strokeStyle = '#b8860b'; ctx.lineWidth = 2.5; ctx.stroke();

    // Jewels
    ['#e74c3c', '#9b59b6', '#3498db', '#e74c3c'].forEach((col, i) => {
        const jx = x + ((i * 2 + 1) / 8) * w;
        const jy = y + h * 0.3 + Math.sin(t * 3 + i) * 2;
        ctx.beginPath(); ctx.arc(jx, jy, 7 * s, 0, Math.PI * 2);
        ctx.fillStyle = col; ctx.fill();
        ctx.strokeStyle = 'rgba(255,255,255,0.55)'; ctx.lineWidth = 1; ctx.stroke();
    });

    ctx.restore();
}

/* ── SPARKLES LENS ────────────────────────────────────── */
function renderSparkles(face, canvas, ctx, t) {
    const { faceScale: s, center } = face;
    const em = ['✨', '💫', '⭐', '🌟'];

    // Emit particles around face
    if (Math.random() < 0.4) {
        const a = Math.random() * Math.PI * 2;
        const r = (80 + Math.random() * 80) * s;
        _ps.emit(center.x + Math.cos(a) * r, center.y + Math.sin(a) * r, 1,
            { emoji: em[Math.floor(Math.random() * 4)], size: 18 * s, speed: 2, rise: 0.8 });
    }

    // Orbiting stars
    ctx.save();
    for (let i = 0; i < 6; i++) {
        const a = t * 1.6 + i * (Math.PI / 3);
        const r = 110 * s;
        ctx.globalAlpha = 0.65 + 0.35 * Math.sin(t * 3 + i);
        emoji(ctx, em[i % 4], center.x + Math.cos(a) * r, center.y + Math.sin(a) * r * 0.38, 26 * s);
    }
    ctx.globalAlpha = 1; ctx.restore();
}

/* ── BEAUTY LENS ──────────────────────────────────────── */
function renderBeauty(face, canvas, ctx, t) {
    const { faceScale: s, center, leftEye, rightEye } = face;

    // Skin glow
    ctx.save();
    const g = ctx.createRadialGradient(center.x, center.y, 0, center.x, center.y, 200 * s);
    g.addColorStop(0, 'rgba(255,200,200,0.18)'); g.addColorStop(1, 'rgba(255,182,193,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(center.x, center.y, 200 * s, 0, Math.PI * 2); ctx.fill();
    ctx.restore();

    // Eye shimmer
    [leftEye, rightEye].forEach((eye, idx) => {
        const g2 = ctx.createRadialGradient(eye.x, eye.y, 0, eye.x, eye.y, 28 * s);
        g2.addColorStop(0, `rgba(255,150,200,${0.28 + 0.1 * Math.sin(t * 4 + idx)})`);
        g2.addColorStop(1, 'rgba(255,150,200,0)');
        ctx.save(); ctx.fillStyle = g2;
        ctx.beginPath(); ctx.arc(eye.x, eye.y, 28 * s, 0, Math.PI * 2); ctx.fill();
        ctx.restore();
    });

    // Cheek roses
    ctx.save(); ctx.globalAlpha = 0.75 + 0.25 * Math.sin(t * 1.5);
    emoji(ctx, '🌸', leftEye.x - 28 * s, leftEye.y + 24 * s, 22 * s);
    emoji(ctx, '🌸', rightEye.x + 28 * s, rightEye.y + 24 * s, 22 * s);
    ctx.globalAlpha = 1; ctx.restore();
}

/* ── RAINBOW LENS ─────────────────────────────────────── */
function renderRainbow(face, canvas, ctx, t) {
    const { faceScale: s, forehead, leftTemple, rightTemple, roll, eyeDist } = face;
    const cx = forehead.x, cy = forehead.y + 15 * s;
    const OR = eyeDist * 1.3, IR = OR * 0.62;

    ctx.save(); ctx.translate(cx, cy); ctx.rotate(roll);
    const colors = ['#FF0000', '#FF7700', '#FFFF00', '#00CC00', '#0077FF', '#8800FF'];
    const bw = (OR - IR) / colors.length;
    colors.forEach((col, i) => {
        const r1 = IR + i * bw, r2 = r1 + bw;
        const pulse = 1 + 0.025 * Math.sin(t * 3 + i * 0.5);
        ctx.beginPath(); ctx.arc(0, 0, r2 * pulse, Math.PI, 0);
        ctx.arc(0, 0, r1 * pulse, 0, Math.PI, true); ctx.closePath();
        ctx.fillStyle = col; ctx.globalAlpha = 0.72; ctx.fill();
    });
    ctx.globalAlpha = 1; ctx.restore();

    emoji(ctx, '☁️', leftTemple.x - 18 * s, leftTemple.y - 55 * s, 36 * s, roll);
    emoji(ctx, '☁️', rightTemple.x + 18 * s, rightTemple.y - 55 * s, 36 * s, roll);
}

/* ── CYBORG LENS ──────────────────────────────────────── */
function renderCyborg(face, canvas, ctx, t) {
    const { faceScale: s, center, leftEye, rightEye, forehead } = face;

    ctx.save();
    // Scanning line
    const scanY = forehead.y + ((t * 120 * s) % (220 * s));
    ctx.fillStyle = `rgba(0,255,200,${0.12 + 0.06 * Math.sin(t * 10)})`;
    ctx.fillRect(center.x - 110 * s, scanY, 220 * s, 3);

    // Face outline
    ctx.strokeStyle = `rgba(0,255,200,${0.22 + 0.1 * Math.sin(t * 5)})`;
    ctx.lineWidth = 1; ctx.setLineDash([4, 7]);
    ctx.beginPath(); ctx.arc(center.x, center.y, 105 * s, 0, Math.PI * 2); ctx.stroke();
    ctx.setLineDash([]);

    // Reticles on eyes
    [leftEye, rightEye].forEach((eye, idx) => {
        ctx.save(); ctx.translate(eye.x, eye.y); ctx.rotate(t * 1.6 + idx * Math.PI);
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
    ctx.fillStyle = `rgba(0,255,200,${0.8 + 0.2 * Math.sin(t * 2)})`;
    ctx.font = `${10 * s}px monospace`; ctx.textAlign = 'left';
    ctx.fillText(`FACE LOCK: 99.${Math.floor(t * 37 % 100).toString().padStart(2, '0')}%`, center.x - 90 * s, forehead.y - 28 * s);
    ctx.fillText('NEURAL: ACTIVE', center.x - 90 * s, forehead.y - 14 * s);
    ctx.restore();
}

/* ── FIRE LENS ────────────────────────────────────────── */
function renderFire(face, canvas, ctx, t) {
    const { faceScale: s, forehead, leftTemple, rightTemple, center } = face;

    // Emit fire particles along hairline
    if (Math.random() < 0.7) {
        const px = leftTemple.x + Math.random() * (rightTemple.x - leftTemple.x);
        _ps.emit(px, forehead.y, 1, {
            emoji: ['🔥', '💥', '✨'][Math.floor(Math.random() * 3)],
            size: (22 + Math.random() * 14) * s, speed: 2.5, rise: 2.5
        });
    }

    // Face glow
    ctx.save();
    const g = ctx.createRadialGradient(center.x, center.y - 15 * s, 0, center.x, center.y, 130 * s);
    g.addColorStop(0, `rgba(255,80,0,${0.1 + 0.06 * Math.sin(t * 8)})`);
    g.addColorStop(1, 'rgba(255,40,0,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(center.x, center.y, 130 * s, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
}

/* ── ASTRONAUT LENS ───────────────────────────────────── */
function renderAstronaut(face, canvas, ctx, t) {
    const { center, faceScale: s, roll, leftTemple, rightTemple } = face;
    const r = Math.hypot(rightTemple.x - leftTemple.x, rightTemple.y - leftTemple.y) * 0.72;

    ctx.save(); ctx.translate(center.x, center.y); ctx.rotate(roll);

    // Helmet shell
    const hg = ctx.createRadialGradient(-r * 0.22, -r * 0.22, r * 0.1, 0, 0, r * 1.22);
    hg.addColorStop(0, 'rgba(210,210,240,0.25)'); hg.addColorStop(1, 'rgba(100,100,150,0.42)');
    ctx.beginPath(); ctx.arc(0, 0, r * 1.18, 0, Math.PI * 2);
    ctx.fillStyle = hg; ctx.fill();
    ctx.strokeStyle = 'rgba(200,200,255,0.65)'; ctx.lineWidth = 5 * s; ctx.stroke();

    // Visor glare
    ctx.beginPath(); ctx.ellipse(-r * 0.3, -r * 0.32, r * 0.23, r * 0.1, -0.5, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,255,255,0.22)'; ctx.fill();

    // Stars in visor
    ctx.globalAlpha = 0.55;
    for (let i = 0; i < 6; i++) {
        const a = t * 0.3 + i * 1.047;
        const sr = r * (0.45 + (i % 3) * 0.14);
        ctx.beginPath(); ctx.arc(Math.cos(a) * sr, Math.sin(a) * sr, 1.8, 0, Math.PI * 2);
        ctx.fillStyle = '#fff'; ctx.fill();
    }
    ctx.globalAlpha = 1; ctx.restore();
}

/* ── LENS REGISTRY ─────────────────────────────────────── */
window.ARLenses = {
    _time: 0,
    _lensMap: {
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
        this._time += 0.016;
        _ps.tick(ctx); // draw + update particles

        const fn = this._lensMap[id];
        if (fn) fn(face, canvas, ctx, this._time);
    },

    reset() {
        this._time = 0;
        _ps.clear();
    }
};
