/**
 * ╔══════════════════════════════════════════════════════╗
 * ║  Toonify AR Engine v2.3                             ║
 * ║  Fixed: segmenter init guard · better fallback UX   ║
 * ╚══════════════════════════════════════════════════════╝
 */

class AREngine {
    constructor(videoEl, canvasEl) {
        this.video = videoEl;
        this.canvas = canvasEl;
        this.ctx = canvasEl.getContext('2d');

        this.isRunning = false;
        this.faceMesh = null;
        this.segmenter = null;
        this.segMask = null;
        this._tmpCanvas = null;
        this._tmpCtx = null;
        this._segLoading = false;   // prevents duplicate init calls
        this._segFailed = false;   // stops retrying after hard fail
        this.animFrame = null;
        this.smoothedFaces = [];
        this.activeLens = 'none';
        this.smoothAlpha = 0.45;

        this.fps = 0;
        this._fpsCount = 0;
        this._fpsTimer = performance.now();

        this.isRecording = false;
        this.mediaRecorder = null;
        this.recordedChunks = [];
        this._recordAF = null;

        this._onFaceResults = this._onFaceResults.bind(this);
        this._onSegResults = this._onSegResults.bind(this);
        this._loop = this._loop.bind(this);
    }

    /* ── Init FaceMesh ──────────────────────────────── */
    async initFaceMesh() {
        if (this.faceMesh) return;
        this.faceMesh = new FaceMesh({
            locateFile: f => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${f}`
        });
        this.faceMesh.setOptions({
            maxNumFaces: 2,
            refineLandmarks: true,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        });
        this.faceMesh.onResults(this._onFaceResults);
        await this.faceMesh.initialize();
    }

    /* ── Init SelfieSegmentation (lazy, guarded) ────── */
    async initSegmenter() {
        if (this.segmenter || this._segLoading || this._segFailed) return;
        this._segLoading = true;
        try {
            this.segmenter = new SelfieSegmentation({
                locateFile: f => `https://cdn.jsdelivr.net/npm/@mediapipe/selfie_segmentation/${f}`
            });
            this.segmenter.setOptions({ modelSelection: 1 });
            this.segmenter.onResults(this._onSegResults);
            await this.segmenter.initialize();
            const W = this.video.videoWidth || 640;
            const H = this.video.videoHeight || 480;
            this._tmpCanvas = document.createElement('canvas');
            this._tmpCanvas.width = W; this._tmpCanvas.height = H;
            this._tmpCtx = this._tmpCanvas.getContext('2d');
            this._segLoading = false;
        } catch (e) {
            console.warn('[AREngine] SelfieSegmentation failed:', e);
            this.segmenter = null;
            this._segLoading = false;
            this._segFailed = true;   // do not retry
        }
    }

    /* ── FaceMesh results ───────────────────────────── */
    _onFaceResults(results) {
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
            const leftEyeCorner = sp(33);
            const rightEyeCorner = sp(263);
            const leftTemple = sp(234);
            const rightTemple = sp(454);

            const eyeDist = Math.hypot(leftEyeCorner.x - rightEyeCorner.x, leftEyeCorner.y - rightEyeCorner.y);
            const faceScale = Math.max(eyeDist / 140, 0.25);
            const templeSpan = Math.hypot(leftTemple.x - rightTemple.x, leftTemple.y - rightTemple.y);
            const roll = Math.atan2(rightEyeCorner.y - leftEyeCorner.y, rightEyeCorner.x - leftEyeCorner.x);

            const mouthLeft = sp(61); const mouthRight = sp(291);
            const upperLip = sp(13); const lowerLip = sp(14);
            const mouthH = Math.hypot(upperLip.x - lowerLip.x, upperLip.y - lowerLip.y);
            const mouthW = Math.hypot(mouthLeft.x - mouthRight.x, mouthLeft.y - mouthRight.y);
            const mouthOpen = (mouthH / Math.max(mouthW, 1)) > 0.25;

            const leftEye = sm.length > 468 ? sp(468) : sp(133);
            const rightEye = sm.length > 473 ? sp(473) : sp(362);

            return {
                raw: sm, faceScale, roll, eyeDist, templeSpan,
                center: sp(168), forehead: sp(10), chin: sp(152), noseTip: sp(4),
                leftTemple, rightTemple, leftEyeCorner, rightEyeCorner,
                leftEye, rightEye, mouthOpen,
                mouthCenter: { x: (mouthLeft.x + mouthRight.x) / 2, y: (upperLip.y + lowerLip.y) / 2 },
                leftBlink: this._ear(sm, 159, 145, 33, 133) < 0.18,
                rightBlink: this._ear(sm, 386, 374, 362, 263) < 0.18,
            };
        });
    }

    /* ── Segmentation results ───────────────────────── */
    _onSegResults(r) { this.segMask = r.segmentationMask; }

    _ear(sm, t, b, l, r) {
        return Math.hypot(sm[t].x - sm[b].x, sm[t].y - sm[b].y) /
            Math.max(Math.hypot(sm[l].x - sm[r].x, sm[l].y - sm[r].y), 1);
    }

    /* ── Main render loop ───────────────────────────── */
    async _loop() {
        if (!this.isRunning) return;

        const W = this.video.videoWidth || 640;
        const H = this.video.videoHeight || 480;

        if (W > 0 && this.canvas.width !== W) {
            this.canvas.width = W; this.canvas.height = H;
            if (this._tmpCanvas) { this._tmpCanvas.width = W; this._tmpCanvas.height = H; }
        }

        const isBgLens = this.activeLens && this.activeLens.startsWith('bg_');

        if (this.video.readyState >= 2) {
            if (!isBgLens && this.faceMesh) {
                try { await this.faceMesh.send({ image: this.video }); } catch (_) { }
            }
            if (isBgLens && !this._segLoading && !this._segFailed) {
                if (!this.segmenter) await this.initSegmenter();
                if (this.segmenter) {
                    try { await this.segmenter.send({ image: this.video }); } catch (_) { }
                }
            }
        }

        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        if (isBgLens && window.ARLenses) {
            if (this.segMask && this._tmpCanvas) {
                /* ── Full background replacement (segmentation ready) ── */
                window.ARLenses.renderBg(this.activeLens, this.ctx, this.canvas.width, this.canvas.height);

                if (this._tmpCanvas.width !== this.canvas.width) {
                    this._tmpCanvas.width = this.canvas.width;
                    this._tmpCanvas.height = this.canvas.height;
                }
                this._tmpCtx.clearRect(0, 0, this._tmpCanvas.width, this._tmpCanvas.height);
                // Draw raw video (unmirrored) — CSS scaleX(-1) handles the flip
                this._tmpCtx.drawImage(this.video, 0, 0, this._tmpCanvas.width, this._tmpCanvas.height);
                // Mask out background → only person pixels remain
                this._tmpCtx.save();
                this._tmpCtx.globalCompositeOperation = 'destination-in';
                this._tmpCtx.drawImage(this.segMask, 0, 0, this._tmpCanvas.width, this._tmpCanvas.height);
                this._tmpCtx.restore();
                // Composite person over background
                this.ctx.drawImage(this._tmpCanvas, 0, 0);

            } else {
                /* ── Fallback: blend background at low opacity over live video ── */
                // Show the real video so person is always visible
                this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);

                // Blend the background artistically on top
                this.ctx.save();
                this.ctx.globalAlpha = this._segLoading ? 0.30 : 0.45;
                this.ctx.globalCompositeOperation = 'screen'; // light blend
                window.ARLenses.renderBg(this.activeLens, this.ctx, this.canvas.width, this.canvas.height);
                this.ctx.restore();

                // Show subtle loading badge (top-right corner, not invasive)
                if (this._segLoading) {
                    this.ctx.save();
                    this.ctx.fillStyle = 'rgba(0,0,0,0.55)';
                    this.ctx.beginPath();
                    this.ctx.roundRect ? this.ctx.roundRect(this.canvas.width - 220, 8, 212, 28, 8)
                        : this.ctx.rect(this.canvas.width - 220, 8, 212, 28);
                    this.ctx.fill();
                    this.ctx.fillStyle = 'white'; this.ctx.font = '12px sans-serif'; this.ctx.textAlign = 'center';
                    this.ctx.fillText('⏳ Loading AI background...', this.canvas.width - 114, 27);
                    this.ctx.restore();
                }
            }

        } else if (!isBgLens && this.activeLens !== 'none' && window.ARLenses) {
            this.smoothedFaces.forEach(face => {
                window.ARLenses.render(this.activeLens, face, this.canvas, this.ctx);
            });
        }

        // FPS counter
        this._fpsCount++;
        const now = performance.now();
        if (now - this._fpsTimer >= 1000) {
            this.fps = this._fpsCount; this._fpsCount = 0; this._fpsTimer = now;
            const n = this.smoothedFaces.length;
            const fpsEl = document.getElementById('arFpsCounter');
            const faceEl = document.getElementById('arFaceCount');
            if (fpsEl) fpsEl.textContent = `${this.fps} FPS`;
            if (faceEl) faceEl.textContent = `${n} face${n !== 1 ? 's' : ''}`;
        }

        this.animFrame = requestAnimationFrame(this._loop);
    }

    async start() {
        await this.initFaceMesh();
        this.isRunning = true;
        this._loop();
    }

    stop() {
        this.isRunning = false;
        if (this.animFrame) { cancelAnimationFrame(this.animFrame); this.animFrame = null; }
        this.smoothedFaces = [];
        this.segMask = null;
        if (window.ARLenses) window.ARLenses.reset();
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    setLens(id) {
        this.activeLens = id;
        this.segMask = null;
        if (window.ARLenses) window.ARLenses.reset();
    }

    /* ── Capture ────────────────────────────────────── */
    captureFrame(facingMode, callback) {
        const oc = document.createElement('canvas');
        oc.width = this.video.videoWidth;
        oc.height = this.video.videoHeight;
        const oc2 = oc.getContext('2d');
        const isBg = this.activeLens && this.activeLens.startsWith('bg_');

        if (isBg || facingMode !== 'user') {
            oc2.save(); oc2.scale(-1, 1);
            oc2.drawImage(this.canvas, -oc.width, 0);
            oc2.restore();
        } else {
            oc2.save(); oc2.scale(-1, 1);
            oc2.drawImage(this.video, -oc.width, 0);
            if (this.activeLens !== 'none') oc2.drawImage(this.canvas, -oc.width, 0);
            oc2.restore();
        }
        oc.toBlob(callback, 'image/jpeg', 0.95);
    }

    /* ── Recording ──────────────────────────────────── */
    startRecording(facingMode) {
        const rc = document.createElement('canvas');
        rc.width = this.video.videoWidth; rc.height = this.video.videoHeight;
        const rctx = rc.getContext('2d');
        this.recordedChunks = [];

        const draw = () => {
            if (!this.isRecording) return;
            rctx.save(); rctx.scale(-1, 1);
            rctx.drawImage(this.canvas, -rc.width, 0);
            rctx.restore();
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
