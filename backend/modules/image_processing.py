"""
Image processing module using OpenCV
Implements various cartoon and artistic effects
"""
import cv2
import numpy as np
from PIL import Image
import io
from typing import Tuple, Optional
import time
import config.settings as settings


class ImageProcessor:
    """Handle all image processing operations"""
    
    def __init__(self):
        """Initialize image processor with default parameters"""
        self.params = settings.CARTOON_PARAMS
    
    @staticmethod
    def load_image(image_file) -> Optional[np.ndarray]:
        """
        Load image from uploaded file
        Returns: numpy array in BGR format
        """
        try:
            # Read image from bytes
            image_bytes = image_file.read()
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    @staticmethod
    def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
        """Convert PIL Image to OpenCV format"""
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
        """Convert OpenCV image to PIL Image"""
        return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))
    
    @staticmethod
    def resize_image(image: np.ndarray, max_width: int = 1280, 
                    max_height: int = 720) -> np.ndarray:
        """Resize image while maintaining aspect ratio"""
        height, width = image.shape[:2]
        
        if width <= max_width and height <= max_height:
            return image
        
        # Calculate scaling factor
        scale = min(max_width / width, max_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return cv2.resize(image, (new_width, new_height), 
                         interpolation=cv2.INTER_AREA)

    @staticmethod
    def get_image_stats(image: np.ndarray) -> dict:
        """Calculate basic image statistics for Task 13"""
        try:
            # Convert to grayscale for brightness/contrast
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Color Distribution (B, G, R)
            b_mean = np.mean(image[:, :, 0])
            g_mean = np.mean(image[:, :, 1])
            r_mean = np.mean(image[:, :, 2])
            total = b_mean + g_mean + r_mean or 1
            
            return {
                "brightness": round(float(brightness), 2),
                "contrast": round(float(contrast), 2),
                "colors": {
                    "r": round((r_mean / total) * 100, 1),
                    "g": round((g_mean / total) * 100, 1),
                    "b": round((b_mean / total) * 100, 1)
                }
            }
        except Exception:
            return {"brightness": 0, "contrast": 0, "colors": {"r": 33, "g": 33, "b": 34}}
    
    def apply_classic_cartoon(self, image: np.ndarray) -> np.ndarray:
        """
        Apply high-fidelity cartoon effect with sharp edges
        Resolution-aware scaling for consistent results
        """
        h, w = image.shape[:2]
        # Base scale factor (standardized to 1280px width)
        scale_factor = w / 1280.0
        
        # Step 1: Smoothing while preserving edges
        smooth = cv2.edgePreservingFilter(image, flags=1, sigma_s=60, sigma_r=0.4)
        
        # Step 2: Edge detection (Resolution-Aware)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        
        # Scale blockSize for higher resolutions (must be odd)
        block_size = int(9 * scale_factor)
        if block_size % 2 == 0: block_size += 1
        block_size = max(3, block_size)
        
        edges = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, blockSize=block_size, C=2
        )
        
        # Step 3: Color quantization (Reduced colors for stronger cartoon feel)
        quantized = self._quantize_colors(smooth, num_colors=8)
        
        # Step 4: Merge edges
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        cartoon = cv2.bitwise_and(quantized, edges_colored)
        
        # Step 5: Boost saturation for that "Pixar" look
        hsv = cv2.cvtColor(cartoon, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.2, 0, 255)
        cartoon = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return cartoon
    
    def apply_sketch_effect(self, image: np.ndarray) -> np.ndarray:
        """
        Apply pencil sketch effect
        Creates a grayscale sketch-like image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Invert the grayscale image
        inverted = cv2.bitwise_not(gray)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
        
        # Invert the blurred image
        inverted_blur = cv2.bitwise_not(blurred)
        
        # Create sketch by dividing grayscale by inverted blur
        sketch = cv2.divide(gray, inverted_blur, scale=256.0)
        
        # Convert back to BGR for consistency
        sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        
        return sketch_bgr
    
    def apply_pencil_color(self, image: np.ndarray) -> np.ndarray:
        """
        Apply colored pencil sketch effect
        Uses OpenCV's pencilSketch function
        """
        # Apply pencil sketch (returns sketch and color sketch)
        _, color_sketch = cv2.pencilSketch(
            image,
            sigma_s=60,
            sigma_r=0.07,
            shade_factor=0.05
        )
        
        return color_sketch
    
    def apply_oil_painting(self, image: np.ndarray) -> np.ndarray:
        """
        Apply a dramatic "Oil Master" painting effect
        """
        # Step 1: Base stylization
        stylized = cv2.stylization(image, sigma_s=100, sigma_r=0.45)
        
        # Step 2: Enhance textures with another pass
        smooth = cv2.edgePreservingFilter(stylized, flags=1, sigma_s=60, sigma_r=0.4)
        
        # Step 3: Immersive Color Boost
        hsv = cv2.cvtColor(smooth, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.3, 0, 255) # Deep Saturation
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.1, 0, 255) # Brightness
        oil = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return oil
    
    def apply_watercolor(self, image: np.ndarray) -> np.ndarray:
        """
        Apply watercolor painting effect with soft edges and vibrant colors
        """
        # Step 1: Apply stylization for watercolor base
        watercolor = cv2.stylization(image, sigma_s=60, sigma_r=0.6)
        
        # Step 2: Apply bilateral filter for smoothness (Switching to edgePreservingFilter)
        smooth = cv2.edgePreservingFilter(watercolor, flags=1, sigma_s=50, sigma_r=0.3)
        
        # Step 3: Enhance colors
        hsv = cv2.cvtColor(smooth, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.4, 0, 255)  # Increase saturation
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.05, 0, 255)  # Slight brightness boost
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return result
    
    def apply_pop_art(self, image: np.ndarray) -> np.ndarray:
        """
        Apply Andy Warhol-style pop art effect with bold colors
        """
        # Step 1: Reduce to fewer colors (posterization)
        quantized = self._quantize_colors(image, num_colors=6)
        
        # Step 2: Detect edges
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edges = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)
        
        # Step 3: Boost saturation dramatically
        hsv = cv2.cvtColor(quantized, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.8, 0, 255)  # High saturation
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.2, 0, 255)  # Brightness
        pop = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Step 4: Add black edges
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        edges_colored = cv2.bitwise_not(edges_colored)
        result = cv2.bitwise_and(pop, edges_colored)
        
        return result
    
    def apply_vintage(self, image: np.ndarray) -> np.ndarray:
        """
        Apply vintage/retro photo effect with sepia tones and vignette
        """
        # Step 1: Apply sepia tone
        kernel = np.array([[0.272, 0.534, 0.131],
                          [0.349, 0.686, 0.168],
                          [0.393, 0.769, 0.189]])
        sepia = cv2.transform(image, kernel)
        sepia = np.clip(sepia, 0, 255).astype(np.uint8)
        
        # Step 2: Add slight blur for dreamy effect
        vintage = cv2.GaussianBlur(sepia, (3, 3), 0)
        
        # Step 3: Create vignette effect
        rows, cols = vintage.shape[:2]
        X_resultant_kernel = cv2.getGaussianKernel(cols, cols/2)
        Y_resultant_kernel = cv2.getGaussianKernel(rows, rows/2)
        resultant_kernel = Y_resultant_kernel * X_resultant_kernel.T
        mask = resultant_kernel / resultant_kernel.max()
        
        # Apply vignette
        for i in range(3):
            vintage[:, :, i] = vintage[:, :, i] * mask
        
        # Step 4: Reduce contrast slightly
        vintage = cv2.convertScaleAbs(vintage, alpha=0.9, beta=10)
        
        return vintage
    
    def apply_anime(self, image: np.ndarray) -> np.ndarray:
        """
        NEO-ANIME ENGINE (Gemini Style):
        Resolution-aware scaling for sharp character lines
        """
        h, w = image.shape[:2]
        scale_factor = w / 1280.0
        
        # Step 1: Smoothing
        smooth = cv2.edgePreservingFilter(image, flags=1, sigma_s=60, sigma_r=0.45)
        
        # Step 2: Advanced Color Quantization
        quantized = self._quantize_colors(smooth, num_colors=12)
        
        # Step 3: Ink Line Extraction (Resolution-Aware)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        
        # Scale blockSize
        block_size = int(7 * scale_factor)
        if block_size % 2 == 0: block_size += 1
        block_size = max(3, block_size)
        
        mask = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, blockSize=block_size, C=4
        )
        
        # Merge
        mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        anime = cv2.bitwise_and(quantized, mask_colored)
        
        # Step 4: Add Glow / Bloom (Resolution-Aware blur)
        blur_size = int(15 * scale_factor)
        if blur_size % 2 == 0: blur_size += 1
        blur_size = max(3, blur_size)
        
        glow = cv2.GaussianBlur(anime, (blur_size, blur_size), 0)
        anime = cv2.addWeighted(anime, 0.8, glow, 0.4, 0)
        
        # Step 5: Final Grade
        hsv = cv2.cvtColor(anime, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.6, 0, 255) 
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return result

    def apply_ghibli(self, image: np.ndarray) -> np.ndarray:
        """
        STUDIO GHIBLI ENGINE (Painterly):
        - Soft, painterly edges
        - Nature-inspired color balancing (warm skin, lush greens)
        - Diffusion glow
        """
        # Step 1: Smooth image heavily but keep structure
        smooth = cv2.edgePreservingFilter(image, flags=1, sigma_s=50, sigma_r=0.4)
        
        # Step 2: Painterly Quantization (Warm & Soft Palette)
        # Ghibli style has higher color count but smoother gradients
        quantized = self._quantize_colors(smooth, num_colors=16)
        
        # Step 3: "Diffusion" glow 
        # This gives that hand-painted background feel
        diffuse = cv2.GaussianBlur(quantized, (31, 31), 0)
        ghibli = cv2.addWeighted(quantized, 0.85, diffuse, 0.15, 0)
        
        # Step 4: Soft Contrast & Gamma Correction
        # This makes the image look like an animated film cell
        invGamma = 1.0 / 1.2
        table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        ghibli = cv2.LUT(ghibli, table)
        
        # Step 5: Subtle Edge preservation (No thick lines for Ghibli)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edges = cv2.GaussianBlur(edges, (3,3), 0)
        edges_inv = cv2.bitwise_not(edges)
        edges_color = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)
        
        result = cv2.multiply(ghibli, edges_color, scale=1/255)
        return result
    
    def apply_comic_book(self, image: np.ndarray) -> np.ndarray:
        """
        Premium Comic Book Engine:
        Resolution-aware halftone and inking
        """
        h, w = image.shape[:2]
        scale_factor = w / 1280.0

        # Step 1: Noise reduction
        img_blur = cv2.medianBlur(image, 5)
        quantized = self._quantize_colors(img_blur, num_colors=8)
        
        # Step 2: Clean Ink Edges
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(gray, 50, 150)
        edges = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)
        
        # Step 3: Halftone Overlay (Resolution-Aware Dots)
        halftone = np.zeros((h, w), dtype=np.uint8)
        dot_spacing = max(4, int(6 * scale_factor))
        dot_radius = max(1, int(2 * scale_factor))
        
        for i in range(0, h, dot_spacing):
            for j in range(0, w, dot_spacing):
                cv2.circle(halftone, (j, i), dot_radius, 255, -1)
        
        # Step 4: Color Grading
        hsv = cv2.cvtColor(quantized, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.6, 0, 255)
        comic = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Mask dots into the shadows
        mask = cv2.cvtColor(halftone, cv2.COLOR_GRAY2BGR)
        comic = cv2.addWeighted(comic, 0.9, mask, 0.1, 0)
        
        # Step 5: Final Ink Layer
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        edges_colored = cv2.bitwise_not(edges_colored)
        result = cv2.bitwise_and(comic, edges_colored)
        
        return result
    
    def _quantize_colors(self, image: np.ndarray, num_colors: int = 8) -> np.ndarray:
        """
        ULTRA-OPTIMIZED: Reduce colors using K-means directly on the image 
        with limited iterations for maximum speed.
        """
        pixels = image.reshape((-1, 3))
        pixels = np.float32(pixels)
        
        # Use a reasonable number of iterations for cartoons
        # 10 is a good balance between speed and quality
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        flags = cv2.KMEANS_RANDOM_CENTERS
        
        _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 1, flags)
        
        centers = np.uint8(centers)
        quantized = centers[labels.flatten()]
        return quantized.reshape(image.shape)
    
    def process_image(self, image: np.ndarray, style: str, is_premium: bool = False) -> Tuple[np.ndarray, float]:
        """
        Process image with selected style
        Returns: (processed_image, processing_time)
        """
        start_time = time.time()
        
        # Resize based on plan
        if is_premium:
            # 4K / Ultra-HD Processing for Premium Users
            image = self.resize_image(image, max_width=3840, max_height=2160)
        else:
            # Standard 720p for Free Users
            image = self.resize_image(image, max_width=1280, max_height=720)
        
        # Apply selected style
        if style == "cartoon":
            processed = self.apply_classic_cartoon(image)
        elif style == "sketch":
            processed = self.apply_sketch_effect(image)
        elif style == "pencil_color":
            processed = self.apply_pencil_color(image)
        elif style == "oil_painting":
            processed = self.apply_oil_painting(image)
        elif style == "watercolor":
            processed = self.apply_watercolor(image)
        elif style == "pop_art":
            processed = self.apply_pop_art(image)
        elif style == "vintage":
            processed = self.apply_vintage(image)
        elif style == "anime":
            processed = self.apply_anime(image)
        elif style == "ghibli":
            processed = self.apply_ghibli(image)
        elif style == "comic_book":
            processed = self.apply_comic_book(image)
        else:
            # Default to cartoon
            processed = self.apply_classic_cartoon(image)
        
        processing_time = time.time() - start_time
        
        return processed, processing_time

    def get_image_statistics(self, image: np.ndarray) -> dict:
        """
        Calculate image statistics: brightness, contrast, and color distribution.
        Part of Task 13 requirements.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 1. Brightness (Mean)
        brightness = np.mean(gray)
        
        # 2. Contrast (Standard Deviation)
        contrast = np.std(gray)
        
        # 3. Color distribution (Mean of each channel)
        # BGR channels
        blue_avg = np.mean(image[:, :, 0])
        green_avg = np.mean(image[:, :, 1])
        red_avg = np.mean(image[:, :, 2])
        
        return {
            "brightness": round(float(brightness), 2),
            "contrast": round(float(contrast), 2),
            "colors": {
                "red": round(float(red_avg), 2),
                "green": round(float(green_avg), 2),
                "blue": round(float(blue_avg), 2)
            }
        }
    
    @staticmethod
    def create_comparison(original: np.ndarray, processed: np.ndarray) -> np.ndarray:
        """
        Create side-by-side comparison image
        """
        # Ensure both images have same height
        h1, w1 = original.shape[:2]
        h2, w2 = processed.shape[:2]
        
        if h1 != h2:
            # Resize processed to match original height
            scale = h1 / h2
            new_width = int(w2 * scale)
            processed = cv2.resize(processed, (new_width, h1))
        
        # Concatenate images horizontally
        comparison = np.hstack([original, processed])
        
        # Add text labels
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_thickness = 2
        color = (255, 255, 255)
        
        cv2.putText(comparison, "Original", (20, 40), font, 
                   font_scale, color, font_thickness)
        cv2.putText(comparison, "Cartoonized", (w1 + 20, 40), font, 
                   font_scale, color, font_thickness)
        
        return comparison
    
    @staticmethod
    def save_image(image: np.ndarray, filepath: str, quality: int = 95) -> bool:
        """Save processed image to file"""
        try:
            cv2.imwrite(filepath, image, [cv2.IMWRITE_JPEG_QUALITY, quality])
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    def remove_background_mask(self, image: np.ndarray) -> np.ndarray:
        """
        Fast foreground segmentation using thresholding and contours as a fallback for GrabCut.
        """
        try:
            mask = np.zeros(image.shape[:2], np.uint8)
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)
            h, w = image.shape[:2]
            rect = (int(w*0.1), int(h*0.1), int(w*0.8), int(h*0.8))
            cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 3, cv2.GC_INIT_WITH_RECT)
            mask2 = np.where((mask==2)|(mask==0), 0, 1).astype('uint8')
            mask2 = cv2.GaussianBlur(mask2, (7, 7), 0)
            return mask2
        except:
            # Fallback to center-weighted mask if GrabCut fails
            h, w = image.shape[:2]
            mask = np.zeros((h, w), np.uint8)
            cv2.circle(mask, (w//2, h//2), int(min(h, w)*0.4), 1, -1)
            return cv2.GaussianBlur(mask, (51, 51), 0)

    def teleport_background(self, image: np.ndarray, bg_type: str) -> np.ndarray:
        """
        Teleport user to a new world.
        """
        bg_map = {
            "tokyo": "frontend/static/images/backgrounds/tokyo.png",
            "cyberpunk": "frontend/static/images/backgrounds/cyberpunk.png",
            "forest": "frontend/static/images/backgrounds/forest.png"
        }
        
        bg_path = bg_map.get(bg_type)
        if not bg_path: return image
        
        # Load background
        import os
        if not os.path.exists(bg_path): return image
        bg = cv2.imread(bg_path)
        if bg is None: return image
        
        h, w = image.shape[:2]
        bg = cv2.resize(bg, (w, h))
        
        # Segment
        mask = self.remove_background_mask(image)
        mask_3d = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR).astype(float)
        
        # Blend
        fg = image.astype(float)
        bg = bg.astype(float)
        
        result = (fg * mask_3d + bg * (1.0 - mask_3d)).astype(np.uint8)
        return result

    def create_toon_mo(self, image: np.ndarray) -> bytes:
        """
        Create a 2-second "breathing" animation (GIF)
        """
        from PIL import Image as PILImage
        frames = []
        h, w = image.shape[:2]
        
        # Convert BGR to RGB for PIL
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        base_pil = PILImage.fromarray(image_rgb)
        
        # Generate 15 frames for a smooth pulse
        for i in range(15):
            # Scale follows a sine wave for "breathing" effect
            # Amplitude is 3% zoom
            scale = 1.0 + 0.03 * np.sin(i * np.pi / 7.5)
            nw, nh = int(w * scale), int(h * scale)
            
            # Resize and crop to original dimensions
            frame = base_pil.resize((nw, nh), PILImage.LANCZOS)
            left = (nw - w) // 2
            top = (nh - h) // 2
            frame = frame.crop((left, top, left + w, top + h))
            
            # Add a subtle brightness pulse
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Brightness(frame)
            frame = enhancer.enhance(1.0 + 0.05 * np.sin(i * np.pi / 7.5))
            
            frames.append(frame)
            
        byte_io = io.BytesIO()
        # Save as optimized GIF
        frames[0].save(
            byte_io, 
            format='GIF', 
            save_all=True, 
            append_images=frames[1:], 
            duration=80, 
            loop=0,
            optimize=True
        )
        return byte_io.getvalue()

    def apply_style_dna(self, target: np.ndarray, reference: np.ndarray) -> np.ndarray:
        """
        AI Style DNA Transfer: Extracts the color profile and 'vibe' from a reference 
        image and injects it into the target image using Lab color space shifting.
        """
        # Convert both to LAB space
        target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype("float32")
        ref_lab = cv2.cvtColor(reference, cv2.COLOR_BGR2LAB).astype("float32")
        
        # Split channels
        (l_t, a_t, b_t) = cv2.split(target_lab)
        (l_r, a_r, b_r) = cv2.split(ref_lab)
        
        # Calculate stats
        (l_t_mean, l_t_std) = (l_t.mean(), l_t.std())
        (a_t_mean, a_t_std) = (a_t.mean(), a_t.std())
        (b_t_mean, b_t_std) = (b_t.mean(), b_t.std())
        
        (l_r_mean, l_r_std) = (l_r.mean(), l_r.std())
        (a_r_mean, a_r_std) = (a_r.mean(), a_r.std())
        (b_r_mean, b_r_std) = (b_r.mean(), b_r.std())
        
        # Shift and scale channels (Reference DNA injection)
        l_t = (((l_t - l_t_mean) / (l_t_std + 1e-5)) * l_r_std) + l_r_mean
        a_t = (((a_t - a_t_mean) / (a_t_std + 1e-5)) * a_r_std) + a_r_mean
        b_t = (((b_t - b_t_mean) / (b_t_std + 1e-5)) * b_r_std) + b_r_mean
        
        # Clip and merge
        l_t = np.clip(l_t, 0, 255)
        a_t = np.clip(a_t, 0, 255)
        b_t = np.clip(b_t, 0, 255)
        
        transfer = cv2.merge([l_t, a_t, b_t])
        transfer = cv2.cvtColor(transfer.astype("uint8"), cv2.COLOR_LAB2BGR)
        
        return transfer

    @staticmethod
    def get_image_bytes(image: np.ndarray, format: str = 'JPEG', 
                       quality: int = 95) -> bytes:
        """
        Convert OpenCV image to bytes for download
        """
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # Save to bytes
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format=format, quality=quality)
        img_byte_arr.seek(0)
        
        return img_byte_arr.getvalue()


# Global image processor instance
image_processor = ImageProcessor()
