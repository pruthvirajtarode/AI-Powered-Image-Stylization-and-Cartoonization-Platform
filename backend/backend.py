import os
import time
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, send_file
from flask_cors import CORS
import cv2
import numpy as np
from pathlib import Path
from modules.image_processing import image_processor
from modules.authentication import auth
from PIL import Image
import io
from modules.payment import payment_processor
from modules.database import db
from modules.whatsapp import whatsapp_processor
from utils.helpers import create_directories, get_temp_filepath
from utils.validators import sanitize_filename
import config.settings as settings
from google.oauth2 import id_token
from google.auth.transport import requests
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.secret_key = settings.SECRET_KEY or os.urandom(24)
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
    if 'user' not in session:
        return redirect('/')
    return render_template('billing.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/')
    return render_template('profile.html')

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
    
    # Background Cleanup (Simple trigger)
    try:
        filenames = db.cleanup_old_history(session['user']['id'])
        for f in filenames:
            path = settings.TEMP_FOLDER / f
            if path.exists(): path.unlink()
    except: pass
    
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
    history = db.get_user_history(user_id, limit=10) # Recent 10
    stats = db.get_user_stats(user_id)
    stats['usage_24h'] = db.get_user_usage_24h(user_id)
    
    # We no longer check .exists() on every file here, as it slows down the API significantly.
    # The frontend handles missing images via the 'onerror' event for better performance.
    for item in history:
        item['is_missing'] = False 
    
    return jsonify({
        "success": True, 
        "history": history,
        "stats": stats
    })

@app.route('/api/user/transactions')
def get_user_transactions():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    user_id = session['user']['id']
    transactions = db.get_user_transactions(user_id)
    return jsonify({
        "success": True,
        "transactions": transactions
    })

@app.route('/api/auth/session')
def check_session():
    if 'user' in session:
        return jsonify({"success": True, "user": session['user']})
    return jsonify({"success": False, "message": "No active session"})

@app.route('/api/user/profile')
def get_user_profile():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    user_id = session['user']['id']
    user = db.get_user_by_id(user_id)
    if user:
        # Don't send password hash
        user.pop('password_hash', None)
        return jsonify({"success": True, "user": user})
    return jsonify({"success": False, "message": "User not found"}), 404

