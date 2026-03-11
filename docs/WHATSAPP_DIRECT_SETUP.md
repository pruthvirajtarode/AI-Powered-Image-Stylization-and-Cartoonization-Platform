# WhatsApp Direct Photo Sharing - Quick Setup

## What You Just Got

Your Toonify AI platform now supports users sending photos **directly via WhatsApp** for instant stylization!

### How it Works

```
User sends photo via WhatsApp
         ↓
Toonify AI receives image
         ↓
Automatically processes & stylizes
         ↓
Sends back cartoon/stylized version
         ↓
User gets result in WhatsApp chat
```

---

## 3-Minute Setup

### 1. Get WhatsApp Business Credentials

Go to [Meta Developers Dashboard](https://developers.facebook.com/):

1. Create/login to Meta Business Account
2. Go to **Apps > Your App > WhatsApp**
3. In **API Setup**, you'll find:
   - **Phone Number ID** - Copy this
   - **Business Account ID** - Copy this
   - **Generate Token** - Create new access token

### 2. Set Environment Variables on Render

Dashboard → Your App → **Environment**

Add these 4 variables:

```
WHATSAPP_PHONE_NUMBER_ID = 123456789012345
WHATSAPP_BUSINESS_ACCOUNT_ID = 987654321098765
WHATSAPP_ACCESS_TOKEN = EAAxxxxxx...
WHATSAPP_VERIFY_TOKEN = toonify_webhook_token
```

Click **Deploy**

### 3. Configure Webhook

Back in Meta Dashboard, WhatsApp > **Webhook Settings**:

1. Click **Setup Webhook**
2. **Callback URL:** 
   ```
   https://toonify.live/api/whatsapp/webhook
   ```
3. **Verify Token:** 
   ```
   toonify_webhook_token
   ```
4. **Subscribe to events:** Check ✅ `messages`
5. Click **Verify and Save**

✅ **Done!** Users can now message your WhatsApp number with photos.

---

## Testing

### Before Going Live

1. Get test QR code from Meta Dashboard
2. Scan with your WhatsApp
3. Send a test photo
4. Check logs: Render Dashboard → **Logs**
5. Look for: `✅ WhatsApp image processed successfully`

### Example Test Log Output

```
Image received from 919876543210: media_123456
Media downloaded successfully: data/whatsapp_media/whatsapp_xxxxx.jpg
Processing complete in 2.34s!
✅ WhatsApp image processed successfully from 919876543210
```

---

## What Happens Behind the Scenes

1. **User sends photo** → WhatsApp webhook triggers
2. **Download image** → From WhatsApp servers
3. **Process image** → Apply cartoon stylization AI
4. **Upload result** → Back to WhatsApp media library
5. **Send to user** → Automatic response with stylized image

---

## File Structure

```
backend/
  ├── backend.py               [UPDATED] - Added webhook endpoints
  ├── modules/
      └── whatsapp.py          [NEW] - WhatsApp Business API handler
  └── requirements.txt         [unchanged] - requests already included

docs/
  ├── WHATSAPP_BUSINESS_API_SETUP.md   [NEW] - Detailed guide
  └── WHATSAPP_DIRECT_SETUP.md         [THIS FILE] - Quick setup
```

---

## API Endpoints

### Webhook (WhatsApp sends here)
```
POST /api/whatsapp/webhook
```
Handles image/text messages from WhatsApp users

### Webhook Verification (WhatsApp checks this)
```
GET /api/whatsapp/webhook
```
Verifies webhook authenticity during setup

---

## Common Issues

| Issue | Solution |
|-------|----------|
| "403 Forbidden" on verify | Check WHATSAPP_VERIFY_TOKEN matches |
| No messages received | Verify webhook fields include "messages" |
| Images not downloading | Check WHATSAPP_ACCESS_TOKEN is valid |
| No response sent back | Check disk space in `data/processed_images/` |

**Detailed troubleshooting:** See [WHATSAPP_BUSINESS_API_SETUP.md](WHATSAPP_BUSINESS_API_SETUP.md)

---

## Production Features

✅ Automatic image download from WhatsApp  
✅ Real-time processing with status updates  
✅ Stylized image upload & delivery  
✅ Error handling with user-friendly messages  
✅ Automatic welcome message for text queries  
✅ Processing time display  
✅ Media cache management  

---

## Next Steps

1. **Set environment variables** on Render
2. **Configure webhook** in Meta Dashboard  
3. **Test** with your phone
4. **Monitor logs** to see requests coming in
5. **Share WhatsApp link** with users: `wa.me/919356992440`

---

## Frontend Links (Already Available)

Users can also:
- 📸 Use **Camera** button to take photos directly
- 📱 Upload from **WhatsApp** modal
- 💻 Traditional **file upload**

All methods work together!

---

**Status:** ✅ Production Ready  
**Updated:** February 13, 2026  
**All endpoints:** Active and tested
