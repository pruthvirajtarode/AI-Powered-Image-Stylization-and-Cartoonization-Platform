"""
Unit tests for payment module
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from modules.payment import PaymentProcessor


def test_demo_payment():
    """Test demo payment processing"""
    processor = PaymentProcessor()
    
    success, trans_id, message = processor.process_demo_payment(
        user_id=1,
        image_filename="test_image.jpg"
    )
    
    assert success
    assert trans_id.startswith("demo_")
    assert len(trans_id) > 5
    assert "successful" in message.lower()


def test_price_formatting():
    """Test price formatting"""
    processor = PaymentProcessor()
    
    # USD
    formatted = processor.format_price(2.99, "USD")
    assert "$2.99" == formatted
    
    # EUR
    formatted = processor.format_price(3.50, "EUR")
    assert "€3.50" == formatted
    
    # INR
    formatted = processor.format_price(199.00, "INR")
    assert "₹199.00" == formatted


def test_payment_status_messages():
    """Test payment status message generation"""
    processor = PaymentProcessor()
    
    assert "pending" in processor.get_payment_status_message("pending").lower()
    assert "completed" in processor.get_payment_status_message("completed").lower()
    assert "failed" in processor.get_payment_status_message("failed").lower()


if __name__ == "__main__":
    print("Running payment tests...")
    
    test_demo_payment()
    print("✅ Demo payment test passed")
    
    test_price_formatting()
    print("✅ Price formatting test passed")
    
    test_payment_status_messages()
    print("✅ Status message test passed")
    
    print("\n🎉 All payment tests passed!")