@app.route('/api/user/profile/update', methods=['POST'])
def update_profile():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    data = request.json
    user_id = session['user']['id']
    
    # Check for password change
    if 'new_password' in data and data['new_password']:
        import bcrypt
        pw = bcrypt.hashpw(data['new_password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.change_password(user_id, pw)
        
    # Check for settings update
    if 'auto_delete_days' in data:
        db.update_user_settings(user_id, int(data['auto_delete_days']))

    success = db.update_user_profile(
        user_id, 
        full_name=data.get('fullname'),
        email=data.get('email')
    )
    
    if success:
        # Update session data
        updated_user = db.get_user_by_id(user_id)
        session['user']['fullname'] = updated_user['full_name']
        session['user']['email'] = updated_user['email']
        return jsonify({"success": True, "message": "Profile and settings updated successfully"})
    
    return jsonify({"success": False, "message": "Failed to update profile"})

@app.route('/api/user/history/advanced')
def get_advanced_history():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    user_id = session['user']['id']
    style = request.args.get('style', 'all')
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'DESC')
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    
    history_data = db.get_advanced_history(user_id, style, sort_by, order, limit, offset)
    
    # We no longer check .exists() on every file here, as it slows down the API significantly.
    # The frontend handles missing images via the 'onerror' event for better performance.
    for item in history_data.get('items', []):
        item['is_missing'] = False 
        
    return jsonify({"success": True, "data": history_data})

@app.route('/api/user/history/delete', methods=['POST'])
def delete_history():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    user_id = session['user']['id']
    data = request.json
    history_id = data.get('history_id') # If None, delete all
    
    filenames = db.delete_user_history(user_id, history_id)
    
    # Physically delete files
    for filename in filenames:
        try:
            path = settings.TEMP_FOLDER / filename
            if path.exists(): path.unlink()
        except: pass
        
    return jsonify({"success": True, "message": "History deleted successfully"})

@app.route('/api/user/history/download-all')
def download_all_history():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    user_id = session['user']['id']
    history = db.get_user_history(user_id, limit=100)
    
    if not history:
        return jsonify({"success": False, "message": "No history to download"}), 404
        
    import io
    import zipfile
    from flask import send_file
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for item in history:
            filename = item['processed_filename']
            file_path = settings.TEMP_FOLDER / filename
            if file_path.exists():
                zip_file.write(file_path, arcname=filename)
                
    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"toonify_gallery_{user_id}.zip"
    )

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
            "role": user['role'],
            "created_at": user['created_at'].isoformat() if hasattr(user['created_at'], 'isoformat') else user['created_at']
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
    is_premium = session['user'].get('role') == 'admin' or session['user'].get('plan') in ['pro', 'elite']
    processed_img, proc_time = image_processor.process_image(img, style, is_premium=is_premium)
    
    # Save processed image
    filename = f"processed_{uuid.uuid4().hex}.jpg"
    temp_path = settings.TEMP_FOLDER / filename
    cv2.imwrite(str(temp_path), processed_img)
    
    # Log activity for admin
    if user_id:
        db.add_processing_history(user_id, file.filename, filename, style, proc_time)
        db.log_user_activity(user_id, "stylize", f"Created {style} art in {proc_time:.2f}s")
    
    # Calculate Statistics (Task 13)
    original_stats = image_processor.get_image_statistics(img)
    processed_stats = image_processor.get_image_statistics(processed_img)

    return jsonify({
        "success": True,
        "processed_url": f"/data/processed/{filename}",
        "image_filename": filename,
        "proc_time": proc_time,
        "style": style,
        "stats": {
            "original": original_stats,
            "processed": processed_stats
        }
    })

