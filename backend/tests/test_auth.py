"""
Unit tests for authentication module
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from modules.authentication import Authentication


def test_password_hashing():
    """Test password hashing and verification"""
    password = "Test@Password123"
    
    # Test hashing
    hashed = Authentication.hash_password(password)
    assert hashed != password
    assert len(hashed) > 0
    
    # Test verification
    assert Authentication.verify_password(password, hashed)
    assert not Authentication.verify_password("WrongPassword", hashed)


def test_email_validation():
    """Test email format validation"""
    # Valid emails
    assert Authentication.validate_email("user@example.com")
    assert Authentication.validate_email("test.user@domain.co.uk")
    assert Authentication.validate_email("user+tag@example.com")
    
    # Invalid emails
    assert not Authentication.validate_email("invalid")
    assert not Authentication.validate_email("@example.com")
    assert not Authentication.validate_email("user@")
    assert not Authentication.validate_email("user@.com")


def test_password_validation():
    """Test password strength validation"""
    # Valid passwords
    valid, _ = Authentication.validate_password("Strong@Pass123")
    assert valid
    
    valid, _ = Authentication.validate_password("MyP@ssw0rd!")
    assert valid
    
    # Invalid passwords
    valid, msg = Authentication.validate_password("short")
    assert not valid
    assert "8 characters" in msg
    
    valid, msg = Authentication.validate_password("nouppercase1!")
    assert not valid
    assert "uppercase" in msg
    
    valid, msg = Authentication.validate_password("NOLOWERCASE1!")
    assert not valid
    assert "lowercase" in msg
    
    valid, msg = Authentication.validate_password("NoDigits!")
    assert not valid
    assert "digit" in msg
    
    valid, msg = Authentication.validate_password("NoSpecialChar1")
    assert not valid
    assert "special" in msg


def test_username_validation():
    """Test username validation"""
    # Valid usernames
    valid, _ = Authentication.validate_username("user123")
    assert valid
    
    valid, _ = Authentication.validate_username("test_user")
    assert valid
    
    # Invalid usernames
    valid, msg = Authentication.validate_username("ab")
    assert not valid
    assert "3 characters" in msg
    
    valid, msg = Authentication.validate_username("a" * 21)
    assert not valid
    assert "20 characters" in msg
    
    valid, msg = Authentication.validate_username("user-name")
    assert not valid
    assert "letters, numbers, and underscores" in msg


if __name__ == "__main__":
    print("Running authentication tests...")
    
    test_password_hashing()
    print("✅ Password hashing tests passed")
    
    test_email_validation()
    print("✅ Email validation tests passed")
    
    test_password_validation()
    print("✅ Password validation tests passed")
    
    test_username_validation()
    print("✅ Username validation tests passed")
    
    print("\n🎉 All authentication tests passed!")
