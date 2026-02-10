"""
Configuration settings for Toonify application
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Application Settings
APP_NAME = os.getenv("APP_NAME", "Toonify")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key_change_in_production")

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "users.db"))

# Payment Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
PAYMENT_AMOUNT = int(os.getenv("PAYMENT_AMOUNT", "299"))  # in cents
PAYMENT_CURRENCY = os.getenv("PAYMENT_CURRENCY", "usd")

# Razorpay Configuration (Alternative)
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

# Image Processing Settings
MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "10485760"))  # 10MB
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]
PROCESSED_IMAGE_QUALITY = int(os.getenv("PROCESSED_IMAGE_QUALITY", "95"))
TEMP_FOLDER = Path(os.getenv("TEMP_FOLDER", str(BASE_DIR / "data" / "processed_images")))

# Create necessary directories
TEMP_FOLDER.mkdir(parents=True, exist_ok=True)
Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)

# Session Settings
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour

# Cartoon Effect Parameters
CARTOON_PARAMS = {
    "bilateral_d": 9,
    "bilateral_sigma_color": 300,
    "bilateral_sigma_space": 300,
    "median_blur": 7,
    "adaptive_threshold_block_size": 9,
    "adaptive_threshold_c": 2,
    "num_colors": 8  # for color quantization
}

# Image Processing Styles
IMAGE_STYLES = {
    "Classic Cartoon": "cartoon",
    "Sketch Effect": "sketch",
    "Pencil Color": "pencil_color",
    "Oil Painting": "oil_painting",
    "Watercolor": "watercolor",
    "Pop Art": "pop_art",
    "Vintage": "vintage",
    "Anime": "anime",
    "Studio Ghibli": "ghibli",
    "Comic Book": "comic_book"
}

# Price per download (in dollars)
DOWNLOAD_PRICE = PAYMENT_AMOUNT / 100  # Convert cents to dollars

# SMTP Configuration for Real Emails
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")  # Add your gmail here
SMTP_PASS = os.getenv("SMTP_PASS", "")  # Add your gmail APP PASSWORD here
SMTP_SENDER = os.getenv("SMTP_SENDER", APP_NAME + " <no-reply@toonify.ai>")

# Real Google Auth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com")
