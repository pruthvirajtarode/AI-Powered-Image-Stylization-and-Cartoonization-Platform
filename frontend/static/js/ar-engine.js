/**
 * ╔══════════════════════════════════════════════════════╗
 * ║  Toonify AR Engine v2.1 — Fixed faceScale            ║
 * ║  MediaPipe Face Mesh · EMA smooth · Multi-face       ║
 * ╚══════════════════════════════════════════════════════╝
 */

class AREngine {
    constructor(videoEl, canvasEl) {
        this.video = videoEl;
        this.canvas = canvasEl;
        this.ctx = canvasEl.getContext('2d');

        this.isRunning = false;
        this.faceMesh = null;
        this.animFrame = null;
        this.smoothedFaces = [];
        this.activeLens = 'none';
        this.smoothAlpha = 0.45;

        // FPS
        this.fps = 0;
        this._fpsCount = 0;
        this._fpsTimer = performance.now();

        // Recording
        this.isRecording = false;
        this.mediaRecorder = null;
        this.recordedChunks = [];
        this._recordAF = null;

        this._onResults = this._onResults.bind(this);
        this._loop = this._loop.bind(this);
    }

    /* ── Init MediaPipe ─────────────────────────────── */
    async init() {
        this.faceMesh = new FaceMesh({
            locateFile: f => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${f}`
        });
        this.faceMesh.setOptions({
            maxNumFaces: 2,
            refineLandmarks: true,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        });
        this.faceMesh.onResults(this._onResults);
        await this.faceMesh.initialize();
    }

    /* ── MediaPipe callback ─────────────────────────── */
    _onResults(results) {
        const rawFaces = results.multiFaceLandmarks || [];
        const W = this.canvas.width || 640;
        const H = this.canvas.height || 480;

        if (!rawFaces.length) { this.smoothedFaces = []; return; }

        this.smoothedFaces = rawFaces.map((raw, fi) => {
            const prev = this.smoothedFaces[fi];
            const a = this.smoothAlpha;

            const sm = raw.map((lm, i) => {
                if (!prev) return { x: lm.x * W, y: lm.y * H, z: lm.z };
                return {
                    x: a * lm.x * W + (1 - a) * prev.raw[i].x,
                    y: a * lm.y * H + (1 - a) * prev.raw[i].y,
                    z: a * lm.z + (1 - a) * prev.raw[i].z,
                };
            });

            const sp = i => sm[i];

            // Key landmarks
            const leftTemple = sp(234);
            const rightTemple = sp(454);
            const forehead = sp(10);   // very top of head region
            const chin = sp(152);
            const noseTip = sp(4);
            const center = sp(168);  // between-eyes midpoint
            const leftEyeCorner = sp(33);   // outer left eye corner
            const rightEyeCorner = sp(263);  // outer right eye corner
            const leftEye = sm.length > 468 ? sp(468) : sp(133);  // iris
            const rightEye = sm.length > 473 ? sp(473) : sp(362);  // iris
            const mouthLeft = sp(61);
            const mouthRight = sp(291);
            const upperLip = sp(13);
            const lowerLip = sp(14);

            // ── faceScale using EYE-CORNER distance (most stable) ──
            // Normalise so inter-eye-corner ≈ 140px → faceScale = 1.0
            const eyeDist = Math.hypot(
                leftEyeCorner.x - rightEyeCorner.x,
                leftEyeCorner.y - rightEyeCorner.y
            );
            const faceScale = Math.max(eyeDist / 140, 0.25);

            // Temple span (for wider crowns / rainbow)
            const templeSpan = Math.hypot(
                leftTemple.x - rightTemple.x,
                leftTemple.y - rightTemple.y
            );

            // Head roll from eye corners
            const roll = Math.atan2(
                rightEyeCorner.y - leftEyeCorner.y,
                rightEyeCorner.x - leftEyeCorner.x
            );

            // Mouth openness
            const mouthH = Math.hypot(upperLip.x - lowerLip.x, upperLip.y - lowerLip.y);
            const mouthW = Math.hypot(mouthLeft.x - mouthRight.x, mouthLeft.y - mouthRight.y);
            const mouthOpen = (mouthH / Math.max(mouthW, 1)) > 0.25;

            // Blink
            const leftBlink = this._ear(sm, 159, 145, 33, 133) < 0.18;
            const rightBlink = this._ear(sm, 386, 374, 362, 263) < 0.18;

            return {
                raw: sm,
                faceScale, roll, eyeDist, templeSpan,
                center, forehead, chin, noseTip,
                leftTemple, rightTemple,
                leftEyeCorner, rightEyeCorner,
                leftEye, rightEye,
                mouthOpen,
                mouthCenter: {
                    x: (mouthLeft.x + mouthRight.x) / 2,
                    y: (upperLip.y + lowerLip.y) / 2,
                },
                leftBlink, rightBlink,
            };
        });
    }

    _ear(sm, t, b, l, r) {
        const v = Math.hypot(sm[t].x - sm[b].x, sm[t].y - sm[b].y);
        const h = Math.hypot(sm[l].x - sm[r].x, sm[l].y - sm[r].y);
        return v / Math.max(h, 1);
    }

    /* ── rAF render loop ────────────────────────────── */
    async _loop() {
        if (!this.isRunning) return;

        // Auto-resize
        if (this.video.videoWidth > 0 && this.canvas.width !== this.video.videoWidth) {
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
        }

        // Send frame to FaceMesh
        if (this.video.readyState >= 2 && this.faceMesh) {
            try { await this.faceMesh.send({ image: this.video }); } catch (_) { }
        }

        // Render
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        if (this.activeLens !== 'none' && window.ARLenses) {
            this.smoothedFaces.forEach(face => {
                window.ARLenses.render(this.activeLens, face, this.canvas, this.ctx);
            });
        }

        // FPS
        this._fpsCount++;
        const now = performance.now();
        if (now - this._fpsTimer >= 1000) {
            this.fps = this._fpsCount; this._fpsCount = 0; this._fpsTimer = now;
            const fpsEl = document.getElementById('arFpsCounter');
            const faceEl = document.getElementById('arFaceCount');
            const n = this.smoothedFaces.length;
            if (fpsEl) fpsEl.textContent = `${this.fps} FPS`;
            if (faceEl) faceEl.textContent = `${n} face${n !== 1 ? 's' : ''}`;
        }

        this.animFrame = requestAnimationFrame(this._loop);
    }

    async start() {
        if (!this.faceMesh) await this.init();
        this.isRunning = true;
        this._loop();
    }

    stop() {
        this.isRunning = false;
        if (this.animFrame) { cancelAnimationFrame(this.animFrame); this.animFrame = null; }
        this.smoothedFaces = [];
        if (window.ARLenses) window.ARLenses.reset();
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    setLens(id) {
        this.activeLens = id;
        if (window.ARLenses) window.ARLenses.reset();
    }

    /* ── Capture ────────────────────────────────────── */
    captureFrame(facingMode, callback) {
        const oc = document.createElement('canvas');
        oc.width = this.video.videoWidth;
        oc.height = this.video.videoHeight;
        const octx = oc.getContext('2d');

        if (facingMode === 'user') {
            octx.save(); octx.scale(-1, 1);
            octx.drawImage(this.video, -oc.width, 0);
            if (this.activeLens !== 'none') octx.drawImage(this.canvas, -oc.width, 0);
            octx.restore();
        } else {
            octx.drawImage(this.video, 0, 0);
            if (this.activeLens !== 'none') octx.drawImage(this.canvas, 0, 0);
        }
        oc.toBlob(callback, 'image/jpeg', 0.95);
    }

    /* ── Recording ──────────────────────────────────── */
    startRecording(facingMode) {
        const rc = document.createElement('canvas');
        rc.width = this.video.videoWidth;
        rc.height = this.video.videoHeight;
        const rctx = rc.getContext('2d');
        this.recordedChunks = [];

        const draw = () => {
            if (!this.isRecording) return;
            if (facingMode === 'user') {
                rctx.save(); rctx.scale(-1, 1);
                rctx.drawImage(this.video, -rc.width, 0);
                if (this.activeLens !== 'none') rctx.drawImage(this.canvas, -rc.width, 0);
                rctx.restore();
            } else {
                rctx.drawImage(this.video, 0, 0);
                if (this.activeLens !== 'none') rctx.drawImage(this.canvas, 0, 0);
            }
            this._recordAF = requestAnimationFrame(draw);
        };

        const mime = MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' : 'video/webm';
        this.mediaRecorder = new MediaRecorder(rc.captureStream(30), { mimeType: mime });
        this.mediaRecorder.ondataavailable = e => { if (e.data.size > 0) this.recordedChunks.push(e.data); };
        this.mediaRecorder.start(100);
        this.isRecording = true;
        draw();
    }

    stopRecording() {
        return new Promise(resolve => {
            this.mediaRecorder.onstop = () => {
                this.isRecording = false;
                if (this._recordAF) { cancelAnimationFrame(this._recordAF); this._recordAF = null; }
                resolve(new Blob(this.recordedChunks, { type: 'video/webm' }));
            };
            this.mediaRecorder.stop();
        });
    }
}