@app.route('/api/process/batch', methods=['POST'])
def process_batch():
    if 'user' not in session and not app.debug:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    if 'images' not in request.files:
        return jsonify({"success": False, "message": "No images uploaded"}), 400

    files = request.files.getlist('images')
    styles_raw = request.form.get('styles', 'cartoon')
    style_list = styles_raw.split(',')

    user = session.get('user', {})
    user_id = user.get('id', 0)
    user_plan = user.get('plan', 'starter')
    user_role = user.get('role', 'user')

    # Quota check for Starter plan (Admins and Pro members are exempt)
    if user_id and user_role != 'admin' and user_plan == 'starter':
        usage_today = db.get_user_usage_24h(user_id)
        if (usage_today + len(files)) > 5:
            return jsonify({
                "success": False, 
                "message": f"Daily limit reached (5 images/day for Starter). You have processed {usage_today} images today. Upgrade to Pro for unlimited access!",
                "limit_reached": True
            }), 402

    results = [None] * len(files)
    
    def process_single_task(index, file, style):
        try:
            # Read image
            img_bytes = file.read()
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return {"success": False, "original_filename": file.filename, "message": "Invalid image"}
                
            # Stylize
            user_plan = user.get('plan', 'starter')
            user_role = user.get('role', 'user')
            is_premium = user_role == 'admin' or user_plan in ['pro', 'elite']
            processed_img, proc_time = image_processor.process_image(img, style, is_premium=is_premium)
            
            # Sub-Task 13: Analysis Stats
            orig_stats = image_processor.get_image_stats(img)
            proc_stats = image_processor.get_image_stats(processed_img)
            
            # Save
            filename = f"processed_{uuid.uuid4().hex}.jpg"
            temp_path = settings.TEMP_FOLDER / filename
            cv2.imwrite(str(temp_path), processed_img, [cv2.IMWRITE_JPEG_QUALITY, 90])
            
            # Database tasks
            if user_id:
                db.add_processing_history(user_id, file.filename, filename, style, proc_time)
            
            return {
                "success": True,
                "original_filename": file.filename,
                "processed_url": f"/data/processed/{filename}",
                "image_filename": filename,
                "proc_time": proc_time,
                "style": style,
                "stats": {
                    "original": orig_stats,
                    "processed": proc_stats
                }
            }
        except Exception as e:
            return {"success": False, "original_filename": file.filename, "message": str(e)}

    # Launch parallel neural tasks
    max_workers = min(os.cpu_count() or 4, len(files))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i, file in enumerate(files):
            style = style_list[i] if i < len(style_list) else style_list[-1]
            futures.append(executor.submit(process_single_task, i, file, style))
        
        for i, future in enumerate(futures):
            results[i] = future.result()

    return jsonify({
        "success": True,
        "results": results
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

@app.route('/api/payment/subscribe', methods=['POST'])
def subscribe_plan():
    """Verify a Razorpay payment and upgrade the user's subscription plan."""
    if 'user' not in session:
        return jsonify({"success": False, "message": "Login required"}), 401

    data = request.json
    plan = data.get('plan')  # 'pro' or 'elite'
    if plan not in ('pro', 'elite'):
        return jsonify({"success": False, "message": "Invalid plan"}), 400

    from modules.payment import razorpay_processor
    success = razorpay_processor.verify_payment(
        data.get('razorpay_order_id'),
        data.get('razorpay_payment_id'),
        data.get('razorpay_signature')
    )

    if success:
        user_id = session['user']['id']
        updated = db.update_user_plan(user_id, plan)
        if updated:
            session['user']['plan'] = plan
            db.log_user_activity(user_id, "subscription", f"Upgraded to {plan}")
            return jsonify({"success": True, "plan": plan})
        else:
            return jsonify({"success": False, "message": "Plan update failed"}), 500

    return jsonify({"success": False, "message": "Payment verification failed"}), 400

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

from itsdangerous import URLSafeTimedSerializer
download_serializer = URLSafeTimedSerializer(app.secret_key)

@app.route('/api/user/check-payment')
def check_payment_status():
    """Check if user has paid for a specific image"""
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized", "has_paid": False}), 401
    
    filename = request.args.get('filename')
    user_id = session['user']['id']
    
    # Pro/Elite/Admin users don't need to pay for single downloads
    is_premium = session['user'].get('role') == 'admin' or session['user'].get('plan') in ['pro', 'elite']
    if is_premium:
        return jsonify({"success": True, "has_paid": True, "message": "Premium user (Unlimited Access)"})
    
    # Check if payment exists for this image
    transaction = db.get_transaction_by_filename(user_id, filename)
    
    if transaction and transaction['status'] == 'completed':
        return jsonify({"success": True, "has_paid": True, "message": "Payment verified"})
    
    return jsonify({"success": True, "has_paid": False, "message": "Payment required"})

@app.route('/api/user/download-token')
def get_download_token():
    """Generate a temporary signed token for download (Task 17)"""
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    filename = request.args.get('filename')
    user_id = session['user']['id']
    
    # Verify payment / Premium status
    is_premium = session['user'].get('role') == 'admin' or session['user'].get('plan') in ['pro', 'elite']
    transaction = db.get_transaction_by_filename(user_id, filename)
    
    if not is_premium and (not transaction or transaction['status'] != 'completed'):
        return jsonify({"success": False, "message": "Payment required"}), 402

    token = download_serializer.dumps({"u": user_id, "f": filename})
    return jsonify({"success": True, "token": token})

@app.route('/api/user/download')
def secure_download():
    """
    Secure download endpoint for Task 14 & 17.
    Enforces payment requirement for non-pro users.
    Supports JWT-style signed tokens or active session.
    """
    token = request.args.get('token')
    filename = request.args.get('filename')
    format_ext = request.args.get('format', 'jpg').lower()
    quality = int(request.args.get('quality', 95))
    
    # Access via Token (Task 17: Temporary Link)
    if token:
        try:
            data = download_serializer.loads(token, max_age=3600) # 1 hour validity
            filename = data['f']
            user_id = data['u']
            is_pro = False  # Token users still need to have paid
        except:
            return "Invalid or expired download link", 403
    elif 'user' in session:
        user_id = session['user']['id']
        is_premium = session['user'].get('role') == 'admin' or session['user'].get('plan') in ['pro', 'elite']
    else:
        return "Authentication required", 401

    if not filename:
        return "Filename missing", 400
    
    # STRICT: Always verify payment for non-pro users
    # Even if via session, check that payment was completed
    if not is_pro:
        transaction = db.get_transaction_by_filename(user_id, filename)
        if not transaction or transaction['status'] != 'completed':
            # Return 402 Payment Required status
            return jsonify({"success": False, "message": "Payment required to download this image"}), 402
        
    # Process Format Conversion (Task 14)
    file_path = settings.TEMP_FOLDER / filename
    if not file_path.exists():
        return "File not found", 404
        
    img = cv2.imread(str(file_path))
    
    import io
    from flask import send_file
    
    if format_ext == 'png':
        _, img_encoded = cv2.imencode('.png', img)
        return send_file(io.BytesIO(img_encoded), mimetype='image/png', as_attachment=True, download_name=f"toonify_{filename.replace('.jpg', '.png')}")
    
    elif format_ext == 'pdf':
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        pdf_buffer = io.BytesIO()
        pil_img.save(pdf_buffer, format='PDF')
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=f"toonify_{filename.replace('.jpg', '.pdf')}")
        
    else: # Default JPG
        _, img_encoded = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, quality])
        return send_file(io.BytesIO(img_encoded), mimetype='image/jpeg', as_attachment=True, download_name=f"toonify_{filename}")

