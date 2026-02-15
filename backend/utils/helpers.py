"""
Helper utility functions
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
import config.settings as settings


def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
    """
    Generate a unique filename using UUID
    """
    extension = original_filename.rsplit('.', 1)[-1]
    unique_id = uuid.uuid4().hex[:12]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if prefix:
        return f"{prefix}_{timestamp}_{unique_id}.{extension}"
    return f"{timestamp}_{unique_id}.{extension}"


def get_temp_filepath(filename: str, user_id: int = None) -> Path:
    """
    Get temporary file path for processed images
    """
    if user_id:
        user_folder = settings.TEMP_FOLDER / f"user_{user_id}"
        user_folder.mkdir(exist_ok=True)
        return user_folder / filename
    return settings.TEMP_FOLDER / filename


def cleanup_old_files(directory: Path, hours: int = 24):
    """
    Clean up files older than specified hours
    """
    if not directory.exists():
        return
    
    from datetime import timedelta
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    for file_path in directory.glob("*"):
        if file_path.is_file():
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_time < cutoff_time:
                try:
                    file_path.unlink()
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format
    """
    if seconds < 1:
        return f"{seconds*1000:.0f} ms"
    elif seconds < 60:
        return f"{seconds:.1f} sec"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"


def get_user_folder(user_id: int) -> Path:
    """Get user-specific folder path"""
    folder = settings.TEMP_FOLDER / f"user_{user_id}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def create_directories():
    """Create all necessary directories for the application"""
    directories = [
        settings.TEMP_FOLDER,
        Path(settings.DATABASE_PATH).parent,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def get_style_display_name(style_key: str) -> str:
    """Get display name for a style key"""
    display_names = {
        "cartoon": "Classic Cartoon",
        "sketch": "Sketch Effect",
        "pencil_color": "Pencil Color",
        "oil_painting": "Oil Painting"
    }
    return display_names.get(style_key, style_key)


def get_app_info() -> dict:
    """Get application information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "styles_available": len(settings.IMAGE_STYLES),
        "max_file_size": format_file_size(settings.MAX_IMAGE_SIZE),
        "price": f"${settings.DOWNLOAD_PRICE:.2f}"
    }
