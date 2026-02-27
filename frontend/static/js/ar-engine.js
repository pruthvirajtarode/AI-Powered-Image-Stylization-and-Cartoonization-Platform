/**
 * ╔══════════════════════════════════════════════════════╗
 * ║  Toonify AR Engine v2.2                             ║
 * ║  Face Mesh + SelfieSegmentation + background swap   ║
 * ╚══════════════════════════════════════════════════════╝
 */

class AREngine {
    constructor(videoEl, canvasEl) {
        this.video = videoEl;
        this.canvas = canvasEl;
        this.ctx = canvasEl.getContext('2d');

        this.isRunning = false;
        this.faceMesh = null;
        this.segmenter = null;     // SelfieSegmentation
        this.segMask = null;     // latest segmentation mask canvas
        this._tmpCanvas = null;     // temp canvas for compositing
        this._tmpCtx = null;
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

    /* ── Init SelfieSegmentation ────────────────────── */
    async initSegmenter() {
        if (this.segmenter) return;
        try {
            this.segmenter = new SelfieSegmentation({
                locateFile: f => `https://cdn.jsdelivr.net/npm/@mediapipe/selfie_segmentation/${f}`
            });
            this.segmenter.setOptions({ modelSelection: 1 }); // 1 = landscape
            this.segmenter.onResults(this._onSegResults);
            await this.segmenter.initialize();

            // Temp canvas for person-only compositing
            this._tmpCanvas = document.createElement('canvas');
            this._tmpCanvas.width = this.video.videoWidth || 640;
            this._tmpCanvas.height = this.video.videoHeight || 480;
            this._tmpCtx = this._tmpCanvas.getContext('2d');
        } catch (e) {
            console.warn('SelfieSegmentation unavailable:', e);
            this.segmenter = null;
        }
    }

    /* ── FaceMesh callback ──────────────────────────── */
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

            const leftTemple = sp(234);
            const rightTemple = sp(454);
            const forehead = sp(10);
            const chin = sp(152);
            const noseTip = sp(4);
            const center = sp(168);
            const leftEyeCorner = sp(33);
            const rightEyeCorner = sp(263);
            const leftEye = sm.length > 468 ? sp(468) : sp(133);
            const rightEye = sm.length > 473 ? sp(473) : sp(362);
            const mouthLeft = sp(61);
            const mouthRight = sp(291);
            const upperLip = sp(13);
            const lowerLip = sp(14);

            const eyeDist = Math.hypot(leftEyeCorner.x - rightEyeCorner.x, leftEyeCorner.y - rightEyeCorner.y);
            const faceScale = Math.max(eyeDist / 140, 0.25);
            const templeSpan = Math.hypot(leftTemple.x - rightTemple.x, leftTemple.y - rightTemple.y);

            const roll = Math.atan2(
                rightEyeCorner.y - leftEyeCorner.y,
                rightEyeCorner.x - leftEyeCorner.x
            );

            const mouthH = Math.hypot(upperLip.x - lowerLip.x, upperLip.y - lowerLip.y);
            const mouthW = Math.hypot(mouthLeft.x - mouthRight.x, mouthLeft.y - mouthRight.y);
            const mouthOpen = (mouthH / Math.max(mouthW, 1)) > 0.25;

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

    /* ── SelfieSegmentation callback ────────────────── */
    _onSegResults(results) {
        this.segMask = results.segmentationMask; // HTMLCanvasElement mask
    }

    _ear(sm, t, b, l, r) {
        const v = Math.hypot(sm[t].x - sm[b].x, sm[t].y - sm[b].y);
        const h = Math.hypot(sm[l].x - sm[r].x, sm[l].y - sm[r].y);
        return v / Math.max(h, 1);
    }

    /* ── Main render loop ───────────────────────────── */
    async _loop() {
        if (!this.isRunning) return;

        const W = this.video.videoWidth || 640;
        const H = this.video.videoHeight || 480;

        // Auto-resize
        if (W > 0 && this.canvas.width !== W) {
            this.canvas.width = W;
            this.canvas.height = H;
            if (this._tmpCanvas) { this._tmpCanvas.width = W; this._tmpCanvas.height = H; }
        }

        const isBgLens = this.activeLens && this.activeLens.startsWith('bg_');

        // Push frame to active model
        if (this.video.readyState >= 2) {
            if (!isBgLens && this.faceMesh) {
                try { await this.faceMesh.send({ image: this.video }); } catch (_) { }
            }
            if (isBgLens) {
                if (!this.segmenter) await this.initSegmenter();
                if (this.segmenter) {
                    try { await this.segmenter.send({ image: this.video }); } catch (_) { }
                }
            }
        }

        // ── Render ──
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        if (isBgLens && window.ARLenses) {
            // 1. Draw animated background scene
            window.ARLenses.renderBg(this.activeLens, this.ctx, this.canvas.width, this.canvas.height);

            // 2. Composite person OVER background using segmentation mask
            if (this.segMask && this._tmpCanvas) {
                // Ensure temp canvas is correctly sized
                if (this._tmpCanvas.width !== this.canvas.width) {
                    this._tmpCanvas.width = this.canvas.width;
                    this._tmpCanvas.height = this.canvas.height;
                }
                // Draw video frame on temp canvas (raw, unmirrored — CSS scaleX(-1) handles mirror)
                this._tmpCtx.clearRect(0, 0, this._tmpCanvas.width, this._tmpCanvas.height);
                this._tmpCtx.drawImage(this.video, 0, 0, this._tmpCanvas.width, this._tmpCanvas.height);

                // Apply segmentation mask — destination-in keeps only where mask is bright (person pixels)
                this._tmpCtx.save();
                this._tmpCtx.globalCompositeOperation = 'destination-in';
                this._tmpCtx.drawImage(this.segMask, 0, 0, this._tmpCanvas.width, this._tmpCanvas.height);
                this._tmpCtx.restore();

                // Draw masked person over background
                this.ctx.drawImage(this._tmpCanvas, 0, 0);
            } else {
                // Segmenter not yet ready → show raw video so user can see themselves
                this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
                // Overlay loading message
                this.ctx.save();
                this.ctx.fillStyle = 'rgba(0,0,0,0.45)';
                this.ctx.fillRect(0, this.canvas.height / 2 - 20, this.canvas.width, 40);
                this.ctx.fillStyle = 'white'; this.ctx.font = '14px sans-serif'; this.ctx.textAlign = 'center';
                this.ctx.fillText('⏳ Loading background model…', this.canvas.width / 2, this.canvas.height / 2 + 5);
                this.ctx.restore();
            }

        } else if (!isBgLens && this.activeLens !== 'none' && window.ARLenses) {
            // Face lens mode — canvas is transparent, video shows through
            this.smoothedFaces.forEach(face => {
                window.ARLenses.render(this.activeLens, face, this.canvas, this.ctx);
            });
        }

        // FPS counter
        this._fpsCount++;
        const now = performance.now();
        if (now - this._fpsTimer >= 1000) {
            this.fps = this._fpsCount; this._fpsCount = 0; this._fpsTimer = now;
            const faceN = this.smoothedFaces.length;
            const fpsEl = document.getElementById('arFpsCounter');
            const faceEl = document.getElementById('arFaceCount');
            if (fpsEl) fpsEl.textContent = `${this.fps} FPS`;
            if (faceEl) faceEl.textContent = `${faceN} face${faceN !== 1 ? 's' : ''}`;
        }

        this.animFrame = requestAnimationFrame(this._loop);
    }

    /* ── Public API ─────────────────────────────────── */
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
        this.segMask = null; // reset mask on lens change
        if (window.ARLenses) window.ARLenses.reset();
    }