@app.route('/data/processed/<filename>')
def get_processed_image(filename):
    """
    Serve processed images with high-performance caching for Task 14.
    If the user has paid (or is Pro), serve un-watermarked.
    Otherwise, serve a cached watermarked version.
    """
    file_path = settings.TEMP_FOLDER / filename
    if not file_path.exists():
        return "Not found", 404
    
    # Check if thumbnail requested for gallery performance
    is_thumb = request.args.get('thumb', '0') == '1'
    
    # Check if we should watermark
    should_watermark = True
    if 'user' in session:
        user_id = session['user']['id']
        is_pro = session['user'].get('role') in ['admin', 'pro_member']
        transaction = db.get_transaction_by_filename(user_id, filename)
        if is_pro or (transaction and transaction['status'] == 'completed'):
            should_watermark = False
            
    if not should_watermark:
        # Paid users get the real deal immediately
        if is_thumb:
            thumb_path = settings.CACHE_FOLDER / "thumbnails" / f"thumb_{filename}"
            if not thumb_path.exists():
                img = cv2.imread(str(file_path))
                if img is not None:
                    h, w = img.shape[:2]
                    scale = 400 / w
                    thumb = cv2.resize(img, (400, int(h * scale)))
                    cv2.imwrite(str(thumb_path), thumb, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if thumb_path.exists():
                response = send_from_directory(settings.CACHE_FOLDER / "thumbnails", f"thumb_{filename}")
                response.headers['Cache-Control'] = 'public, max-age=31536000'
                return response
        
        return send_from_directory(settings.TEMP_FOLDER, filename)
    
    # Caching Logic for Watermarked results
    cache_subdir = "thumbnails" if is_thumb else "watermarked"
    prefix = "thumb_wm_" if is_thumb else "wm_"
    cache_filename = f"{prefix}{filename}"
    cache_path = settings.CACHE_FOLDER / cache_subdir / cache_filename
    
    # Return cached version if exists
    if cache_path.exists():
        response = send_from_directory(settings.CACHE_FOLDER / cache_subdir, cache_filename)
        response.headers['Cache-Control'] = 'public, max-age=31536000'
        return response
    
    # Generate and Store in Cache
    img = cv2.imread(str(file_path))
    if img is None:
        return send_from_directory(settings.TEMP_FOLDER, filename)
    
    # Add a professional watermark
    h, w = img.shape[:2]
    watermark_text = "TOONIFY AI PREVIEW"
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    if is_thumb:
        # Resize first for thumbnail speed
        scale_w = 400 / w
        img = cv2.resize(img, (400, int(h * scale_w)))
        h, w = img.shape[:2]
        font_scale = 0.6
        thickness = 1
    else:
        font_scale = w / 1000 
        thickness = max(1, int(2 * font_scale))
    
    # Semi-transparent overlay
    overlay = img.copy()
    cv2.putText(overlay, watermark_text, (int(w*0.1), int(h*0.9)), font, font_scale, (255, 255, 255), thickness)
    cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)
    
    # Save to Cache
    cv2.imwrite(str(cache_path), img, [cv2.IMWRITE_JPEG_QUALITY, 85])
    
    response = send_file(str(cache_path), mimetype='image/jpeg')
    # Add aggressive caching for these static-ish assets
    response.headers['Cache-Control'] = 'public, max-age=31536000' # 1 year
    return response

