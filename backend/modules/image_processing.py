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
    def resize_image(image: np.ndarray, max_width: int = 1920, 
                    max_height: int = 1080) -> np.ndarray:
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
    
    def apply_classic_cartoon(self, image: np.ndarray) -> np.ndarray:
        """
        Apply high-fidelity cartoon effect with sharp edges
        """
        # Step 1: Smoothing while preserving edges (Optimized for speed)
        img_small = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)
        for _ in range(2):
            img_small = cv2.bilateralFilter(img_small, d=9, sigmaColor=75, sigmaSpace=75)
            
        smooth = cv2.resize(img_small, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_LINEAR)
        
        # Step 2: Edge detection 
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, blockSize=9, C=2
        )
        
        # Step 3: Color quantization
        quantized = self._quantize_colors(smooth, num_colors=10)
        
        # Step 4: Merge edges
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        cartoon = cv2.bitwise_and(quantized, edges_colored)
        
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
        
        # Step 2: Apply bilateral filter for smoothness
        smooth = cv2.bilateralFilter(watercolor, d=9, sigmaColor=90, sigmaSpace=90)
        
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
        - High-contrast character focus
        - Vibrant "Cyber-Anime" color palettes
        - Soft-light Bloom
        """
        # Step 1: Smoothing (Multi-pass guided approximation)
        img_small = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)
        for _ in range(2):
            img_small = cv2.bilateralFilter(img_small, d=9, sigmaColor=100, sigmaSpace=100)
        
        smooth = cv2.resize(img_small, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_LINEAR)
        
        # Step 2: Advanced Color Quantization
        quantized = self._quantize_colors(smooth, num_colors=12)
        
        # Step 3: Ink Line Extraction (Preserving highlights)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        # We use a narrower blockSize to avoid eating up light hair/skin
        mask = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, blockSize=7, C=4
        )
        
        # Merge
        mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        anime = cv2.bitwise_and(quantized, mask_colored)
        
        # Step 4: Add "Gemini" Glow / Bloom
        glow = cv2.GaussianBlur(anime, (15, 15), 0)
        anime = cv2.addWeighted(anime, 0.8, glow, 0.4, 0)
        
        # Step 5: Final Grade
        hsv = cv2.cvtColor(anime, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.6, 0, 255) # Intense colors
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
        - Halftone screen patterns
        - Clean, bold ink outlines
        - Posterized vibrant colors
        """
        # Step 1: Noise reduction for clean edges
        img_blur = cv2.medianBlur(image, 5)
        quantized = self._quantize_colors(img_blur, num_colors=8)
        
        # Step 2: Clean Ink Edges
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(gray, 50, 150)
        edges = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)
        
        # Step 3: Halftone Overlay (Creative Dots)
        h, w = image.shape[:2]
        halftone = np.zeros((h, w), dtype=np.uint8)
        for i in range(0, h, 6):
            for j in range(0, w, 6):
                cv2.circle(halftone, (j, i), 2, 255, -1)
        
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
        OPTIMIZED: Reduce colors for real-time performance using representative K-means
        """
        # Performance trick: Run K-means on a tiny version of the image to get colorspace
        h, w = image.shape[:2]
        img_mini = cv2.resize(image, (min(w, 150), min(h, 150)), interpolation=cv2.INTER_AREA)
        pixels = img_mini.reshape((-1, 3))
        pixels = np.float32(pixels)
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, _, centers = cv2.kmeans(
            pixels, num_colors, None, criteria, 3, cv2.KMEANS_RANDOM_CENTERS
        )
        
        centers = np.uint8(centers)
        
        # Apply the found colors back to the ORIGINAL high-res image using broadcasting (FASTER)
        image_flat = image.reshape((-1, 3))
        # Calculating distances manually to avoid slow label loops
        distances = np.linalg.norm(image_flat[:, np.newaxis] - centers, axis=2)
        labels = np.argmin(distances, axis=1)
        
        quantized = centers[labels]
        return quantized.reshape(image.shape)
    
    def process_image(self, image: np.ndarray, style: str) -> Tuple[np.ndarray, float]:
        """
        Process image with selected style
        Returns: (processed_image, processing_time)
        """
        start_time = time.time()
        
        # Resize if too large
        image = self.resize_image(image)
        
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
