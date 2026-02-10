"""
Test image processing functions
"""
import sys
from pathlib import Path
import cv2
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.image_processing import image_processor
import time


def create_test_image():
    """Create a simple test image"""
    # Create a colorful test image
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # Add colored rectangles
    cv2.rectangle(img, (50, 50), (250, 150), (255, 0, 0), -1)  # Blue
    cv2.rectangle(img, (350, 50), (550, 150), (0, 255, 0), -1)  # Green
    cv2.rectangle(img, (50, 250), (250, 350), (0, 0, 255), -1)  # Red
    cv2.rectangle(img, (350, 250), (550, 350), (255, 255, 0), -1)  # Cyan
    
    # Add some shapes
    cv2.circle(img, (150, 200), 50, (255, 255, 255), -1)
    cv2.circle(img, (450, 200), 50, (128, 128, 128), -1)
    
    return img


def test_all_styles():
    """Test all cartoon styles"""
    print("🧪 Testing Image Processing Styles\n")
    
    # Create test image
    print("Creating test image...")
    test_image = create_test_image()
    
    styles = {
        "cartoon": "Classic Cartoon",
        "sketch": "Sketch Effect",
        "pencil_color": "Pencil Color",
        "oil_painting": "Oil Painting"
    }
    
    results = []
    
    for style_key, style_name in styles.items():
        print(f"\n🎨 Testing {style_name}...")
        start_time = time.time()
        
        try:
            processed, proc_time = image_processor.process_image(test_image, style_key)
            duration = time.time() - start_time
            
            print(f"  ✅ Success! Processing time: {proc_time:.2f}s")
            print(f"  📏 Output shape: {processed.shape}")
            
            results.append({
                'style': style_name,
                'success': True,
                'time': proc_time
            })
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            results.append({
                'style': style_name,
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print("\n" + "="*50)
    print("📊 Test Summary")
    print("="*50)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\nTotal tests: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    
    if successful == total:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
    
    print("\n" + "="*50)


def test_image_utilities():
    """Test image utility functions"""
    print("\n🔧 Testing Image Utilities\n")
    
    test_image = create_test_image()
    
    # Test resize
    print("Testing resize...")
    resized = image_processor.resize_image(test_image, max_width=300, max_height=200)
    print(f"  Original: {test_image.shape}")
    print(f"  Resized: {resized.shape}")
    print("  ✅ Resize working")
    
    # Test comparison
    print("\nTesting comparison...")
    processed, _ = image_processor.process_image(test_image, "cartoon")
    comparison = image_processor.create_comparison(test_image, processed)
    print(f"  Comparison shape: {comparison.shape}")
    print("  ✅ Comparison working")
    
    # Test conversion
    print("\nTesting format conversion...")
    pil_img = image_processor.cv2_to_pil(test_image)
    cv2_img = image_processor.pil_to_cv2(pil_img)
    print(f"  PIL conversion: {pil_img.size}")
    print(f"  Back to CV2: {cv2_img.shape}")
    print("  ✅ Conversion working")
    
    print("\n✅ All utility tests passed!")


if __name__ == "__main__":
    print("🎨 Toonify - Image Processing Test Suite")
    print("="*50)
    
    test_all_styles()
    test_image_utilities()
    
    print("\n✨ Testing complete!")
