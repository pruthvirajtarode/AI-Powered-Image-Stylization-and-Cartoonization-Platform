# Quick Setup Guide: Camera & WhatsApp Features

## ✅ Camera Capture - READY TO USE
The camera capture feature is **fully functional** and requires no additional setup!

**To use:**
1. Open your Toonify AI app
2. Click the **📷 Camera** button in the "Media Asset" section
3. Allow camera permission when prompted
4. Click **Capture Photo** or switch cameras as needed
5. Your photo appears ready for transformation!

---

## 🚀 WhatsApp Integration - REQUIRES SETUP

### Step 1: Get WhatsApp Business Number
Visit: https://www.whatsapp.com/business/

**For Testing Without WhatsApp:**
- You can still click WhatsApp button - it shows instructions
- Replace phone number with your personal number to test
- In production, use your WhatsApp Business verified number

### Step 2: Update Phone Number
Edit `frontend/static/js/app.js`:

**Find this line (around line 162):**
```javascript
const phoneNumber = '919876543210'; // Replace with your number
```

**Replace with your WhatsApp number:**
```javascript
const phoneNumber = '911234567890'; // Your actual WhatsApp Business number
```

**Format Examples:**
- 🇮🇳 India: `919876543210` (country code 91 + number without +)
- 🇺🇸 US: `14155552671` (country code 1 + number)
- 🇬🇧 UK: `441632960000` (country code 44 + number)

### Step 3: Test It
1. Log in to your app
2. Click **💬 WhatsApp** button
3. Click **"Open WhatsApp"**
4. You should be redirected to WhatsApp conversation

---

## 📱 Mobile Configuration

### iOS (iPhone)
- ✅ Works with Safari 14.1+
- ✅ Works with built-in browsers
- Requires iPhone 15 or later for full camera feature
- HTTPS required

### Android
- ✅ Works with Chrome
- ✅ Works with Firefox
- ✅ Works with Edge
- Supports all recent Android versions (8+)
- HTTP works on localhost for testing

### Desktop
- ✅ Webcam support (Chrome, Edge, Firefox)
- ✅ Webcam selection if multiple cameras connected
- HTTPS required in production

---

## 🔧 Advanced: Enable Backend Webhook (Optional)

If you want WhatsApp images to automatically process:

### 1. Set Up WhatsApp Business API
```bash
pip install twilio==8.10.0
```

### 2. Add to `.env`
```
WHATSAPP_ACCOUNT_SID=your_sid
WHATSAPP_AUTH_TOKEN=your_token
WHATSAPP_PHONE_ID=your_phone_id
```

### 3. Update `backend/backend.py`
Add this after the existing routes:
```python
@app.route('/api/whatsapp/webhook', methods=['POST', 'GET'])
def whatsapp_webhook():
    """WhatsApp webhook handler"""
    if request.method == 'GET':
        # Webhook verification
        return request.args.get('hub.challenge', ''), 200
    
    data = request.get_json()
    # Process incoming WhatsApp messages
    # Extract media, download, and store
    
    return jsonify({"success": True})
```

### 4. Set Webhook in WhatsApp Dashboard
- Go to WhatsApp Business API settings
- Set webhook URL: `https://yourdomain.com/api/whatsapp/webhook`
- Subscribe to: `messages` event

---

## ✨ Features Summary

| Feature | Status | Setup Required |
|---------|--------|------------------|
| 📷 Camera Capture | ✅ Ready | No - works out of box |
| 💬 WhatsApp Modal | ✅ Ready | No - shows instructions |
| 📬 WhatsApp Auto-Process | ⏳ Optional | Yes - requires API setup |
| 🔄 Switch Camera | ✅ Ready | No |
| 🎥 Video Recording | ⏳ Coming Soon | N/A |

---

## 🧪 Testing Without Phone/Camera

### Test Camera Locally
```bash
# Run on localhost (HTTP)
python backend/backend.py

# Visit http://localhost:5000 (NOT https)
# Click Camera button - should work
```

### Test WhatsApp
```javascript
// In browser console, add test button:
const testBtn = document.createElement('button');
testBtn.textContent = 'Test WhatsApp';
testBtn.onclick = openWhatsappModal;
document.body.appendChild(testBtn);
```

---

## 📊 File Size Limits

Current implementation:
- **Max Camera Resolution**: Device maximum (typically 4K)
- **Max File Size**: 10MB (set in backend)
- **Supported Formats**: JPEG, PNG, WebP

To change limits, edit `backend/backend.py`:
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

---

## 🚨 Common Issues & Solutions

### Camera showing black screen
- ✅ Check browser permissions
- ✅ Ensure HTTPS in production
- ✅ Try switching to different camera

### WhatsApp link not opening
- ✅ Verify phone number format (no + or spaces)
- ✅ Install WhatsApp app if not installed
- ✅ Check internet connection

### Images not processing after capture
- ✅ Ensure you're logged in
- ✅ Check backend is running
- ✅ Try uploading different format

---

## 📱 Example WhatsApp Numbers (Replace These!)

For testing, you can use:
- 🇮🇳 Indian Number: `919876543210`
- 🇺🇸 US Number: `12015550123`
- 🇬🇧 UK Number: `441632960000`

⚠️ **Always replace with your actual WhatsApp Business number in production!**

---

## ✅ Checklist

- [ ] Camera button visible in app
- [ ] WhatsApp button visible in app
- [ ] Camera works on phone
- [ ] WhatsApp number updated in code
- [ ] WhatsApp button opens correct conversation
- [ ] Buttons are styled nicely
- [ ] Both work on mobile and desktop
- [ ] Logged-in users can access features

---

## 📞 Next Steps

1. **Test Camera**: Click camera button, take a photo
2. **Update WhatsApp**: Change phone number in `app.js`
3. **Test WhatsApp**: Click WhatsApp button, should open chat
4. **(Optional)** Set up WhatsApp API webhook for auto-processing

---

**Setup Complete! Your Toonify AI now has:**
- 📷 Live camera capture
- 💬 WhatsApp integration
- 🎨 Full stylization pipeline

**Enjoy!** 🎉
