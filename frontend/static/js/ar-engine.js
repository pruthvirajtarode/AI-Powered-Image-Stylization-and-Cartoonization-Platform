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
        this._maskCanvas = null;
        this._maskCtx = null;
        this._refinedMaskCanvas = null;
        this._refinedMaskCtx = null;
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
        this._recCanvas = null;
        this._recCtx = null;

        // Snapshot of current video frame captured before any async work
        this._videoSnap = null;
        this._videoSnapCtx = null;

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
            // modelSelection: 0 is tuned for close selfie subjects and cleaner face boundaries.
            this.segmenter.setOptions({ modelSelection: 0 });
            this.segmenter.onResults(this._onSegResults);
            await this.segmenter.initialize();
            const W = this.video.videoWidth || 640;
            const H = this.video.videoHeight || 480;
            this._tmpCanvas = document.createElement('canvas');
            this._tmpCanvas.width = W; this._tmpCanvas.height = H;
            this._tmpCtx = this._tmpCanvas.getContext('2d');
            this._maskCanvas = document.createElement('canvas');
            this._maskCanvas.width = W; this._maskCanvas.height = H;
            this._maskCtx = this._maskCanvas.getContext('2d', { willReadFrequently: true });
            this._refinedMaskCanvas = document.createElement('canvas');
            this._refinedMaskCanvas.width = W; this._refinedMaskCanvas.height = H;
            this._refinedMaskCtx = this._refinedMaskCanvas.getContext('2d');
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

    _getCompositeSourceFrame() {
        if (this.video && this.video.readyState >= 2) return this.video;
        return this._videoSnap || null;
    }

    _getRefinedSegMask(W, H) {
        if (!this.segMask || !this._maskCanvas || !this._maskCtx || !this._refinedMaskCanvas || !this._refinedMaskCtx) {
            return this.segMask || null;
        }

        if (this._maskCanvas.width !== W || this._maskCanvas.height !== H) {
            this._maskCanvas.width = W; this._maskCanvas.height = H;
            this._refinedMaskCanvas.width = W; this._refinedMaskCanvas.height = H;
        }

        this._maskCtx.clearRect(0, 0, W, H);
        this._maskCtx.drawImage(this.segMask, 0, 0, W, H);

        const img = this._maskCtx.getImageData(0, 0, W, H);
        const px = img.data;

        // Confidence remap: removes halo noise and keeps face/body opaque.
        for (let i = 0; i < px.length; i += 4) {
            const m = px[i];
            let a = 0;
            if (m >= 168) a = 255;
            else if (m > 96) a = ((m - 96) * 255) / 72;
            px[i] = 255;
            px[i + 1] = 255;
            px[i + 2] = 255;
            px[i + 3] = a;
        }
        this._maskCtx.putImageData(img, 0, 0);

        this._refinedMaskCtx.clearRect(0, 0, W, H);
        this._refinedMaskCtx.filter = 'blur(2px)';
        this._refinedMaskCtx.drawImage(this._maskCanvas, 0, 0, W, H);
        this._refinedMaskCtx.filter = 'none';

        return this._refinedMaskCanvas;
    }

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
            if (this._maskCanvas) { this._maskCanvas.width = W; this._maskCanvas.height = H; }
            if (this._refinedMaskCanvas) { this._refinedMaskCanvas.width = W; this._refinedMaskCanvas.height = H; }
        }

        // ── Snapshot NOW before any await — GPU frame guaranteed readable here ──
        if (this.video.readyState >= 2 && W > 0) {
            if (!this._videoSnap || this._videoSnap.width !== W) {
                this._videoSnap = document.createElement('canvas');
                this._videoSnap.width = W; this._videoSnap.height = H;
                this._videoSnapCtx = this._videoSnap.getContext('2d');
            }
            this._videoSnapCtx.drawImage(this.video, 0, 0, W, H);
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
                // Use live frame when available; fallback to last readable snapshot.
                const srcFrame = this._getCompositeSourceFrame();
                if (srcFrame) this._tmpCtx.drawImage(srcFrame, 0, 0, this._tmpCanvas.width, this._tmpCanvas.height);
                // Mask out background → only person pixels remain
                this._tmpCtx.save();
                this._tmpCtx.globalCompositeOperation = 'destination-in';
                const refinedMask = this._getRefinedSegMask(this._tmpCanvas.width, this._tmpCanvas.height);
                if (refinedMask) this._tmpCtx.drawImage(refinedMask, 0, 0, this._tmpCanvas.width, this._tmpCanvas.height);
                this._tmpCtx.restore();
                // Composite person over background
                this.ctx.drawImage(this._tmpCanvas, 0, 0);

            } else {
                /* ── Fallback: blend background at low opacity over live video ── */
                // Show the real video so person is always visible
                const snapFb = this._getCompositeSourceFrame();
                if (snapFb) this.ctx.drawImage(snapFb, 0, 0, this.canvas.width, this.canvas.height);

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

        // ── Recording composite — uses pre-snapped frame so pixels are always readable ──
        if (this.isRecording && this._recCanvas && this._recCtx) {
            // Keep rec canvas dims in sync with live video
            if (this._recCanvas.width !== W || this._recCanvas.height !== H) {
                this._recCanvas.width = W; this._recCanvas.height = H;
            }
            this._recCtx.clearRect(0, 0, W, H);
            this._recCtx.save();
            this._recCtx.scale(-1, 1); // mirror for front-camera selfie output
            const recSrc = this._getCompositeSourceFrame();
            if (isBgLens) {
                // canvas already has full composite (bg + segmented person)
                this._recCtx.drawImage(this.canvas, -W, 0);
            } else {
                // draw snapped video frame first, then AR overlay on top
                if (recSrc) this._recCtx.drawImage(recSrc, -W, 0, W, H);
                if (this.activeLens !== 'none') {
                    this._recCtx.drawImage(this.canvas, -W, 0);
                }
            }
            this._recCtx.restore();
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
        this.isRecording = false;
        if (this.animFrame) { cancelAnimationFrame(this.animFrame); this.animFrame = null; }
        this.smoothedFaces = [];
        this.segMask = null;
        this._recCanvas = null;
        this._recCtx = null;
        this._videoSnap = null;
        this._videoSnapCtx = null;
        this._maskCanvas = null;
        this._maskCtx = null;
        this._refinedMaskCanvas = null;
        this._refinedMaskCtx = null;
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
        const mirror = facingMode === 'user'; // only front camera needs mirror
        const src = this._getCompositeSourceFrame() || this.video;

        oc2.save();
        if (mirror) { oc2.scale(-1, 1); }
        const dx = mirror ? -oc.width : 0;

        if (isBg) {
            // canvas already has full composite (background + segmented person)
            oc2.drawImage(this.canvas, dx, 0);
        } else {
            // face/no lens: draw video first, then AR overlay on top
            oc2.drawImage(src, dx, 0, oc.width, oc.height);
            if (this.activeLens !== 'none') {
                oc2.drawImage(this.canvas, dx, 0);
            }
        }
        oc2.restore();
        oc.toBlob(callback, 'image/jpeg', 0.95);
    }

    /* ── Recording ──────────────────────────────────── */
    startRecording() {
        const W = this.video.videoWidth || this.canvas.width || 640;
        const H = this.video.videoHeight || this.canvas.height || 480;
        this._recCanvas = document.createElement('canvas');
        this._recCanvas.width = W;
        this._recCanvas.height = H;
        this._recCtx = this._recCanvas.getContext('2d');
        this.recordedChunks = [];

        const mime = MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' : 'video/webm';
        this.mediaRecorder = new MediaRecorder(this._recCanvas.captureStream(30), { mimeType: mime });
        this.mediaRecorder.ondataavailable = e => { if (e.data.size > 0) this.recordedChunks.push(e.data); };
        this.mediaRecorder.start(100);
        this.isRecording = true;
    }

    stopRecording() {
        return new Promise(resolve => {
            this.mediaRecorder.onstop = () => {
                this.isRecording = false;
                resolve(new Blob(this.recordedChunks, { type: 'video/webm' }));
            };
            this.mediaRecorder.stop();
        });
    }
}
