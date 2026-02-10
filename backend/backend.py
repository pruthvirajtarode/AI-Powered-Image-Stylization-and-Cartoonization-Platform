import os
import time
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect
from flask_cors import CORS
import cv2
import numpy as np
from pathlib import Path
from modules.image_processing import image_processor
from modules.authentication import auth
from modules.payment import payment_processor
from modules.database import db
from utils.helpers import create_directories, get_temp_filepath
from utils.validators import sanitize_filename
import config.settings as settings
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.secret_key = os.urandom(24)
CORS(app)

# --- LIVE HEARTBEAT ---
@app.before_request
def update_user_heartbeat():
    if 'user' in session and session['user'].get('id'):
        try:
            db.update_last_active(session['user']['id'])
        except:
            pass # Fail silently if DB is locked or busy during heartbeat

# Ensure directories exist
create_directories()

@app.route('/api/config')
def get_config():
    """Return public configuration for the frontend"""
    return jsonify({
        "razorpay_key": settings.RAZORPAY_KEY_ID or "rzp_test_DEMO_KEY",
        "google_client_id": settings.GOOGLE_CLIENT_ID,
        "download_price": settings.DOWNLOAD_PRICE,
        "app_name": settings.APP_NAME
    })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/tutorials')
def tutorials():
    return render_template('tutorials.html')

@app.route('/billing')
def billing():
    return render_template('billing.html')

@app.route('/security')
def security():
    return render_template('security.html')

