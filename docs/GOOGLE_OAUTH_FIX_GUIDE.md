# 🔧 Google OAuth Fix Guide

## Issue
Your Google OAuth is showing: **"Access blocked: Authorisation error"**

This happens because the JavaScript origin `https://toonify-ai-saas.onrender.com` is not registered in your Google Cloud Console.

---

## ✅ Step-by-Step Fix

### Step 1: Access Google Cloud Console
1. Go to: https://console.cloud.google.com/
2. Sign in with the same Google account you used to create the OAuth credentials
3. Select your project (the one containing your OAuth credentials)

### Step 2: Navigate to OAuth Credentials
1. Click on the **hamburger menu** (☰) in the top left
2. Go to **APIs & Services** → **Credentials**
3. Find your **OAuth 2.0 Client ID** (it should be listed under "OAuth 2.0 Client IDs")
4. Click on the credential name to edit it

### Step 3: Add Authorized JavaScript Origins
In the **Authorized JavaScript origins** section:

**Add these URLs:**
```
https://toonify-ai-saas.onrender.com
http://localhost:5000
```

### Step 4: Add Authorized Redirect URIs
In the **Authorized redirect URIs** section:

**Add these URLs:**
```
https://toonify-ai-saas.onrender.com
https://toonify-ai-saas.onrender.com/
http://localhost:5000
http://localhost:5000/
```

### Step 5: Save Changes
1. Click **Save** at the bottom
2. Wait **5-10 minutes** for Google to propagate the changes

### Step 6: Update Your Environment Variables
Make sure your `.env` file or Render environment variables contain:

```bash
GOOGLE_CLIENT_ID=your_actual_client_id_here.apps.googleusercontent.com
```

**To find your Client ID:**
- In Google Cloud Console → Credentials
- Copy the "Client ID" from your OAuth 2.0 Client ID
- It should look like: `123456789-abcdefghijklmnop.apps.googleusercontent.com`

### Step 7: Set Environment Variable on Render
1. Go to your Render dashboard: https://dashboard.render.com/
2. Select your **toonify-ai-saas** service
3. Go to **Environment** tab
4. Add or update:
   - **Key:** `GOOGLE_CLIENT_ID`
   - **Value:** Your actual Google Client ID (from step 6)
5. Click **Save Changes**
6. Render will automatically redeploy your app

---

## 🧪 Testing

After completing all steps and waiting 5-10 minutes:

1. Visit: https://toonify-ai-saas.onrender.com/
2. Click **Login**
3. Click **"Continue with Google"** button
4. You should now be able to authenticate successfully! ✅

---

## 🚨 Common Issues

### Issue: Still getting "Access blocked" error
**Solution:** 
- Wait 5-10 minutes after saving changes in Google Cloud Console
- Clear your browser cache or try in incognito mode
- Verify the exact URL matches (with/without trailing slash)

### Issue: "Client ID not found" error
**Solution:**
- Double-check the Client ID in your Render environment variables
- Make sure there are no extra spaces or quotes
- Verify it ends with `.apps.googleusercontent.com`

### Issue: Redirect URI mismatch
**Solution:**
- Make sure you added BOTH:
  - `https://toonify-ai-saas.onrender.com`
  - `https://toonify-ai-saas.onrender.com/`
- Both versions (with and without trailing slash) are needed

---

## 📸 Visual Guide

### What the OAuth Credentials page should look like:

**Authorized JavaScript origins:**
```
https://toonify-ai-saas.onrender.com
http://localhost:5000
```

**Authorized redirect URIs:**
```
https://toonify-ai-saas.onrender.com
https://toonify-ai-saas.onrender.com/
http://localhost:5000
http://localhost:5000/
```

---

## ✨ After Fix is Applied

Once Google OAuth is working:
- Users can sign in with "Continue with Google"
- No email verification required for Google users
- Faster onboarding experience
- Automatic profile creation from Google account

---

## 📞 Need Help?

If you're still having issues:
1. Check the browser console for detailed error messages (F12 → Console tab)
2. Verify your Google Cloud project is the correct one
3. Ensure OAuth consent screen is configured
4. Make sure your Google Cloud project is not in "Testing" mode (should be "Production" or have your email as a test user)

---

## 🎯 Current Status

- ✅ **Mobile Responsiveness:** Fixed
- ⏳ **Google OAuth:** Awaiting configuration in Google Cloud Console
