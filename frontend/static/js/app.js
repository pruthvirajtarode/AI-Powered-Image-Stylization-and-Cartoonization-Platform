document.addEventListener('DOMContentLoaded', () => {
    let selectedFile = null;
    let selectedStyle = 'cartoon';
    let batchQueue = [];
    let selectedBatchItemId = null;


    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');
    const uploadPreview = document.getElementById('uploadPreview');
    const uploadText = document.getElementById('uploadText');
    const processBtn = document.getElementById('processBtn');

    // Task 13: Neural Reality Slider Logic
    const compareSlider = document.getElementById('compareSlider');
    const imgAfter = document.querySelector('.img-after');
    const sliderHandle = document.querySelector('.slider-handle');

    if (compareSlider && imgAfter && sliderHandle) {
        compareSlider.oninput = (e) => {
            const value = e.target.value;
            imgAfter.style.width = `${value}%`;
            sliderHandle.style.left = `${value}%`;
        };
    }

    const styleItems = document.querySelectorAll('.style-item');
    const loader = document.getElementById('loader');
    const placeholder = document.getElementById('placeholder');

    if (fileInput) {
        fileInput.onchange = (e) => {
            if (e.target.files.length > 0) handleFile(e.target.files);
        };
    }
    const resultView = document.getElementById('resultView');
    const downloadArea = document.getElementById('downloadArea');
    const downloadBtn = document.getElementById('downloadBtn');

    const viewOriginal = document.getElementById('viewOriginal');
    const viewProcessed = document.getElementById('viewProcessed');

    // Neural View Controls (Task 13)
    const tabSideBySide = document.getElementById('tabSideBySide');
    const tabDynamic = document.getElementById('tabDynamic');
    const sliderView = document.getElementById('sliderView');

    if (tabSideBySide && tabDynamic) {
        tabSideBySide.onclick = () => {
            tabSideBySide.classList.add('active');
            tabDynamic.classList.remove('active');
            if (resultView) resultView.style.display = 'grid';
            if (sliderView) sliderView.style.display = 'none';
        };
        tabDynamic.onclick = () => {
            tabDynamic.classList.add('active');
            tabSideBySide.classList.remove('active');
            if (resultView) resultView.style.display = 'none';
            if (sliderView) sliderView.style.display = 'block';
        };
    }

    // Neural Canvas Crop Box Logic
    const cropBoxView = document.getElementById('cropBoxView');
    const canvasImage = document.getElementById('canvasImage');
    const cropBox = document.getElementById('cropBox');
    const cropOverlay = document.getElementById('cropOverlay');
    const canvasImageWrapper = document.getElementById('canvasImageWrapper');
    
    let cropBoxState = {
        isActive: false,
        cropData: null,
        isDragging: false,
        dragStartX: 0,
        dragStartY: 0,
        dragStartLeft: 0,
        dragStartTop: 0,
        activeHandle: null
    };

    // Initialize crop box events
    if (cropBox && cropOverlay) {
        cropOverlay.onmousedown = (e) => {
            if (!cropBoxState.isActive) {
                // Create new crop box
                const rect = canvasImageWrapper.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                cropBox.style.left = x + 'px';
                cropBox.style.top = y + 'px';
                cropBox.style.width = '150px';
                cropBox.style.height = '150px';
                cropBox.style.display = 'block';
                cropBoxState.isActive = true;
                cropBoxState.isDragging = true;
                cropBoxState.dragStartX = e.clientX;
                cropBoxState.dragStartY = e.clientY;
            }
        };
        
        cropBox.onmousedown = (e) => {
            if (e.target.classList.contains('crop-box-handle')) {
                cropBoxState.activeHandle = e.target.className.split(' ')[1];
                cropBoxState.isDragging = true;
                cropBoxState.dragStartX = e.clientX;
                cropBoxState.dragStartY = e.clientY;
                cropBoxState.dragStartLeft = parseInt(cropBox.style.left);
                cropBoxState.dragStartTop = parseInt(cropBox.style.top);
                e.preventDefault();
            } else {
                // Drag the entire box
                cropBoxState.isDragging = true;
                cropBoxState.dragStartX = e.clientX;
                cropBoxState.dragStartY = e.clientY;
                cropBoxState.dragStartLeft = parseInt(cropBox.style.left);
                cropBoxState.dragStartTop = parseInt(cropBox.style.top);
            }
        };
    }

    document.onmousemove = (e) => {
        if (!cropBoxState.isDragging || !cropBox) return;
        
        const deltaX = e.clientX - cropBoxState.dragStartX;
        const deltaY = e.clientY - cropBoxState.dragStartY;
        
        if (cropBoxState.activeHandle) {
            // Resize operation
            const newWidth = Math.max(50, parseInt(cropBox.style.width || '150') + deltaX);
            const newHeight = Math.max(50, parseInt(cropBox.style.height || '150') + deltaY);
            
            if (cropBoxState.activeHandle.includes('e')) {
                cropBox.style.width = newWidth + 'px';
            }
            if (cropBoxState.activeHandle.includes('s')) {
                cropBox.style.height = newHeight + 'px';
            }
            if (cropBoxState.activeHandle.includes('w')) {
                cropBox.style.width = Math.max(50, parseInt(cropBox.style.width || '150') - deltaX) + 'px';
                cropBox.style.left = (cropBoxState.dragStartLeft + deltaX) + 'px';
            }
            if (cropBoxState.activeHandle.includes('n')) {
                cropBox.style.height = Math.max(50, parseInt(cropBox.style.height || '150') - deltaY) + 'px';
                cropBox.style.top = (cropBoxState.dragStartTop + deltaY) + 'px';
            }
        } else {
            // Move operation
            cropBox.style.left = (cropBoxState.dragStartLeft + deltaX) + 'px';
            cropBox.style.top = (cropBoxState.dragStartTop + deltaY) + 'px';
        }
    };

    document.onmouseup = () => {
        cropBoxState.isDragging = false;
        cropBoxState.activeHandle = null;
    };

    // Global Crop Box Functions
    window.resetCropBox = () => {
        if (cropBox) {
            cropBox.style.display = 'none';
        }
        cropBoxState.isActive = false;
        cropBoxState.cropData = null;
        alert('Crop area reset. Click to draw a new crop box.');
    };

    window.applyCrop = () => {
        if (!cropBox || !cropBoxState.isActive) {
            alert('Please draw a crop box first');
            return;
        }
        
        const canvasRect = canvasImageWrapper.getBoundingClientRect();
        const cropRect = cropBox.getBoundingClientRect();
        
        // Calculate crop coordinates relative to the image
        const img = new Image();
        img.src = canvasImage.src;
        img.onload = () => {
            const scaleX = img.width / canvasRect.width;
            const scaleY = img.height / canvasRect.height;
            
            const cropData = {
                x: (cropRect.left - canvasRect.left) * scaleX,
                y: (cropRect.top - canvasRect.top) * scaleY,
                width: cropRect.width * scaleX,
                height: cropRect.height * scaleY
            };
            
            // Store crop data for this batch item
            const selectedItem = batchQueue.find(i => i.id === selectedBatchItemId);
            if (selectedItem) {
                selectedItem.cropData = cropData;
                cropBoxState.cropData = cropData;
                alert('✅ Crop area applied! This selected region will be processed by the neural engine.');
            }
        };
    };

    // Helper function to crop an image file based on crop data
    window.cropImageFile = async (file, cropData) => {
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = new Image();
                img.onload = () => {
                    // Create a canvas with the cropped dimensions
                    const canvas = document.createElement('canvas');
                    canvas.width = Math.round(cropData.width);
                    canvas.height = Math.round(cropData.height);
                    
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(
                        img,
                        Math.round(cropData.x), 
                        Math.round(cropData.y), 
                        Math.round(cropData.width), 
                        Math.round(cropData.height),
                        0, 
                        0, 
                        Math.round(cropData.width), 
                        Math.round(cropData.height)
                    );
                    
                    // Convert canvas to blob
                    canvas.toBlob((blob) => {
                        // Create a new File object from the blob
                        const croppedFile = new File([blob], file.name, { type: 'image/jpeg' });
                        resolve(croppedFile);
                    }, 'image/jpeg', 0.95);
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        });
    };

    // Safe Element existence checks
    /* This ensures that if we are on a page without a specific UI element (like the editor), 
       the script continues to run for other features like the Navbar and Authentication. */
    const hasEditor = fileInput && dropZone && processBtn;

    // Handle Download from Batch Results
    window.handleBatchDownload = async (event, filename) => {
        event.stopPropagation();
        
        const user = JSON.parse(localStorage.getItem('toonify_user'));
        if (!user) {
            openAuth();
            return;
        }

        const isPro = user.role === 'admin' || user.role === 'pro_member';
        
        if (!isPro) {
            // Non-pro users MUST pay
            try {
                const checkRes = await fetch(`/api/user/check-payment?filename=${filename}`);
                const checkData = await checkRes.json();
                
                if (!checkData.has_paid) {
                    // User hasn't paid - open payment modal
                    window.currentImage = filename;
                    openPayment('jpg', '95');
                    return;
                }
            } catch (err) {
                console.error('Error checking payment:', err);
                alert('Unable to verify payment status. Please try again.');
                return;
            }
        }

        // User is Pro/Admin or has paid - allow download
        const url = `/api/user/download?filename=${filename}&format=jpg&quality=95`;
        window.location.href = url;
    };

    // Handle Download Click
    if (downloadBtn) {
        downloadBtn.onclick = async () => {
            const format = document.getElementById('downloadFormat').value;
            const quality = document.getElementById('downloadQuality').value;
            const filename = window.currentImage;

            if (!filename) return;

            // Check if user is logged in
            const user = JSON.parse(localStorage.getItem('toonify_user'));
            if (!user) {
                openAuth();
                return;
            }

            // ENFORCE PAYMENT: Check payment status before allowing download
            const isPro = user.role === 'admin' || user.role === 'pro_member';
            
            if (!isPro) {
                // Non-pro users MUST pay
                try {
                    const checkRes = await fetch(`/api/user/check-payment?filename=${filename}`);
                    const checkData = await checkRes.json();
                    
                    if (!checkData.has_paid) {
                        // User hasn't paid - open payment modal
                        openPayment(format, quality);
                        return;
                    }
                } catch (err) {
                    console.error('Error checking payment:', err);
                    alert('Unable to verify payment status. Please try again.');
                    return;
                }
            }

            // User is Pro/Admin or has paid - allow download
            const url = `/api/user/download?filename=${filename}&format=${format}&quality=${quality}`;
            window.location.href = url;
        };
    }

    // SaaS Style Switcher
    if (styleItems.length > 0) {
        styleItems.forEach(item => {
            item.onclick = () => {
                styleItems.forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                selectedStyle = item.dataset.style;

                // If an item is selected in the batch queue, update its style
                if (selectedBatchItemId) {
                    updateItemStyle(selectedBatchItemId, selectedStyle);
                }
            };
        });
    }

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
    if (dropZone) {
        dropZone.onclick = () => {
            const user = JSON.parse(localStorage.getItem('toonify_user'));
            if (!user) {
                openAuth();
            } else {
                fileInput.click();
            }
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

            if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files);
        };
    }

    function handleFile(input) {
        let filesArray = [];
        if (input instanceof FileList) {
            filesArray = Array.from(input);
        } else if (input instanceof File || input instanceof Blob) {
            filesArray = [input];
            // If it's a blob from camera, give it a name
            if (input instanceof Blob && !input.name) {
                input.name = `capture_${Date.now()}.jpg`;
            }
        } else if (Array.isArray(input)) {
            filesArray = input;
        }

        filesArray.forEach(file => {
            if (file.type && !file.type.startsWith('image/')) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                const item = {
                    file: file,
                    preview: e.target.result,
                    style: selectedStyle,
                    id: Math.random().toString(36).substr(2, 9)
                };
                batchQueue.push(item);

                // If it's the first image, select it automatically
                if (batchQueue.length === 1) {
                    selectedBatchItemId = item.id;
                    window.selectBatchItem(item.id); // Trigger crop box view
                }

                updateBatchUI();
            };
            reader.readAsDataURL(file);
        });
    }

    window.clearBatch = () => {
        batchQueue = [];
        updateBatchUI();
    };

    window.updateItemStyle = (id, style) => {
        const item = batchQueue.find(i => i.id === id);
        if (item) {
            item.style = style;
            updateBatchUI(); // Re-render to show updated style in the list if needed
        }
    };

    window.selectBatchItem = (id) => {
        selectedBatchItemId = id;
        const item = batchQueue.find(i => i.id === id);
        if (item) {
            // Update sidebar style to match selected item
            styleItems.forEach(si => {
                if (si.dataset.style === item.style) {
                    si.classList.add('active');
                } else {
                    si.classList.remove('active');
                }
            });
            selectedStyle = item.style;
            
            // Show crop box view for this image
            if (canvasImage && cropBoxView) {
                canvasImage.src = item.preview;
                placeholder.style.display = 'none';
                resultView.style.display = 'none';
                sliderView.style.display = 'none';
                cropBoxView.style.display = 'flex';
                
                // Reset crop box state and create default crop box
                cropBoxState.isActive = false;
                cropBoxState.cropData = null;
                
                // Wait for image to load then create default crop box
                canvasImage.onload = () => {
                    if (cropBox && canvasImageWrapper) {
                        const wrapperRect = canvasImageWrapper.getBoundingClientRect();
                        const padding = 40; // Pixels from edge
                        
                        cropBox.style.left = padding + 'px';
                        cropBox.style.top = padding + 'px';
                        cropBox.style.width = (wrapperRect.width - padding * 2) + 'px';
                        cropBox.style.height = (wrapperRect.height - padding * 2) + 'px';
                        cropBox.style.display = 'block';
                        cropBoxState.isActive = true;
                    }
                };
                
                // Trigger load if already cached
                if (canvasImage.complete) {
                    canvasImage.onload();
                }
            }
        }
        updateBatchUI();
    };

    window.removeItem = (id) => {
        batchQueue = batchQueue.filter(i => i.id !== id);
        if (selectedBatchItemId === id) selectedBatchItemId = null;
        updateBatchUI();
    };

    function updateBatchUI() {
        const batchList = document.getElementById('batchList');
        const batchItems = document.getElementById('batchItems');
        const batchCount = document.getElementById('batchCount');
        const uploadText = document.getElementById('uploadText');
        const uploadPreview = document.getElementById('uploadPreview');
        const processBtn = document.getElementById('processBtn');

        if (batchQueue.length > 0) {
            batchList.style.display = 'block';
            batchCount.innerText = batchQueue.length;

            // Hide the single preview and text, show "Add More" button instead
            uploadPreview.style.display = 'none';
            uploadText.innerHTML = `
                <div style="padding: 10px; border: 2px dashed var(--primary); border-radius: 12px; background: var(--primary-soft); color: var(--primary);">
                    <i class="fas fa-plus-circle" style="font-size: 1.5rem; margin-bottom: 5px; display: block;"></i>
                    <strong style="font-size: 0.8rem;">Add More Photos</strong>
                </div>
            `;
            uploadText.style.display = 'block';

            processBtn.disabled = false;
            processBtn.innerHTML = `Transform ${batchQueue.length} ${batchQueue.length > 1 ? 'Images' : 'Image'} <span style="font-size:0.75rem; opacity:0.8; font-weight:400; display:block;">Neural Batch Enabled</span>`;
        } else {
            batchList.style.display = 'none';
            uploadPreview.style.display = 'none';
            uploadText.innerHTML = '<i class="fas fa-cloud-arrow-up"></i><p><strong>Upload Photo(s)</strong></p><p style="font-size:11px; opacity:0.6;">Select multiple files at once</p>';
            processBtn.disabled = true;
            processBtn.innerHTML = `Launch Transformation <i class="fas fa-sparkles"></i>`;
        }

        if (batchItems) {
            batchItems.innerHTML = batchQueue.map((item, index) => {
                const isSelected = item.id === selectedBatchItemId;
                return `
                <div class="batch-item ${isSelected ? 'selected' : ''}" 
                     onclick="selectBatchItem('${item.id}')"
                     style="display: flex; align-items: center; gap: 10px; background: ${isSelected ? 'rgba(255, 126, 95, 0.08)' : '#f8fafc'}; padding: 10px; border-radius: 12px; border: 1px solid ${isSelected ? 'var(--primary)' : '#e2e8f0'}; margin-bottom:5px; cursor: pointer; transition: 0.2s; position: relative;">
                    <img src="${item.preview}" style="width: 40px; height: 40px; border-radius: 8px; object-fit: cover; border: 1px solid #e2e8f0;">
                    <div style="flex: 1; overflow: hidden;">
                        <p style="font-size: 0.75rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin: 0; color: #1e293b;">${item.file.name}</p>
                        <p style="font-size: 0.65rem; color: var(--primary); font-weight: 800; margin: 0; text-transform: uppercase;">Style: ${item.style.replace(/_/g, ' ')}</p>
                    </div>
                    <button onclick="event.stopPropagation(); removeItem('${item.id}')" style="background: none; border: none; color: #94a3b8; cursor: pointer; padding: 5px; font-size: 0.8rem;"><i class="fas fa-trash-alt"></i></button>
                    ${isSelected ? '<div style="position: absolute; right: 8px; top: 10px; width: 6px; height: 6px; background: var(--primary); border-radius: 50%;"></div>' : ''}
                </div>
            `}).join('');
        }
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

                    handleFile(blob);

                    // Close modal after capture
                    closeCameraModal();
                    alert('📸 Photo captured! Added to batch queue.');
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

                handleFile(file);

                closeWhatsappModal();
                alert('✅ Image imported from WhatsApp! Added to batch queue.');
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
    if (processBtn) {
        processBtn.onclick = async () => {
            if (batchQueue.length === 0) return;

            const batchQueue_at_start = [...batchQueue];
            loader.style.display = 'flex';

            const formData = new FormData();
            const styles = [];

            try {
                // Process each item, applying crop if needed
                for (const item of batchQueue) {
                    let imageToSend = item.file;
                    
                    // If item has crop data, crop the image before sending
                    if (item.cropData) {
                        imageToSend = await window.cropImageFile(item.file, item.cropData);
                    }
                    
                    formData.append('images', imageToSend);
                    styles.push(item.style);
                }
                
                formData.append('styles', styles.join(','));

                const response = await fetch('/api/process/batch', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error("Server Error:", response.status, errorText);
                    throw new Error(`Server responded with ${response.status}`);
                }

                const data = await response.json();

                if (data.success && data.results && data.results.length > 0) {
                    // Clear batch queue after success
                    const completedBatch = data.results;
                    const previewsCopy = batchQueue_at_start; // Use our copy
                    batchQueue = [];
                    selectedBatchItemId = null;
                    updateBatchUI();

                    // Hide all stage views before showing results
                    if (document.getElementById('placeholder')) document.getElementById('placeholder').style.display = 'none';
                    if (document.getElementById('cropBoxView')) document.getElementById('cropBoxView').style.display = 'none';
                    if (document.getElementById('resultView')) document.getElementById('resultView').style.display = 'none';
                    if (document.getElementById('sliderView')) document.getElementById('sliderView').style.display = 'none';
                    if (document.getElementById('downloadArea')) document.getElementById('downloadArea').style.display = 'none';
                    if (document.getElementById('statsPanel')) document.getElementById('statsPanel').style.display = 'none';

                    // Show Batch Results Container
                    const batchResultsView = document.getElementById('batchResultsView');
                    const batchResultsGrid = document.getElementById('batchResultsGrid');
                    const batchResultsCount = document.getElementById('batchResultsCount');

                    if (batchResultsView && batchResultsGrid) {
                        batchResultsView.style.display = 'block';
                        batchResultsCount.innerText = `${completedBatch.length} Images`;

                        batchResultsGrid.innerHTML = completedBatch.map(res => {
                            if (!res.success) return `
                                <div class="batch-result-card" style="background:#fff1f2; border: 1px solid #fecaca; padding:15px; border-radius:16px; text-align:center;">
                                    <i class="fas fa-exclamation-triangle" style="color:#ef4444; font-size:1.5rem;"></i>
                                    <p style="font-size:0.75rem; margin-top:10px; color:#991b1b;">Failed: ${res.original_filename}</p>
                                </div>
                            `;

                            const previewItem = previewsCopy.find(p => p.file.name === res.original_filename);
                            const originalSrc = previewItem ? previewItem.preview : '';

                            return `
                                <div class="batch-result-card" style="background:white; border: 1px solid #e2e8f0; border-radius:16px; overflow:hidden; transition: 0.3s; cursor:pointer;" onclick="viewBatchSingle('${res.image_filename}', '${originalSrc.replace(/'/g, "\\'")}')">
                                    <div style="position:relative; aspect-ratio: 1; overflow:hidden;">
                                        <img src="${res.processed_url}?thumb=1" style="width:100%; height:100%; object-fit:cover;" loading="lazy">
                                        <div style="position:absolute; bottom:0; left:0; right:0; background:linear-gradient(transparent, rgba(0,0,0,0.6)); padding:10px;">
                                            <span style="font-size:0.65rem; color:white; font-weight:700; text-transform:uppercase;">${res.style}</span>
                                        </div>
                                    </div>
                                    <div style="padding:10px; display:flex; justify-content:space-between; align-items:center;">
                                        <span style="font-size:0.7rem; color:#64748b; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:100px;">${res.original_filename}</span>
                                        <button onclick="handleBatchDownload(event, '${res.image_filename}')" style="background:none; border:none; color:var(--primary); font-size:0.9rem; cursor:pointer;"><i class="fas fa-download"></i></button>
                                    </div>
                                </div>
                            `;
                        }).join('');
                    }

                    // Define helper for viewing single image from batch
                    window.viewBatchSingle = (filename, originalSrc) => {
                        window.currentImage = filename;
                        const timestamp = Date.now();
                        const path = `/data/processed/${filename}?t=${timestamp}`;

                        // Hide batch grid, show single view
                        if (batchResultsView) batchResultsView.style.display = 'none';
                        if (document.getElementById('cropBoxView')) document.getElementById('cropBoxView').style.display = 'none';
                        const isDynamic = document.getElementById('tabDynamic').classList.contains('active');
                        if (isDynamic) {
                            if (sliderView) sliderView.style.display = 'block';
                            if (resultView) resultView.style.display = 'none';
                        } else {
                            if (resultView) resultView.style.display = 'grid';
                            if (sliderView) sliderView.style.display = 'none';
                        }
                        if (document.getElementById('downloadArea')) document.getElementById('downloadArea').style.display = 'block';

                        if (document.getElementById('viewOriginal')) document.getElementById('viewOriginal').src = originalSrc;
                        const processedImg = document.getElementById('viewProcessed');
                        if (processedImg) processedImg.src = path;

                        if (document.getElementById('sliderOriginal')) document.getElementById('sliderOriginal').src = originalSrc;
                        if (document.getElementById('sliderProcessed')) document.getElementById('sliderProcessed').src = path;

                        // NEW: Update Stats if available
                        const result = completedBatch.find(r => r.image_filename === filename);
                        if (result && result.stats) {
                            const statsPanel = document.getElementById('statsPanel');
                            const statsPanelBody = document.getElementById('statsPanelBody');
                            const chevron = document.getElementById('statsPanelChevron');
                            if (statsPanel) statsPanel.style.display = 'block';
                            if (statsPanelBody) statsPanelBody.style.display = 'block';
                            if (chevron) chevron.style.transform = 'rotate(180deg)';

                            const s = result.stats;
                            if (document.getElementById('origBright')) document.getElementById('origBright').innerText = s.original.brightness;
                            if (document.getElementById('procBright')) document.getElementById('procBright').innerText = s.processed.brightness;
                            if (document.getElementById('origContrast')) document.getElementById('origContrast').innerText = s.original.contrast;
                            if (document.getElementById('procContrast')) document.getElementById('procContrast').innerText = s.processed.contrast;
                            if (document.getElementById('procTimeLabel')) document.getElementById('procTimeLabel').innerText = `${result.proc_time.toFixed(2)}s`;

                            // Color Bars
                            if (document.getElementById('origR')) document.getElementById('origR').style.width = `${s.original.colors.r}%`;
                            if (document.getElementById('origG')) document.getElementById('origG').style.width = `${s.original.colors.g}%`;
                            if (document.getElementById('origB')) document.getElementById('origB').style.width = `${s.original.colors.b}%`;
                            if (document.getElementById('procR')) document.getElementById('procR').style.width = `${s.processed.colors.r}%`;
                            if (document.getElementById('procG')) document.getElementById('procG').style.width = `${s.processed.colors.g}%`;
                            if (document.getElementById('procB')) document.getElementById('procB').style.width = `${s.processed.colors.b}%`;
                        }

                        // Add "Back to Batch" button if it doesn't exist
                        let backBtn = document.getElementById('backToBatchBtn');
                        if (!backBtn) {
                            backBtn = document.createElement('button');
                            backBtn.id = 'backToBatchBtn';
                            backBtn.innerHTML = '<i class="fas fa-arrow-left"></i> Back to Batch Results';
                            backBtn.className = 'btn-auth';
                            backBtn.style = 'margin-bottom: 20px; background: #64748b; font-size: 0.8rem; padding: 8px 15px;';
                            backBtn.onclick = () => {
                                if (document.getElementById('resultView')) document.getElementById('resultView').style.display = 'none';
                                if (document.getElementById('downloadArea')) document.getElementById('downloadArea').style.display = 'none';
                                if (batchResultsView) batchResultsView.style.display = 'block';
                            };
                            document.querySelector('.app-canvas').prepend(backBtn);
                        } else {
                            backBtn.style.display = 'block';
                        }
                    };

                    // Show a specialized Batch Result Banner
                    const canvasHeader = document.querySelector('.canvas-header');
                    if (canvasHeader) {
                        let banner = document.getElementById('batchSuccessBanner');
                        if (!banner) {
                            banner = document.createElement('div');
                            banner.id = 'batchSuccessBanner';
                            banner.style = "background: #dcfce7; color: #15803d; padding: 15px 25px; border-radius: 12px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; font-weight: 600; font-size: 0.9rem; border: 1px solid #bbf7d0;";
                            canvasHeader.after(banner);
                        }
                        banner.innerHTML = `
                            <span><i class="fas fa-check-circle"></i> Batch transformation complete! processed ${completedBatch.length} images.</span>
                            <a href="/gallery" style="color: #15803d; text-decoration: underline;">View All in Gallery</a>
                        `;
                        banner.style.display = 'flex';
                    }

                    alert(`✅ Batch Complete! ${completedBatch.filter(r => r.success).length} images processed successfully.`);
                } else {
                    alert("Neural Logic Error: " + data.message);
                }
            } catch (error) {
                console.error(error);
                alert("Connection lost during neural stylization.");
            } finally {
                if (loader) loader.style.display = 'none';
            }
        };
    }

    // --- AUTH LOGIC ---
    // Toggle Neural Analysis Statistics panel open/closed
    window.toggleStatsPanel = () => {
        const body = document.getElementById('statsPanelBody');
        const chevron = document.getElementById('statsPanelChevron');
        if (!body) return;
        const isOpen = body.style.display !== 'none';
        body.style.display = isOpen ? 'none' : 'block';
        if (chevron) chevron.style.transform = isOpen ? 'rotate(0deg)' : 'rotate(180deg)';
    };

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

    // --- SESSION & NAV SYNC ---
    async function syncSession() {
        const localUser = JSON.parse(localStorage.getItem('toonify_user'));
        const loginBtn = document.getElementById('loginHeaderBtn');
        const profileContainer = document.getElementById('profileDropdownContainer');
        const profileBtn = document.getElementById('profilePillBtn');
        const profileDropdown = document.getElementById('profileDropdown');

        if (!localUser || !profileContainer) return;

        try {
            // Verify session with server
            const res = await fetch('/api/auth/session');
            const data = await res.json();

            if (data.success) {
                // Session is valid
                if (loginBtn) loginBtn.style.display = 'none';
                profileContainer.style.display = 'block';

                profileBtn.innerHTML = `
                    <img src="https://images.unsplash.com/photo-1633332755192-727a05c4013d?auto=format&fit=crop&q=80&w=100&h=100" class="profile-avatar" alt="User ${data.user.username}">
                    <span style="font-family: 'Inter';">${data.user.username}</span>
                    <i class="fas fa-chevron-down" style="font-size: 0.7rem; color: #94a3b8; margin-left: auto;"></i>
                `;

                profileBtn.onclick = (e) => {
                    e.stopPropagation();
                    const isVisible = profileDropdown.classList.contains('active');
                    if (isVisible) {
                        profileDropdown.style.display = 'none';
                        profileDropdown.classList.remove('active');
                    } else {
                        profileDropdown.style.display = 'block';
                        profileDropdown.classList.add('active');
                    }
                };

                // Close dropdown when clicking outside
                document.addEventListener('click', (e) => {
                    if (profileContainer && !profileContainer.contains(e.target)) {
                        profileDropdown.style.display = 'none';
                        profileDropdown.classList.remove('active');
                    }
                });

                // Rely on native browser navigation and the global click listener
                // for closing the dropdown. This prevents navigation cancellation.

                // Add Admin Panel link if admin
                if (data.user.role === 'admin') {
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
            } else {
                // Session expired on server - clear local state
                localStorage.removeItem('toonify_user');
                if (loginBtn) loginBtn.style.display = 'block';
                profileContainer.style.display = 'none';
            }
        } catch (err) {
            console.error("Session sync failed:", err);
        }
    }
    syncSession();

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

    // Check if we should open auth modal on load
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth') === 'login') {
        if (typeof openAuth === 'function') openAuth();
    }
});
