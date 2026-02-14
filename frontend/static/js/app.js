document.addEventListener('DOMContentLoaded', () => {
    let selectedFile = null;
    let selectedStyle = 'cartoon';

    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');
    const uploadPreview = document.getElementById('uploadPreview');
    const uploadText = document.getElementById('uploadText');
    const processBtn = document.getElementById('processBtn');

    const styleItems = document.querySelectorAll('.style-item');
    const loader = document.getElementById('loader');
    const placeholder = document.getElementById('placeholder');
    const resultView = document.getElementById('resultView');
    const downloadArea = document.getElementById('downloadArea');
    const downloadBtn = document.getElementById('downloadBtn');

    const viewOriginal = document.getElementById('viewOriginal');
    const viewProcessed = document.getElementById('viewProcessed');

    // Handle Download Click
    if (downloadBtn) {
        downloadBtn.onclick = async () => {
            const format = document.getElementById('downloadFormat').value;
            const quality = document.getElementById('downloadQuality').value;
            const filename = window.currentImage;

            if (!filename) return;

            // Check if user is Pro/Admin or has paid
            const user = JSON.parse(localStorage.getItem('toonify_user'));
            if (!user) {
                openAuth();
                return;
            }

            // Simple check (server will double-check)
            // If the user just processed it, they might not have paid yet
            // If they are Admin/Pro, we allow direct download
            if (user.role === 'admin' || user.role === 'pro_member') {
                const url = `/api/user/download?filename=${filename}&format=${format}&quality=${quality}`;
                window.location.href = url;
            } else {
                openPayment(format, quality);
            }
        };
    }

    // SaaS Style Switcher
    styleItems.forEach(item => {
        item.onclick = () => {
            styleItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            selectedStyle = item.dataset.style;
        };
    });

    // Password Visibility Toggle Logic
    document.querySelectorAll('.toggle-password').forEach(icon => {
        icon.onclick = () => {
            const targetId = icon.getAttribute('data-target');
            const input = document.getElementById(targetId);

            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        };
    });

    // Dashboard Upload Trigger (Protected)
    dropZone.onclick = () => {
        const user = JSON.parse(localStorage.getItem('toonify_user'));
        if (!user) {
            openAuth();
        } else {
            fileInput.click();
        }
    };

    fileInput.onchange = (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    };

    dropZone.ondragover = (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#ff7e5f';
        dropZone.style.background = 'rgba(255, 126, 95, 0.1)';
    };
    dropZone.ondragleave = () => {
        dropZone.style.borderColor = '#e2e8f0';
        dropZone.style.background = 'white';
    };
    dropZone.ondrop = (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#e2e8f0';
        dropZone.style.background = 'white';

        const user = JSON.parse(localStorage.getItem('toonify_user'));
        if (!user) {
            openAuth();
            return;
        }

        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    };

    function handleFile(file) {
        selectedFile = file;
        const reader = new FileReader();
        reader.onload = (re) => {
            uploadPreview.src = re.target.result;
            uploadPreview.style.display = 'block';
            uploadText.style.display = 'none';
            processBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    // --- CAMERA CAPTURE FUNCTIONALITY ---
    let cameraStream = null;
    let facingMode = 'user'; // 'user' for front camera, 'environment' for back camera

    const cameraBtn = document.getElementById('cameraBtn');
    const cameraModal = document.getElementById('cameraModal');
    const cameraVideo = document.getElementById('cameraStream');
    const cameraCanvas = document.getElementById('cameraCanvas');
    const captureCameraBtn = document.getElementById('captureCameraBtn');
    const switchCameraBtn = document.getElementById('switchCameraBtn');

    window.openCameraModal = () => {
        const user = JSON.parse(localStorage.getItem('toonify_user'));
        if (!user) {
            openAuth();
            return;
        }

        if (cameraModal) {
            cameraModal.style.display = 'flex';
            setTimeout(startCamera, 300); // Give modal time to render
        }
    };

    window.closeCameraModal = () => {
        if (cameraModal) {
            cameraModal.style.display = 'none';
        }
        stopCamera();
    };

    async function startCamera() {
        try {
            // Stop any existing stream first
            stopCamera();

            const constraints = {
                video: {
                    facingMode: facingMode,
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
            };

            cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
            if (cameraVideo) {
                cameraVideo.srcObject = cameraStream;
                cameraVideo.style.display = 'block';
                cameraVideo.play(); // Ensure video plays
            }
            const permissionDenied = document.getElementById('cameraPermissionDenied');
            if (permissionDenied) {
                permissionDenied.style.display = 'none';
            }
            console.log('✅ Camera started successfully');
        } catch (error) {
            console.error('❌ Camera access denied:', error);
            const permissionDenied = document.getElementById('cameraPermissionDenied');
            if (permissionDenied) {
                permissionDenied.style.display = 'flex';
            }
            if (cameraVideo) {
                cameraVideo.style.display = 'none';
            }
            alert('Camera access denied. Please enable camera permissions in your browser settings.');
        }
    }

    function stopCamera() {
        if (cameraStream) {
            cameraStream.getTracks().forEach(track => track.stop());
            cameraStream = null;
        }
    }

    if (cameraBtn) {
        cameraBtn.onclick = openCameraModal;
    }

    if (captureCameraBtn) {
        captureCameraBtn.onclick = () => {
            if (!cameraVideo || !cameraCanvas) {
                alert('Camera not initialized');
                return;
            }

            try {
                const context = cameraCanvas.getContext('2d');
                cameraCanvas.width = cameraVideo.videoWidth;
                cameraCanvas.height = cameraVideo.videoHeight;

                if (cameraCanvas.width === 0 || cameraCanvas.height === 0) {
                    alert('Camera stream not ready. Please try again.');
                    return;
                }

                // Flip the canvas if using front camera for more natural appearance
                if (facingMode === 'user') {
                    context.scale(-1, 1);
                    context.drawImage(cameraVideo, -cameraCanvas.width, 0);
                } else {
                    context.drawImage(cameraVideo, 0, 0);
                }

                cameraCanvas.toBlob((blob) => {
                    if (!blob) {
                        alert('Failed to capture image');
                        return;
                    }
                    selectedFile = blob;
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        uploadPreview.src = e.target.result;
                        uploadPreview.style.display = 'block';
                        uploadText.style.display = 'none';
                        processBtn.disabled = false;
                    };
                    reader.readAsDataURL(blob);

                    // Close modal after capture
                    closeCameraModal();
                    alert('📸 Photo captured! Ready to transform.');
                }, 'image/jpeg', 0.95);
            } catch (error) {
                console.error('Error capturing image:', error);
                alert('Failed to capture image. Please try again.');
            }
        };
    }

    if (switchCameraBtn) {
        switchCameraBtn.onclick = () => {
            facingMode = facingMode === 'user' ? 'environment' : 'user';
            stopCamera();
            setTimeout(startCamera, 200);
        };
    }

    // --- WHATSAPP INTEGRATION ---
    const whatsappBtn = document.getElementById('whatsappBtn');
    const whatsappModal = document.getElementById('whatsappModal');
    const whatsappLink = document.getElementById('whatsappLink');
    const whatsappFileInput = document.getElementById('whatsappFileInput');

    window.openWhatsappModal = () => {
        const user = JSON.parse(localStorage.getItem('toonify_user'));
        if (!user) {
            openAuth();
            return;
        }

        if (whatsappModal) {
            whatsappModal.style.display = 'flex';
        }

        // Set WhatsApp Business API link (replace with your actual WhatsApp number)
        const phoneNumber = '919356992440'; // Your WhatsApp Business number
        const message = encodeURIComponent('Hi! I want to send a photo to Toonify AI for stylization.');
        if (whatsappLink) {
            whatsappLink.href = `https://wa.me/${phoneNumber}?text=${message}`;
        }
    };

    window.closeWhatsappModal = () => {
        if (whatsappModal) {
            whatsappModal.style.display = 'none';
        }
    };

    // Handle WhatsApp file upload
    if (whatsappFileInput) {
        whatsappFileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                const file = e.target.files[0];

                // Validate file type
                if (!file.type.startsWith('image/')) {
                    alert('❌ Please select a valid image file');
                    return;
                }

                // Validate file size (max 10MB)
                if (file.size > 10 * 1024 * 1024) {
                    alert('❌ File size exceeds 10MB limit');
                    return;
                }

                selectedFile = file;
                const reader = new FileReader();
                reader.onload = (event) => {
                    uploadPreview.src = event.target.result;
                    uploadPreview.style.display = 'block';
                    uploadText.style.display = 'none';
                    processBtn.disabled = false;
                };
                reader.readAsDataURL(file);

                closeWhatsappModal();
                alert('✅ Image imported from WhatsApp! Ready to transform.');
            }
        });
    }

    if (whatsappBtn) {
        whatsappBtn.onclick = openWhatsappModal;
    }

    // WhatsApp drag-and-drop functionality
    const whatsappUploadArea = document.querySelector('[onclick*="whatsappFileInput"]');
    if (whatsappUploadArea) {
        whatsappUploadArea.ondragover = (e) => {
            e.preventDefault();
            whatsappUploadArea.style.borderColor = '#25d366';
            whatsappUploadArea.style.background = 'rgba(37, 211, 102, 0.05)';
        };
        whatsappUploadArea.ondragleave = () => {
            whatsappUploadArea.style.borderColor = '#25d366';
            whatsappUploadArea.style.background = '#f8fafc';
        };
        whatsappUploadArea.ondrop = (e) => {
            e.preventDefault();
            whatsappUploadArea.style.borderColor = '#25d366';
            whatsappUploadArea.style.background = '#f8fafc';

            if (e.dataTransfer.files.length) {
                const file = e.dataTransfer.files[0];
                if (file.type.startsWith('image/')) {
                    whatsappFileInput.files = e.dataTransfer.files;
                    const event = new Event('change', { bubbles: true });
                    whatsappFileInput.dispatchEvent(event);
                } else {
                    alert('❌ Please drop a valid image file');
                }
            }
        };
    }

    // AI SaaS Processing Logic
    processBtn.onclick = async () => {
        if (!selectedFile) return;

        loader.style.display = 'flex';
        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('style', selectedStyle);

        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.success) {
                const filename = data.image_filename;
                window.currentImage = filename;
                const path = `/data/processed/${filename}`;

                // Update Views
                document.getElementById('viewOriginal').src = uploadPreview.src;
                document.getElementById('viewProcessed').src = path;
                document.getElementById('sliderOriginal').src = uploadPreview.src;
                document.getElementById('sliderProcessed').src = path;

                document.getElementById('placeholder').style.display = 'none';
                document.getElementById('resultView').style.display = 'grid';
                document.getElementById('downloadArea').style.display = 'block';

                // Initial Tab Setup
                const tabSide = document.getElementById('tabSideBySide');
                const tabDynamic = document.getElementById('tabDynamic');
                const sideView = document.getElementById('resultView');
                const sliderView = document.getElementById('sliderView');

                tabSide.onclick = () => {
                    tabSide.classList.add('active');
                    tabDynamic.classList.remove('active');
                    sideView.style.display = 'grid';
                    sliderView.style.display = 'none';
                };

                tabDynamic.onclick = () => {
                    tabDynamic.classList.add('active');
                    tabSide.classList.remove('active');
                    sideView.style.display = 'none';
                    sliderView.style.display = 'flex';
                };

                // Slider Interaction
                const slider = document.getElementById('compareSlider');
                const imgAfter = document.querySelector('.img-after');
                const handle = document.querySelector('.slider-handle');

                // Stats Update (Task 13)
                if (data.stats) {
                    document.getElementById('statsPanel').style.display = 'block';
                    document.getElementById('procTimeLabel').innerText = data.proc_time.toFixed(2) + 's';

                    // Original Stats
                    document.getElementById('origBright').innerText = data.stats.original.brightness;
                    document.getElementById('origContrast').innerText = data.stats.original.contrast;

                    const origTotal = data.stats.original.colors.red + data.stats.original.colors.green + data.stats.original.colors.blue;
                    document.getElementById('origR').style.width = (data.stats.original.colors.red / origTotal * 100) + '%';
                    document.getElementById('origG').style.width = (data.stats.original.colors.green / origTotal * 100) + '%';
                    document.getElementById('origB').style.width = (data.stats.original.colors.blue / origTotal * 100) + '%';

                    // Processed Stats
                    document.getElementById('procBright').innerText = data.stats.processed.brightness;
                    document.getElementById('procContrast').innerText = data.stats.processed.contrast;

                    const procTotal = data.stats.processed.colors.red + data.stats.processed.colors.green + data.stats.processed.colors.blue;
                    document.getElementById('procR').style.width = (data.stats.processed.colors.red / procTotal * 100) + '%';
                    document.getElementById('procG').style.width = (data.stats.processed.colors.green / procTotal * 100) + '%';
                    document.getElementById('procB').style.width = (data.stats.processed.colors.blue / procTotal * 100) + '%';
                }

                slider.oninput = () => {
                    const val = slider.value;
                    imgAfter.style.clipPath = `inset(0 0 0 ${val}%)`;
                    handle.style.left = `${val}%`;
                };
            } else {
                alert("Neural Logic Error: " + data.message);
            }
        } catch (error) {
            console.error(error);
            alert("Connection lost during neural stylization.");
        } finally {
            loader.style.display = 'none';
        }
    };

    // --- AUTH LOGIC ---
    window.closeAuth = () => { document.getElementById('authModal').style.display = 'none'; };
    window.toggleAuth = (e, target) => {
        if (e && e.preventDefault) e.preventDefault();
        const login = document.getElementById('loginForm');
        const register = document.getElementById('registerForm');
        const verify = document.getElementById('verifyForm');

        login.style.display = target === 'login' ? 'block' : 'none';
        register.style.display = target === 'register' ? 'block' : 'none';
        verify.style.display = target === 'verify' ? 'block' : 'none';
    };

    window.openAuth = () => {
        document.getElementById('authModal').style.display = 'flex';
        toggleAuth(null, 'login');
    };

    window.handleLogin = async () => {
        const u = document.getElementById('loginUser').value;
        const p = document.getElementById('loginPass').value;
        const btn = document.querySelector('#loginForm .btn-convert') || document.querySelector('.btn-convert');

        if (!u || !p) {
            alert("Please enter both username/email and password.");
            return;
        }

        // Production Feedback
        const originalContent = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Authenticating...';
        btn.disabled = true;

        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: u, password: p })
            });
            const data = await res.json();

            if (data.success) {
                localStorage.setItem('toonify_user', JSON.stringify(data.user));
                if (data.user.role === 'admin') {
                    location.href = '/admin';
                } else {
                    location.href = '/dashboard';
                }
            } else {
                if (data.message === "VERIFY_REQUIRED") {
                    const email = data.user.email;
                    localStorage.setItem('temp_verify_email', email);
                    alert(`🔐 Security Handshake: Please verify your email (${email}) first.`);
                    toggleAuth(null, 'verify');
                } else {
                    alert("⚠️ Access Denied: " + data.message);
                }
            }
        } catch (err) {
            alert("⚠️ Connection Lost: Unable to reach the Neural Engine. Please check your network.");
        } finally {
            btn.innerHTML = originalContent;
            btn.disabled = false;
        }
    };

    // --- PRODUCTION GOOGLE AUTH ---
    async function initGoogleAuth() {
        try {
            const res = await fetch('/api/config');
            const config = await res.json();

            google.accounts.id.initialize({
                client_id: config.google_client_id,
                callback: handleCredentialResponse,
                auto_select: false,
                cancel_on_tap_outside: true
            });

            // Render the official Google Sign-In button
            const btnContainer = document.getElementById('googleBtnContainer');
            if (btnContainer) {
                google.accounts.id.renderButton(btnContainer, {
                    theme: 'outline',
                    size: 'large',
                    width: btnContainer.offsetWidth,
                    text: 'continue_with',
                    shape: 'pill'
                });
            }
            console.log("Google Auth Initialized and Button Rendered.");
        } catch (err) {
            console.error("Neural Handshake Failed: Unable to load Google Config.");
        }
    }
    initGoogleAuth();

    async function handleCredentialResponse(response) {
        // This is the REAL token from Google
        const res = await fetch('/api/auth/google/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: response.credential })
        });
        const data = await res.json();
        if (data.success) {
            localStorage.setItem('toonify_user', JSON.stringify(data.user));
            location.href = '/dashboard';
        } else {
            alert("Google Authentication Failed: " + data.message);
        }
    }


    window.handleRegister = async () => {
        const u = document.getElementById('regUser').value;
        const e = document.getElementById('regEmail').value;
        const p = document.getElementById('regPass').value;
        const cp = document.getElementById('regConfirmPass').value;
        const terms = document.getElementById('regTerms').checked;

        if (!terms) {
            alert("Please agree to the Terms of Service and Privacy Policy.");
            return;
        }

        if (p !== cp) {
            alert("Passwords do not match!");
            return;
        }

        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: u, email: e, password: p, fullname: u })
        });
        const data = await res.json();

        if (data.success) {
            alert(data.message);
            localStorage.setItem('temp_verify_email', e);
            toggleAuth(null, 'verify');
        } else {
            // Check for specific duplicate errors
            if (data.message.includes("exists") || data.message.includes("registered")) {
                const noteEl = data.message.includes("Username") ? document.getElementById('userNote') : document.getElementById('emailNote');
                noteEl.innerHTML = `<i class="fas fa-exclamation-circle" style="color: #ef4444;"></i> ${data.message}`;
                noteEl.style.color = "#ef4444";
            }
            alert(data.message);
        }
    };

    window.handleVerifyEmail = async () => {
        const email = localStorage.getItem('temp_verify_email');
        const codeInput = document.getElementById('verifyCode');
        const code = codeInput ? codeInput.value.replace(/\s+/g, '') : "";

        if (!code || code.length !== 6) {
            alert("Please enter the 6-digit verification code. (Detected: " + code.length + " digits)");
            return;
        }

        if (!email) {
            alert("Verification session not found. Please try logging in again.");
            toggleAuth(null, 'login');
            return;
        }

        const btn = document.querySelector('#verifyForm button');
        const originalText = btn ? btn.innerHTML : "Confirm Verification";
        if (btn) {
            btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Checking...';
            btn.disabled = true;
        }

        try {
            console.log("Attempting Verification Handshake for:", email);
            const res = await fetch('/api/auth/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, code })
            });

            if (!res.ok) {
                const errorText = await res.text();
                console.error("Server Handshake Rejected:", res.status, errorText);
                alert(`⚠️ Server Error (${res.status}): Please contact technical support.`);
                return;
            }

            const data = await res.json();
            if (data.success) {
                alert("✅ Success! Identity verified. You can now log in.");
                localStorage.removeItem('temp_verify_email');
                toggleAuth(null, 'login');
            } else {
                alert("⚠️ Verification Error: " + data.message);
            }
        } catch (err) {
            console.error("Neural Connection Interrupted:", err);
            alert("🚨 Network Handshake Failure: The server is unreachable or blocked. Please ensure backend.py is running on port 5000.");
        } finally {
            if (btn) {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        }
    };

    window.handleResendCode = async () => {
        const email = localStorage.getItem('temp_verify_email');
        if (!email) {
            alert("No email session found. Please try logging in again.");
            toggleAuth(null, 'login');
            return;
        }

        const res = await fetch('/api/auth/resend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await res.json();
        alert(data.message);
    };

    // --- PAYMENT & SUBSCRIPTION LOGIC ---
    window.openPayment = (format = 'jpg', quality = '95') => {
        document.getElementById('paymentModal').style.display = 'flex';
        // Store current format/quality in modal state
        const payBtn = document.getElementById('payBtn');
        payBtn.dataset.format = format;
        payBtn.dataset.quality = quality;
    };
    window.closePayment = () => { document.getElementById('paymentModal').style.display = 'none'; };

    window.processPayment = async () => {
        const payBtn = document.getElementById('payBtn');
        const isUpgrade = payBtn.dataset.type === 'subscription';
        const format = payBtn.dataset.format || 'jpg';
        const quality = payBtn.dataset.quality || '95';

        payBtn.disabled = true;
        payBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Initializing...';

        try {
            // 1. Fetch live config from server
            const configRes = await fetch('/api/config');
            const configData = await configRes.json();

            // 2. Create Order on Server
            const res = await fetch('/api/payment/razorpay/order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    amount: isUpgrade ? 1900 : 299, // INR prices
                    image_filename: window.currentImage
                })
            });
            const data = await res.json();

            if (!data.success) {
                alert("Error initializing payment: " + data.message);
                return;
            }

            const user = JSON.parse(localStorage.getItem('toonify_user'));

            // 3. Open Razorpay Checkout Modal
            const options = {
                "key": configData.razorpay_key,
                "amount": data.order.amount,
                "currency": "INR",
                "name": "Toonify AI",
                "description": isUpgrade ? "Creator Pro Subscription" : "HD Image Export",
                "image": "https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e?auto=format&fit=crop&q=80&w=100&h=100",
                "order_id": data.order.id,
                "handler": async function (response) {
                    // 3. Verify Payment on Server
                    const verifyRes = await fetch('/api/payment/razorpay/verify', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_signature: response.razorpay_signature
                        })
                    });
                    const verifyData = await verifyRes.json();

                    if (verifyData.success) {
                        if (isUpgrade) {
                            alert("🌟 VIP Upgrade Successful! You now have Unlimited 4K Generations.");
                            location.reload();
                        } else {
                            alert("💎 Payment Successful! Starting your high-res download...");
                            const url = `/api/user/download?filename=${window.currentImage}&format=${format}&quality=${quality}`;
                            window.location.href = url;
                        }
                        closePayment();
                    } else {
                        alert("Signature mismatch. Verification failed.");
                    }
                },
                "prefill": {
                    "name": user.username,
                    "email": user.email
                },
                "theme": { "color": "#ff7e5f" }
            };

            const rzp = new Razorpay(options);
            rzp.on('payment.failed', function (response) {
                alert("Payment Failed: " + response.error.description);
            });
            rzp.open();

        } catch (err) {
            console.error(err);
            alert("Unexpected error during checkout.");
        } finally {
            payBtn.disabled = false;
            payBtn.innerHTML = isUpgrade ? 'Confirm Upgrade' : 'Complete Checkout <i class="fas fa-credit-card"></i>';
        }
    };

    window.upgradeToPro = () => {
        const user = JSON.parse(localStorage.getItem('toonify_user'));
        if (!user) {
            openAuth();
            return;
        }

        const modal = document.getElementById('paymentModal');
        const payBtn = document.getElementById('payBtn');
        const modalTitle = modal.querySelector('h2');
        const modalPrice = modal.querySelector('h1');

        modalTitle.innerHTML = 'Upgrade to <span>Creator Pro</span>';
        modalPrice.innerHTML = '$19<span>/mo</span>';
        payBtn.innerHTML = 'Confirm Upgrade <i class="fas fa-rocket"></i>';
        payBtn.dataset.type = 'subscription';

        openPayment();
    };

    window.contactSales = () => {
        alert("🏢 Agency Elite Inquiry Sent! Our enterprise team will contact you within 2 hours to set up your custom neural training cluster.");
    };

    window.showStarterPlan = () => {
        alert("✅ Current Plan: Starter. You have 5 generations remaining today. Upgrade to Pro for unlimited 4K exports!");
    };

    // Update Navbar if logged in
    const user = JSON.parse(localStorage.getItem('toonify_user'));
    const loginBtn = document.getElementById('loginHeaderBtn');
    const profileContainer = document.getElementById('profileDropdownContainer');
    const profileBtn = document.getElementById('profilePillBtn');
    const profileDropdown = document.getElementById('profileDropdown');

    if (user && profileContainer) {
        if (loginBtn) loginBtn.style.display = 'none';
        profileContainer.style.display = 'block';

        profileBtn.innerHTML = `
            <img src="https://images.unsplash.com/photo-1633332755192-727a05c4013d?auto=format&fit=crop&q=80&w=100&h=100" class="profile-avatar" alt="User ${user.username}">
            <span style="font-family: 'Inter';">${user.username}</span>
            <i class="fas fa-chevron-down" style="font-size: 0.7rem; color: #94a3b8; margin-left: auto;"></i>
        `;

        profileBtn.onclick = (e) => {
            console.log("Profile clicked");
            e.stopPropagation();
            if (profileDropdown.style.display === 'none' || profileDropdown.style.display === '') {
                profileDropdown.style.display = 'block';
            } else {
                profileDropdown.style.display = 'none';
            }
        };

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (profileContainer && !profileContainer.contains(e.target)) {
                profileDropdown.style.display = 'none';
            }
        });

        // Add Admin Panel link if admin
        if (user.role === 'admin') {
            const navLinks = document.querySelector('.nav-links');
            if (navLinks && !document.getElementById('adminLink')) {
                const adminLink = document.createElement('a');
                adminLink.id = 'adminLink';
                adminLink.href = '/admin';
                adminLink.innerHTML = '<i class="fas fa-user-shield"></i> Admin Settings';
                adminLink.style.color = '#ff7e5f';
                adminLink.style.fontWeight = '800';
                navLinks.appendChild(adminLink);
            }
        }
    }

    window.handleLogout = async (e) => {
        if (e) e.preventDefault();
        if (confirm("Sign out from Toonify AI Studio?")) {
            localStorage.removeItem('toonify_user');
            await fetch('/api/auth/logout');
            window.location.href = '/';
        }
    };

    // Hero Carousel Rotation (3 seconds)

    // Hero Carousel Rotation (3 seconds)
    const slides = document.querySelectorAll('.hero-slide');
    if (slides.length > 1) {
        let currentSlide = 0;
        setInterval(() => {
            slides[currentSlide].classList.remove('active');
            currentSlide = (currentSlide + 1) % slides.length;
            slides[currentSlide].classList.add('active');
        }, 3000);
    }

    // --- MOBILE MENU LOGIC ---
    const menuToggle = document.getElementById('menuToggle');
    const navLinks = document.querySelector('.nav-links');
    if (menuToggle && navLinks) {
        menuToggle.onclick = () => {
            navLinks.classList.toggle('active');
            const icon = menuToggle.querySelector('i');
            if (navLinks.classList.contains('active')) {
                icon.className = 'fas fa-times';
            } else {
                icon.className = 'fas fa-bars';
            }
        };
        // Close menu on link click
        navLinks.querySelectorAll('a').forEach(link => {
            link.onclick = () => {
                navLinks.classList.remove('active');
                menuToggle.querySelector('i').className = 'fas fa-bars';
            };
        });
    }

    // Gallery Slider Logic (3 seconds)
    const track = document.getElementById('galleryTrack');
    const cards = document.querySelectorAll('.gallery-card');
    if (track && cards.length > 0) {
        let currentIndex = 0;
        const cardWidth = 332; // card width (300) + gap (32)

        const updateSlider = () => {
            const visibleCards = Math.floor(window.innerWidth / cardWidth);
            const maxIndex = Math.max(0, cards.length - visibleCards);

            if (currentIndex > maxIndex) currentIndex = maxIndex;
            track.style.transform = `translateX(-${currentIndex * cardWidth}px)`;
            return maxIndex;
        };

        let maxIdx = updateSlider();
        window.addEventListener('resize', () => {
            maxIdx = updateSlider();
        });

        setInterval(() => {
            currentIndex++;
            if (currentIndex > maxIdx) {
                currentIndex = 0;
            }
            track.style.transform = `translateX(-${currentIndex * cardWidth}px)`;
        }, 3000);
    }

    // --- ELITE LIVE VALIDATION ---
    const regUser = document.getElementById('regUser');
    const regEmail = document.getElementById('regEmail');
    const regPass = document.getElementById('regPass');
    const userNote = document.getElementById('userNote');
    const emailNote = document.getElementById('emailNote');
    const passNote = document.getElementById('passNote');

    if (regUser) {
        regUser.oninput = () => {
            const val = regUser.value;
            if (val === "") {
                userNote.innerHTML = "";
            } else if (/[0-9]/.test(val)) {
                userNote.innerHTML = '<i class="fas fa-times-circle" style="color: #ef4444;"></i> Numbers are not allowed in username';
                userNote.style.color = "#ef4444";
            } else {
                userNote.innerHTML = '<i class="fas fa-check-circle" style="color: #10b981;"></i> Username format valid';
                userNote.style.color = "#10b981";
            }
        };
    }

    if (regEmail) {
        regEmail.oninput = () => {
            const val = regEmail.value.trim();
            // Robust professional email regex
            const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,63}$/;

            // Catch obvious typos for common domains (e.g. gam0il, gmaill, etc.)
            const domainTypos = ['gam0il.com', 'gmaill.com', 'gamil.com', 'yah0o.com', 'hotmial.com'];
            const isTypo = domainTypos.some(typo => val.toLowerCase().endsWith(typo));

            if (val === "") {
                emailNote.innerHTML = "";
            } else if (pattern.test(val) && !isTypo) {
                emailNote.innerHTML = '<i class="fas fa-check-circle" style="color: #10b981;"></i> Valid email format';
                emailNote.style.color = "#10b981";
            } else if (isTypo) {
                emailNote.innerHTML = '<i class="fas fa-exclamation-triangle" style="color: #f59e0b;"></i> Possible typo in domain name';
                emailNote.style.color = "#f59e0b";
            } else {
                emailNote.innerHTML = '<i class="fas fa-times-circle" style="color: #ef4444;"></i> Invalid email format';
                emailNote.style.color = "#ef4444";
            }
        };
    }

    const regConfirmPass = document.getElementById('regConfirmPass');
    const confirmNote = document.getElementById('confirmNote');

    if (regPass) {
        regPass.oninput = () => {
            const val = regPass.value;

            // Requirements checklist
            const reqs = {
                length: val.length >= 8,
                upper: /[A-Z]/.test(val),
                number: /[0-9]/.test(val),
                special: /[!@#$%^&*()]/.test(val)
            };

            // Update UI checklist
            Object.keys(reqs).forEach(key => {
                const el = document.getElementById(`req-${key}`);
                if (el) {
                    if (reqs[key]) {
                        el.style.color = "#10b981";
                        el.querySelector('i').className = "fas fa-check-circle";
                    } else {
                        el.style.color = "var(--slate)";
                        el.querySelector('i').className = "fas fa-circle";
                    }
                }
            });

            // Overall strength
            let strength = Object.values(reqs).filter(Boolean).length;
            let msg = "";

            if (val === "") {
                msg = "";
            } else if (strength < 2) {
                msg = '<i class="fas fa-shield-alt"></i> Strength: Weak';
                passNote.style.color = "#ef4444";
            } else if (strength < 4) {
                msg = '<i class="fas fa-shield-alt"></i> Strength: Medium';
                passNote.style.color = "#f59e0b";
            } else {
                msg = '<i class="fas fa-shield-alt"></i> Strength: Strong';
                passNote.style.color = "#10b981";
            }
            passNote.innerHTML = msg;

            // Trigger confirm check if typing
            if (regConfirmPass.value) regConfirmPass.oninput();
        };
    }

    if (regConfirmPass) {
        regConfirmPass.oninput = () => {
            const val = regConfirmPass.value;
            const pass = regPass.value;

            if (val === "") {
                confirmNote.innerHTML = "";
            } else if (val === pass && pass !== "") {
                confirmNote.innerHTML = '<i class="fas fa-check-circle" style="color: #10b981;"></i> Passwords match';
                confirmNote.style.color = "#10b981";
            } else {
                confirmNote.innerHTML = '<i class="fas fa-times-circle" style="color: #ef4444;"></i> Passwords do not match';
                confirmNote.style.color = "#ef4444";
            }
        };
    }
    // --- SCROLL REVEAL ANIMATION ---
    const revealElements = document.querySelectorAll('.feat-card, .gallery-card, .price-card, .section-title, .hero-content, .hero-visual');

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('reveal-active');
                revealObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15
    });

    revealElements.forEach(el => {
        el.classList.add('reveal-hidden');
        revealObserver.observe(el);
    });
});
