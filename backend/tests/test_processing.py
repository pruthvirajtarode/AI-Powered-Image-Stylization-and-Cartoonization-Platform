"""
Unit tests for image processing module
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import numpy as np
import cv2
from modules.image_processing import ImageProcessor


@pytest.fixture
def test_image():
    """Create a test image"""
    img = np.zeros((300, 400, 3), dtype=np.uint8)
    cv2.rectangle(img, (50, 50), (350, 250), (255, 128, 0), -1)
    cv2.circle(img, (200, 150), 50, (255, 255, 255), -1)
    return img


def test_image_resize(test_image):
    """Test image resizing"""
    processor = ImageProcessor()
    
    # Resize to smaller dimensions
    resized = processor.resize_image(test_image, max_width=200, max_height=150)
    assert resized.shape[1] <= 200
    assert resized.shape[0] <= 150
    
    # Image smaller than max dimensions should not be resized
    small_img = np.zeros((100, 100, 3), dtype=np.uint8)
    not_resized = processor.resize_image(small_img, max_width=200, max_height=200)
    assert not_resized.shape == small_img.shape


def test_cartoon_effect(test_image):
    """Test classic cartoon effect"""
    processor = ImageProcessor()
    result, proc_time = processor.process_image(test_image, "cartoon")
    
    assert result.shape == test_image.shape
    assert proc_time > 0
    assert result.dtype == np.uint8


def test_sketch_effect(test_image):
    """Test sketch effect"""
    processor = ImageProcessor()
    result, proc_time = processor.process_image(test_image, "sketch")
    
    assert result.shape == test_image.shape
    assert proc_time > 0


def test_pencil_color_effect(test_image):
    """Test pencil color effect"""
    processor = ImageProcessor()
    result, proc_time = processor.process_image(test_image, "pencil_color")
    
    assert result.shape == test_image.shape
    assert proc_time > 0


def test_oil_painting_effect(test_image):
    """Test oil painting effect"""
    processor = ImageProcessor()
    result, proc_time = processor.process_image(test_image, "oil_painting")
    
    assert result.shape == test_image.shape
    assert proc_time > 0


def test_create_comparison(test_image):
    """Test comparison image creation"""
    processor = ImageProcessor()
    processed, _ = processor.process_image(test_image, "cartoon")
    comparison = processor.create_comparison(test_image, processed)
    
    # Comparison should be wider (side by side)
    assert comparison.shape[1] > test_image.shape[1]
    assert comparison.shape[0] == test_image.shape[0]


def test_image_conversion(test_image):
    """Test image format conversions"""
    processor = ImageProcessor()
    
    # CV2 to PIL
    pil_img = processor.cv2_to_pil(test_image)
    assert pil_img.mode == 'RGB'
    
    # PIL to CV2
    cv2_img = processor.pil_to_cv2(pil_img)
    assert cv2_img.shape == test_image.shape


if __name__ == "__main__":
    print("Running image processing tests...")
    
    # Create test image
    test_img = np.zeros((300, 400, 3), dtype=np.uint8)
    cv2.rectangle(test_img, (50, 50), (350, 250), (255, 128, 0), -1)
    
    processor = ImageProcessor()
    
    test_image_resize(test_img)
    print("✅ Resize test passed")
    
    test_cartoon_effect(test_img)
    print("✅ Cartoon effect test passed")
    
    test_sketch_effect(test_img)
    print("✅ Sketch effect test passed")
    
    test_pencil_color_effect(test_img)
    print("✅ Pencil color test passed")
    
    test_oil_painting_effect(test_img)
    print("✅ Oil painting test passed")
    
    test_create_comparison(test_img)
    print("✅ Comparison test passed")
    
    test_image_conversion(test_img)
    print("✅ Conversion test passed")
    
    print("\n🎉 All image processing tests passed!")