@app.route('/our-story')
def our_story():
    return render_template('our_story.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_of_service.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template('dashboard.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/instagram')
def instagram():
    return render_template('instagram.html')

@app.route('/twitter')
def twitter():
    return render_template('twitter.html')

@app.route('/discord')
def discord():
    return render_template('discord.html')

@app.route('/api/user/history')
def get_user_performance():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    user_id = session['user']['id']
    history = db.get_user_history(user_id, limit=20)
    stats = db.get_user_stats(user_id)
    
    return jsonify({
        "success": True, 
        "history": history,
        "stats": stats
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    fullname = data.get('fullname')
    
    success, message = auth.register_user(username, email, password, fullname)
    return jsonify({"success": success, "message": message})

@app.route('/api/auth/verify', methods=['POST'])
def verify_email():
    data = request.json
    success, message = auth.verify_email_code(
        data.get('email'),
        data.get('code')
    )
    return jsonify({"success": success, "message": message})

@app.route('/api/auth/resend', methods=['POST'])
def resend_code():
    data = request.json
    success, message = auth.resend_verification_code(data.get('email'))
    return jsonify({"success": success, "message": message})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    success, user_data, message = auth.login_user(username, password)
    if success:
        session['user'] = user_data
        return jsonify({"success": True, "message": message, "user": user_data})
    
    # Return user_data even on fail if it's a verification requirement
    return jsonify({"success": False, "message": message, "user": user_data})

@app.route('/api/auth/google/verify', methods=['POST'])
def verify_google_token():
    try:
        data = request.json
        token = data.get('token')
        
        # Verify the REAL token from Google
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )

        # Token is valid. Get user details from Google's verified response
        user_email = idinfo['email']
        user_name = idinfo.get('name', user_email.split('@')[0])
        
        # Check if user exists in our DB or create them
        user = db.get_user_by_email(user_email)
        if not user:
            # Create a professional profile for new Google users
            user_id = db.create_user(
                username=user_name.replace(" ", "").lower() + "_" + str(uuid.uuid4())[:4],
                email=user_email,
                password_hash="GOOGLE_AUTH_EXTERNAL",
                full_name=user_name
            )
            
            if not user_id:
                return jsonify({"success": False, "message": "Failed to create your account in our database. Please contact support."})
                
            db.verify_user_email(user_email) # Google users are pre-verified
            user = db.get_user_by_id(user_id)
            
            if not user:
                return jsonify({"success": False, "message": "Account created but could not be retrieved. Handshake failed."})
                
            # Send Welcome Email
            try:
                auth.send_welcome_email(user_email, user_name)
            except:
                pass # Don't block login if welcome email fails
        
        # Prepare official user session
        session_user = {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "fullname": user['full_name'],
            "role": user['role']
        }
        
        session['user'] = session_user
        return jsonify({"success": True, "user": session_user, "message": "Production Google Login Successful!"})
        
    except Exception as e:
        import traceback
        print(f"ERROR: Google Auth Exception: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": f"Security Handshake Failed: {str(e)}"})

@app.route('/api/auth/google', methods=['POST'])
def google_login():
    # Mock Google Login Logic for Demo
    # In production, you would verify the ID token from Google here
    mock_google_user = {
        "id": "google_12345",
        "username": "Google_User",
        "email": "user@gmail.com",
        "role": "pro_member"
    }
    session['user'] = mock_google_user
    return jsonify({"success": True, "user": mock_google_user, "message": "Google Authentication Successful!"})

@app.route('/api/auth/logout')
def logout():
    user = session.get('user')
    if user and 'id' in user:
        db.update_last_logout(user['id'])
    session.pop('user', None)
    return jsonify({"success": True})

@app.route('/api/process', methods=['POST'])
def process():
    if 'user' not in session and not app.debug:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No image uploaded"}), 400
    
    file = request.files['image']
    style = request.form.get('style', 'cartoon')
    user_id = session['user'].get('id', 0) if 'user' in session else 0
    
    # Load image
    nparr = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return jsonify({"success": False, "message": "Invalid image"}), 400
    
    # Process
    processed_img, proc_time = image_processor.process_image(img, style)
    
    # Save processed image
    filename = f"processed_{uuid.uuid4().hex}.jpg"
    temp_path = Path("data/processed_images") / filename
    cv2.imwrite(str(temp_path), processed_img)
    
    # Log activity for admin
    if user_id:
        db.add_processing_history(user_id, file.filename, filename, style, proc_time)
        db.log_user_activity(user_id, "stylize", f"Created {style} art in {proc_time:.2f}s")
    
    return jsonify({
        "success": True,
        "processed_url": f"/data/processed/{filename}",
        "image_filename": filename,
        "proc_time": proc_time,
        "style": style
    })

# --- RAZORPAY PAYMENT ROUTES ---
@app.route('/api/payment/razorpay/order', methods=['POST'])
def create_razorpay_order():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Login required"}), 401
    
    user_id = session['user']['id']
    data = request.json
    amount = data.get('amount', settings.DOWNLOAD_PRICE)
    image_filename = data.get('image_filename')
    
    from modules.payment import razorpay_processor
    success, order, message = razorpay_processor.create_order(amount, user_id, image_filename)
    
    return jsonify({"success": success, "order": order, "message": message})

@app.route('/api/payment/razorpay/verify', methods=['POST'])
def verify_razorpay_payment():
    data = request.json
    from modules.payment import razorpay_processor
    
    success = razorpay_processor.verify_payment(
        data.get('razorpay_order_id'),
        data.get('razorpay_payment_id'),
        data.get('razorpay_signature')
    )
    
    if success and 'user' in session:
        db.log_user_activity(session['user']['id'], "payment", "Successful Razorpay transaction")
        
    return jsonify({"success": success})

# --- ADMIN DASHBOARD ROUTES ---
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session['user'].get('role') != 'admin':
            return jsonify({"success": False, "message": "Admin privileges required"}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
def admin_panel():
    if 'user' not in session or session['user'].get('role') != 'admin':
        return redirect('/') # Redirect to home if not admin
    return render_template('admin.html')

@app.route('/api/admin/stats')
@admin_required
def admin_stats():
    stats = db.get_admin_dashboard_stats()
    return jsonify({"success": True, "stats": stats})

@app.route('/api/admin/logs')
@admin_required
def admin_logs():
    logs = db.get_recent_activity_logs(limit=100)
    return jsonify({"success": True, "logs": logs})

@app.route('/api/admin/users')
@admin_required
def admin_users():
    users = db.get_all_users_admin()
    return jsonify({"success": True, "users": users})

@app.route('/api/admin/transactions')
@admin_required
def admin_transactions():
    transactions = db.get_all_transactions_admin()
    return jsonify({"success": True, "transactions": transactions})

@app.route('/data/processed/<filename>')
def get_processed_image(filename):
    return send_from_directory('data/processed_images', filename)

if __name__ == '__main__':
    # Flask in Debug mode with watchdog optimization
    app.run(debug=True, host='0.0.0.0', port=5000)