# --- WHATSAPP WEBHOOK ROUTES ---
@app.route('/api/whatsapp/webhook', methods=['GET'])
def whatsapp_verify_webhook():
    """
    Webhook verification endpoint for WhatsApp Business API
    Called by WhatsApp to verify webhook authenticity
    """
    verify_token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    result = whatsapp_processor.verify_webhook(verify_token, challenge)
    if result:
        return result
    
    return jsonify({"error": "Webhook verification failed"}), 403


@app.route('/api/whatsapp/webhook', methods=['POST'])
def whatsapp_handle_webhook():
    """
    Webhook endpoint for receiving WhatsApp messages
    Processes incoming media (images) for stylization
    """
    try:
        body = request.get_json()
        
        # Check if this is a message event
        if body.get('object') == 'whatsapp_business_account':
            changes = body.get('entry', [{}])[0].get('changes', [{}])[0]
            
            # Check for message changes
            if changes.get('field') == 'messages':
                messages = changes.get('value', {}).get('messages', [])
                
                for message in messages:
                    # Only process image messages for now
                    if message.get('type') == 'image':
                        # Handle the message asynchronously
                        process_whatsapp_image(message)
                    
                    elif message.get('type') == 'text':
                        # Handle text message
                        process_whatsapp_text(message)
        
        # Always return 200 OK to WhatsApp
        return jsonify({"success": True}), 200
    
    except Exception as e:
        import traceback
        print(f"ERROR: WhatsApp webhook error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/api/post-process/background', methods=['POST'])
def post_process_bg():
    if 'user' not in session: return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    data = request.json
    filename = data.get('filename')
    bg_type = data.get('bg_type') # 'tokyo', 'cyberpunk', 'forest'
    
    file_path = settings.TEMP_FOLDER / filename
    if not file_path.exists(): return jsonify({"success": False, "message": "File not found"}), 404
    
    img = cv2.imread(str(file_path))
    processed = image_processor.teleport_background(img, bg_type)
    
    new_filename = f"bg_{uuid.uuid4().hex}.jpg"
    cv2.imwrite(str(settings.TEMP_FOLDER / new_filename), processed)
    
    return jsonify({"success": True, "filename": new_filename})

@app.route('/api/post-process/animate', methods=['POST'])
def post_process_animate():
    if 'user' not in session: return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    data = request.json
    filename = data.get('filename')
    
    file_path = settings.TEMP_FOLDER / filename
    if not file_path.exists(): return jsonify({"success": False, "message": "File not found"}), 404
    
    img = cv2.imread(str(file_path))
    gif_bytes = image_processor.create_toon_mo(img)
    
    gif_filename = f"anim_{uuid.uuid4().hex}.gif"
    with open(settings.TEMP_FOLDER / gif_filename, "wb") as f:
        f.write(gif_bytes)
        
    return jsonify({"success": True, "filename": gif_filename})

@app.route('/api/web3/mint', methods=['POST'])
def mint_nft():
    if 'user' not in session: return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    # Mock NFT minting on Polygon Testnet for high-tech SaaS feel
    import time
    time.sleep(1.5) # Simulate blockchain consensus latency
    
    tx_hash = f"0x{uuid.uuid4().hex}{uuid.uuid4().hex}"[:66]
    return jsonify({
        "success": True, 
        "message": "Asset officially minted on Polygon PoS!",
        "tx_hash": tx_hash,
        "opensea_url": f"https://opensea.io/assets/matic/{tx_hash}"
    })

@app.route('/api/process/dna', methods=['POST'])
def process_dna():
    if 'user' not in session: return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    if 'target' not in request.files or 'reference' not in request.files:
        return jsonify({"success": False, "message": "Missing target or reference image"}), 400
        
    target_file = request.files['target']
    ref_file = request.files['reference']
    
    # Load images
    nparr_t = np.frombuffer(target_file.read(), np.uint8)
    img_t = cv2.imdecode(nparr_t, cv2.IMREAD_COLOR)
    
    nparr_r = np.frombuffer(ref_file.read(), np.uint8)
    img_r = cv2.imdecode(nparr_r, cv2.IMREAD_COLOR)
    
    if img_t is None or img_r is None:
        return jsonify({"success": False, "message": "Invalid image data"}), 400
        
    # Apply DNA transfer
    dna_result = image_processor.apply_style_dna(img_t, img_r)
    
    filename = f"dna_{uuid.uuid4().hex}.jpg"
    cv2.imwrite(str(settings.TEMP_FOLDER / filename), dna_result)
    
    return jsonify({"success": True, "filename": filename})


def process_whatsapp_image(message_data):
    """
    Process incoming WhatsApp image for stylization
    
    Args:
        message_data: Message data from WhatsApp webhook
    """
    try:
        # Parse incoming message
        result = whatsapp_processor.handle_incoming_message(message_data)
        
        if not result.get('success'):
            print(f"Failed to handle WhatsApp message: {result.get('error')}")
            return
        
        if result.get('type') != 'image':
            return
        
        # Get image path
        local_path = result.get('local_path')
        sender_phone = result.get('sender_phone')
        message_id = result.get('message_id')
        
        # Read and process image
        try:
            img = cv2.imread(local_path)
            if img is None:
                whatsapp_processor.send_message(sender_phone, 
                    "❌ Invalid image format. Please try again.")
                return
            
            # Default style is cartoon
            style = 'cartoon'
            
            # Process image (WhatsApp users are standard by default unless phone recognized)
            processed_img, proc_time = image_processor.process_image(img, style, is_premium=False)
            
            # Save processed image
            filename = f"whatsapp_processed_{uuid.uuid4().hex}.jpg"
            temp_path = settings.TEMP_FOLDER / filename
            cv2.imwrite(str(temp_path), processed_img)
            
            # Send status update
            whatsapp_processor.send_message(sender_phone, 
                f"✨ Processing complete in {proc_time:.2f}s!\n\nSending your stylized image...")
            
            # Send stylized image back
            whatsapp_processor.send_stylized_image(sender_phone, str(temp_path), "Cartoon")
            
            # Log activity if user is authenticated
            print(f"✅ WhatsApp image processed successfully from {sender_phone}")
        
        except Exception as e:
            print(f"Error processing WhatsApp image: {str(e)}")
            whatsapp_processor.send_message(sender_phone, 
                "❌ Sorry! Error processing your image. Please try again.")
    
    except Exception as e:
        print(f"Error in process_whatsapp_image: {str(e)}")


def process_whatsapp_text(message_data):
    """
    Process incoming WhatsApp text message
    
    Args:
        message_data: Message data from WhatsApp webhook
    """
    try:
        result = whatsapp_processor.handle_incoming_message(message_data)
        if not result.get('success'):
            print(f"Failed to handle text message: {result.get('error')}")
    
    except Exception as e:
        print(f"Error in process_whatsapp_text: {str(e)}")


    # Flask in Debug mode with watchdog optimization
    app.run(debug=True, host='0.0.0.0', port=5000)