    /* ── Capture ────────────────────────────────────── */
    captureFrame(facingMode, callback) {
        const oc = document.createElement('canvas');
        oc.width = this.video.videoWidth; oc.height = this.video.videoHeight;
        const oc2 = oc.getContext('2d');
        const isBg = this.activeLens && this.activeLens.startsWith('bg_');

        if (isBg) {
            // Capture what's on the AR canvas (background + masked person), then mirror it
            if (facingMode === 'user') {
                oc2.save(); oc2.scale(-1, 1); oc2.drawImage(this.canvas, -oc.width, 0); oc2.restore();
            } else {
                oc2.drawImage(this.canvas, 0, 0);
            }
        } else if (facingMode === 'user') {
            oc2.save(); oc2.scale(-1, 1);
            oc2.drawImage(this.video, -oc.width, 0);
            if (this.activeLens !== 'none') oc2.drawImage(this.canvas, -oc.width, 0);
            oc2.restore();
        } else {
            oc2.drawImage(this.video, 0, 0);
            if (this.activeLens !== 'none') oc2.drawImage(this.canvas, 0, 0);
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
            const isBg = this.activeLens && this.activeLens.startsWith('bg_');
            if (isBg) {
                if (facingMode === 'user') {
                    rctx.save(); rctx.scale(-1, 1); rctx.drawImage(this.canvas, -rc.width, 0); rctx.restore();
                } else {
                    rctx.drawImage(this.canvas, 0, 0);
                }
            } else if (facingMode === 'user') {
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
