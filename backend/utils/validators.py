"""
Validation utilities
"""
import os
from typing import Tuple
import config.settings as settings


def validate_file_size(file) -> Tuple[bool, str]:
    """
    Validate uploaded file size
    Returns: (is_valid, message)
    """
    try:
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > settings.MAX_IMAGE_SIZE:
            max_mb = settings.MAX_IMAGE_SIZE / (1024 * 1024)
            return False, f"File size exceeds {max_mb}MB limit"
        
        return True, "File size valid"
    except Exception as e:
        return False, f"Error validating file size: {str(e)}"


def validate_file_extension(filename: str) -> Tuple[bool, str]:
    """
    Validate file extension
    Returns: (is_valid, message)
    """
    if not filename:
        return False, "No filename provided"
    
    extension = filename.rsplit('.', 1)[-1].lower()
    
    if extension not in settings.ALLOWED_EXTENSIONS:
        allowed = ", ".join(settings.ALLOWED_EXTENSIONS)
        return False, f"Invalid file type. Allowed: {allowed}"
    
    return True, "File type valid"


def validate_image_file(file, filename: str) -> Tuple[bool, str]:
    """
    Validate uploaded image file
    Returns: (is_valid, message)
    """
    # Check extension
    valid, message = validate_file_extension(filename)
    if not valid:
        return valid, message
    
    # Check file size
    valid, message = validate_file_size(file)
    if not valid:
        return valid, message
    
    return True, "File is valid"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent security issues
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove special characters except dots and underscores
    import re
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    
    return filename


def is_valid_transaction_id(transaction_id: str) -> bool:
    """Validate transaction ID format"""
    if not transaction_id:
        return False
    
    # Check if it starts with expected prefix
    valid_prefixes = ['txn_', 'demo_', 'pi_']
    return any(transaction_id.startswith(prefix) for prefix in valid_prefixes)
