"""
User authentication and authorization module
"""
import bcrypt
import re
from typing import Optional, Tuple
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from modules.database import db
import config.settings as settings


class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass


class Authentication:
    """Handle user authentication operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength
        Returns: (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, ""
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate username
        Returns: (is_valid, error_message)
        """
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 20:
            return False, "Username must not exceed 20 characters"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        return True, ""
    
    @staticmethod
    def register_user(username: str, email: str, password: str, 
                     full_name: str = None) -> Tuple[bool, str]:
        """
        Register a new user
        Returns: (success, message)
        """
        # Validate username
        valid, error = Authentication.validate_username(username)
        if not valid:
            return False, error
        
        # Validate email
        if not Authentication.validate_email(email):
            return False, "Invalid email format"
        
        # Validate password
        valid, error = Authentication.validate_password(password)
        if not valid:
            return False, error
        
        # Check if username already exists
        if db.get_user_by_username(username):
            return False, "Username already exists"
        
        # Check if email already exists
        if db.get_user_by_email(email):
            return False, "Email already registered"
        
        # Hash password and create user
        password_hash = Authentication.hash_password(password)
        user_id = db.create_user(username, email, password_hash, full_name)
        
        if user_id:
            # Generate and store verification code
            code = str(random.randint(100000, 999999))
            expiry = datetime.now() + timedelta(minutes=10)
            db.store_verification_code(email, code, expiry)
            
            # Attempt Real Email Delivery
            email_sent = Authentication.send_verification_email(email, code)
            
            if email_sent:
                return True, f"Security code sent! Please check your inbox (and spam folder) at {email}."
            else:
                # If email fails, we don't leak the code in production.
                # We notify the user that the mail server is currently being tuned.
                return False, "Verification system is temporarily offline. Please try again in a few minutes or contact support."
        else:
            return False, "Registration failed. Database error."

    @staticmethod
    def send_verification_email(receiver_email: str, code: str) -> bool:
        """Send actual verification email using SMTP"""
        if not settings.SMTP_USER or not settings.SMTP_PASS:
            print("WARNING: SMTP credentials not set. Falling back to console log.")
            print(f"DEBUG: Verification code for {receiver_email} is {code}")
            return False

        try:
            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_SENDER
            msg['To'] = receiver_email
            msg['Subject'] = f"{settings.APP_NAME} - Verify Your Account"

            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e1e1e1; border-radius: 10px;">
                        <h2 style="color: #4A90E2; text-align: center;">Welcome to {settings.APP_NAME}!</h2>
                        <p>Hi there,</p>
                        <p>Thank you for joining our AI Stylization platform. To complete your registration, please use the following verification code:</p>
                        <div style="background: #f4f4f4; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0;">
                            <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #1e293b;">{code}</span>
                        </div>
                        <p>This code will expire in 10 minutes. If you did not sign up for an account, please ignore this email.</p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="font-size: 12px; color: #888; text-align: center;">&copy; 2026 {settings.APP_NAME}.AI - Powered by Neural Engine</p>
                    </div>
                </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html'))

            # Setup SMTP server
            server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
            server.starttls()  # Secure the connection
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            
            # Send email
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"ERROR: Failed to send email: {e}")
            return False

    @staticmethod
    def send_welcome_email(receiver_email: str, name: str) -> bool:
        """Send a welcome email to new users (e.g. Google Login)"""
        if not settings.SMTP_USER or not settings.SMTP_PASS:
            print(f"DEBUG: Welcome email would be sent to {receiver_email}")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_SENDER
            msg['To'] = receiver_email
            msg['Subject'] = f"Welcome to {settings.APP_NAME}!"

            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e1e1e1; border-radius: 10px;">
                        <h2 style="color: #4A90E2; text-align: center;">🎨 Welcome aboard, {name}!</h2>
                        <p>Hi {name},</p>
                        <p>We're thrilled to have you at <strong>{settings.APP_NAME}</strong>. Your account has been successfully created via Google Authentication.</p>
                        <p>You can now start transforming your photos into artistic masterpieces using our 9 premium neural styles.</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="http://localhost:5000" style="background: #4A90E2; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Launch Neural Editor</a>
                        </div>
                        <p>If you have any questions, simply reply to this email.</p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="font-size: 12px; color: #888; text-align: center;">&copy; 2026 {settings.APP_NAME}.AI - The Future of Image Stylization</p>
                    </div>
                </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"ERROR: Failed to send welcome email: {e}")
            return False

    @staticmethod
    def verify_email_code(email: str, code: str) -> Tuple[bool, str]:
        """Verify the 6-digit code sent to user's email"""
        entry = db.get_verification_code(email)
        if not entry:
            return False, "No verification code found for this email."
        
        if entry['code'] != code:
            return False, "Invalid verification code."
        
        # Check expiry
        if datetime.strptime(entry['expires_at'], '%Y-%m-%d %H:%M:%S.%f') < datetime.now():
            return False, "Verification code has expired."
        
        db.verify_user_email(email)
        return True, "Email verified successfully! You can now log in."

    @staticmethod
    def resend_verification_code(email: str) -> Tuple[bool, str]:
        """Generate and resend a new verification code"""
        user = db.get_user_by_email(email)
        if not user:
            return False, "User not found."
        
        if user.get('is_verified', False):
            return False, "Email already verified."
        
        # New code
        code = str(random.randint(100000, 999999))
        expiry = datetime.now() + timedelta(minutes=10)
        db.store_verification_code(email, code, expiry)
        
        # Send Email
        sent = Authentication.send_verification_email(email, code)
        if sent:
            return True, f"New code sent to {email}."
        else:
            # Professional Fallback for Development
            print(f"✅ REAL PROJECT READY: NEW Verification code for {email} is {code}")
            return True, f"New code generated! [DEV MODE]: Your real code is {code}. Setup SMTP in .env for actual delivery."
    
    @staticmethod
    def login_user(username: str, password: str) -> Tuple[bool, Optional[dict], str]:
        """
        Log in a user
        Returns: (success, user_data, message)
        """
        # Get user by username or email
        user = db.get_user_by_username(username)
        if not user:
            user = db.get_user_by_email(username)
        
        if not user:
            return False, None, "Invalid username or password"
        
        # Verify password
        if not Authentication.verify_password(password, user['password_hash']):
            return False, None, "Invalid username or password"
        
        # Check if user is active
        if not user.get('is_active', True):
            return False, None, "Account is deactivated. Please contact support."
        
        # Check if email is verified
        if not user.get('is_verified', False):
            # Return email so frontend knows which email to verify
            return False, {"email": user['email']}, "VERIFY_REQUIRED"
        
        # Update last login
        db.update_last_login(user['id'])
        
        # Remove password hash from user data
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return True, user_data, "Login successful!"
    
    @staticmethod
    def init_session_state():
        """Initialize session state for authentication"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'login'
    
    @staticmethod
    def logout():
        """Log out the current user"""
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.current_page = 'login'
        if 'processed_image' in st.session_state:
            del st.session_state.processed_image
        if 'original_image' in st.session_state:
            del st.session_state.original_image
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    @staticmethod
    def get_current_user() -> Optional[dict]:
        """Get current logged-in user"""
        return st.session_state.get('user', None)
    
    @staticmethod
    def require_auth(func):
        """Decorator to require authentication for a function"""
        def wrapper(*args, **kwargs):
            if not Authentication.is_authenticated():
                st.warning("⚠️ Please log in to access this feature")
                st.stop()
            return func(*args, **kwargs)
        return wrapper


# Create global auth instance
auth = Authentication()
