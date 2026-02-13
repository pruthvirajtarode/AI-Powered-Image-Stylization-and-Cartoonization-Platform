# WhatsApp Business API Integration Guide

## Overview

This guide walks you through setting up the WhatsApp Business API integration with Toonify AI to allow users to send photos directly via WhatsApp for stylization.

**Current Status:** ✅ Backend webhook endpoints implemented and ready

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [WhatsApp Business Setup](#whatsapp-business-setup)
3. [Configuration](#configuration)
4. [Webhook Verification](#webhook-verification)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- WhatsApp Business Account (free or paid)
- Meta Business Account
- Meta API Access Token
- Phone number registered with WhatsApp
- Webhook URL (your Render deployment URL)

## WhatsApp Business Setup

### Step 1: Create Meta Business Account

1. Visit [https://developers.facebook.com/](https://developers.facebook.com/)
2. Click **Get Started** and follow the account creation process
3. From your dashboard, go to **Settings > Business Settings**

### Step 2: Verify Your Business

1. In Business Settings, add your phone number and verify via SMS
2. Add your business name and category
3. Verify your domain (if applicable)

### Step 3: Register WhatsApp Business Phone Number

1. Go to **Apps and Websites** > **Your Apps**
2. Create a new app (if you don't have one) or select existing
3. Add **WhatsApp** product
4. In WhatsApp settings, go to **API Setup**
5. Click **Create Test Number** or **Add Phone Number**

### Step 4: Get API Credentials

After phone number verification:

1. **Phone Number ID:** Found in WhatsApp Settings > API Setup
   - Example: `123456789012345`

2. **Business Account ID:** Found in WhatsApp Settings > API Setup
   - Example: `987654321098765`

3. **Access Token:** 
   - Generate from **Settings > System Users**
   - Select **Generate New Token**
   - Permission: `whatsapp_business_messaging`
   - Token never expires (Recommended for production)

### Step 5: Configure Webhook

1. In WhatsApp Settings, scroll to **Webhook Settings**
2. Click **Setup Webhook**
3. Enter your webhook URL: 
   ```
   https://your-app-domain.onrender.com/api/whatsapp/webhook
   ```
   Example: `https://toonify-ai-saas.onrender.com/api/whatsapp/webhook`

4. Enter Callback Verify Token:
   ```
   toonify_webhook_token
   ```
   (Can be changed in `.env` as `WHATSAPP_VERIFY_TOKEN`)

5. Select Webhook Fields:
   - ✅ messages
   - ✅ message_template_status_update

6. Click **Verify and Save**

---

## Configuration

### Environment Variables

Add these to your `.env` file or Render dashboard:

```env
# WhatsApp Business API
WHATSAPP_PHONE_NUMBER_ID=YOUR_PHONE_NUMBER_ID
WHATSAPP_BUSINESS_ACCOUNT_ID=YOUR_BUSINESS_ACCOUNT_ID
WHATSAPP_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
WHATSAPP_VERIFY_TOKEN=toonify_webhook_token
```

### For Render Deployment

1. Dashboard → Your App → **Environment**
2. Add the 4 environment variables above
3. Click **Deploy**

### Local Testing

Create/update `.env` in your project root:

```env
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_BUSINESS_ACCOUNT_ID=987654321098765
WHATSAPP_ACCESS_TOKEN=EAAxxxxxx...
WHATSAPP_VERIFY_TOKEN=toonify_webhook_token
```

Then run:
```bash
python backend/backend.py
```

---

## Webhook Verification

### Testing Webhook Setup

Use `curl` to test webhook verification:

```bash
curl -X GET "http://localhost:5000/api/whatsapp/webhook?hub.mode=subscribe&hub.challenge=test_challenge&hub.verify_token=toonify_webhook_token"
```

**Expected Response:**
```
test_challenge
```

### Production Testing

After deploying to Render:

```bash
curl -X GET "https://toonify-ai-saas.onrender.com/api/whatsapp/webhook?hub.mode=subscribe&hub.challenge=test_challenge&hub.verify_token=toonify_webhook_token"
```

---

## Testing

### Test User Flow

1. **Get test number from Meta:**
   - WhatsApp Settings > API Setup > Test Number
   - This generates a test QR code

2. **Send test message:**
   - Scan QR code with WhatsApp
   - Send an image to the test number

3. **Check logs:**
   ```bash
   # For Render
   Dashboard → Your App → Logs
   
   # For local
   Terminal output from `python backend/backend.py`
   ```

### Expected Webhook Messages

**Image Message:**
```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "changes": [{
      "field": "messages",
      "value": {
        "messages": [{
          "from": "919876543210",
          "id": "wamid.xxxxx",
          "timestamp": "1644965066",
          "type": "image",
          "image": {
            "id": "image_media_id",
            "mime_type": "image/jpeg"
          }
        }]
      }
    }]
  }]
}
```

**Text Message:**
```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "changes": [{
      "field": "messages",
      "value": {
        "messages": [{
          "from": "919876543210",
          "id": "wamid.xxxxx",
          "timestamp": "1644965066",
          "type": "text",
          "text": {
            "body": "Hello Toonify!"
          }
        }]
      }
    }]
  }]
}
```

---

## API Endpoints

### POST `/api/whatsapp/webhook`

Handles incoming WhatsApp messages and media.

**Request:**
```json
{
  "object": "whatsapp_business_account",
  "entry": [{ ... message data ... }]
}
```

**Response:**
```json
{
  "success": true
}
```

**HTTP Status:** `200 OK`

---

### GET `/api/whatsapp/webhook`

Webhook verification (called by WhatsApp during setup).

**Query Parameters:**
- `hub.mode` - "subscribe"
- `hub.verify_token` - Your verification token
- `hub.challenge` - Challenge string to echo back

**Response:** Echo back the challenge string

**HTTP Status:** `200 OK` if verified, `403 Forbidden` if token mismatch

---

## Features Implemented

### Incoming Message Handling
- ✅ Image message reception
- ✅ Media download from WhatsApp servers
- ✅ Text message reception with help response
- ✅ Automatic error handling

### Image Processing
- ✅ Image download and validation
- ✅ Cartoon stylization
- ✅ JPEG compression optimization
- ✅ processed image storage

### Outgoing Messages
- ✅ Send text status updates
- ✅ Upload processed images to WhatsApp media library
- ✅ Send stylized images back to user
- ✅ Error notifications

### User Experience
- ✅ Real-time processing feedback
- ✅ Friendly error messages in user's language
- ✅ Processing time display
- ✅ Automatic welcome message for text

---

## Troubleshooting

### Issue: Webhook Verification Fails

**Problem:** `403 Forbidden` when verifying webhook

**Solutions:**
1. Check `WHATSAPP_VERIFY_TOKEN` matches webhook settings
2. Ensure URL is publicly accessible (not localhost)
3. Check environment variables are loaded
4. Verify URL is exactly: `https://your-domain.com/api/whatsapp/webhook`

### Issue: Messages Not Being Received

**Problem:** Webhook receives requests but no messages processed

**Solutions:**
1. Check `WHATSAPP_PHONE_NUMBER_ID` is correct
2. Verify webhook fields include "messages"
3. Check app logs for errors
4. Ensure message subscription is enabled

### Issue: Media Download Fails

**Problem:** `ERROR: Failed to download media`

**Solutions:**
1. Verify `WHATSAPP_ACCESS_TOKEN` is valid and not expired
2. Check token permissions include media access
3. Ensure media URL is still valid (URLs expire after 20 minutes)
4. Check network connectivity

### Issue: Image Processing Fails

**Problem:** `ERROR: Invalid image format`

**Solutions:**
1. Ensure image is actual JPEG/PNG (not corrupted)
2. Check disk space in `data/processed_images/`
3. Verify OpenCV installation: `python -c "import cv2; print(cv2.__version__)"`

### Issue: Timeout Sending Stylized Image

**Problem:** Processing works but response never sent

**Solutions:**
1. Check image file is properly saved
2. Verify WhatsApp media upload permissions
3. Check token hasn't expired
4. Try manual test: `curl -X POST https://graph.instagram.com/v18.0/{PHONE_ID}/media ...`

### Debug Mode

Enable detailed logging in `backend/modules/whatsapp.py`:

```python
# Line 3-4
import logging
logging.basicConfig(level=logging.DEBUG)
```

Then restart and check logs for detailed error messages.

---

## Production Checklist

Before going live:

- [ ] `WHATSAPP_PHONE_NUMBER_ID` set in environment
- [ ] `WHATSAPP_BUSINESS_ACCOUNT_ID` set in environment
- [ ] `WHATSAPP_ACCESS_TOKEN` set and valid
- [ ] `WHATSAPP_VERIFY_TOKEN` matches webhook settings
- [ ] Webhook URL verified and responding with 200 OK
- [ ] Test image message processed successfully
- [ ] Response image received by user
- [ ] Error handling tested (invalid images, network errors)
- [ ] Render logs monitored for errors
- [ ] User phone number format includes country code (e.g., 919876543210)

---

## Next Steps (Optional)

### Enhancement Ideas

1. **Analytics Tracking**
   - Log all image processing requests
   - Track success/failure rates
   - Measure average processing time

2. **User Authentication**
   - Link WhatsApp number to user account
   - Save processing history to user profile

3. **Multiple Styles**
   - Add style selection prompt
   - Let users choose cartoon, sketch, oil painting, etc.

4. **Batch Processing**
   - Support multiple images in one message
   - Create collage of all stylized results

5. **Premium Features**
   - Higher resolution outputs for subscribers
   - Priority processing queue
   - Remove Toonify watermark

---

## Support

For issues with:
- **WhatsApp API:** [Meta Developer Docs](https://developers.facebook.com/docs/whatsapp)
- **Toonify Integration:** Check app logs and server console
- **Account Issues:** [WhatsApp Business Support](https://www.whatsapp.com/business/get-started)

---

**Last Updated:** February 13, 2026
**Status:** Production Ready ✅
