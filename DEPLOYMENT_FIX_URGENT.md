# 🚨 URGENT: Google OAuth Configuration Fix

## ✅ BACKEND CONFIGURATION - UPDATED

**Changes Made:**
1. ✅ Updated `GOOGLE_REDIRECT_URI` in `/app/backend/.env`:
   - OLD: `https://exerate-poll.emergent.host/api/auth/google/callback`
   - NEW: `https://habitere.com/api/auth/google/callback`

2. ✅ Updated `REACT_APP_BACKEND_URL` in `/app/frontend/.env`:
   - OLD: `https://fastapi-modules-1.preview.emergentagent.com`
   - NEW: `https://habitere.com`

3. ✅ Services restarted - All running successfully

---

## 🔧 CRITICAL: Update Google Cloud Console

**You MUST update your Google OAuth settings to match the new domain:**

### **Step 1: Go to Google Cloud Console**
1. Visit: https://console.cloud.google.com/
2. Select your project (Habitere)
3. Go to **APIs & Services** → **Credentials**

### **Step 2: Find Your OAuth 2.0 Client**
- Look for client ID: `913533136721-l73cp0nog642ldvmul7ssoh6quld3t31.apps.googleusercontent.com`

### **Step 3: Update Authorized Redirect URIs**

**Add these URIs:**
```
https://habitere.com/api/auth/google/callback
https://www.habitere.com/api/auth/google/callback
```

**Remove old URIs:**
```
https://exerate-poll.emergent.host/api/auth/google/callback
```

### **Step 4: Update Authorized JavaScript Origins**

**Add these origins:**
```
https://habitere.com
https://www.habitere.com
```

### **Step 5: Save Changes**
- Click **Save**
- Wait 5-10 minutes for changes to propagate

---

## 🔧 ADDITIONAL FIXES NEEDED

### **Fix 1: Update Cookie Settings for Production**

The cookie settings need to be secure for HTTPS. I've already updated the .env files, but you may need to verify the backend cookie configuration.

**To verify cookies are working:**
1. Open https://habitere.com
2. Try to login with email/password
3. Check browser DevTools → Application → Cookies
4. You should see `session_token` cookie

### **Fix 2: Email/Password Login**

**Current Status:** Should work now that backend URL is correct

**Test Steps:**
1. Go to https://habitere.com/auth/register
2. Register a new account
3. Try to login
4. Check browser console for errors

If you see 401 errors, check:
- Backend is running: `sudo supervisorctl status backend`
- Backend logs: `tail -f /var/log/supervisor/backend.err.log`

---

## 📊 VERIFICATION CHECKLIST

After updating Google Cloud Console:

### **Test Google OAuth:**
- [ ] Go to https://habitere.com/auth/login
- [ ] Click "Sign in with Google"
- [ ] Should redirect to Google login
- [ ] After login, should redirect back to habitere.com
- [ ] Should be logged in successfully

### **Test Email/Password:**
- [ ] Go to https://habitere.com/auth/register
- [ ] Register with email/password
- [ ] Should redirect to dashboard or role selection
- [ ] Verify session persists

### **Test API Calls:**
- [ ] Login successfully
- [ ] Open browser DevTools → Network tab
- [ ] Navigate around the site
- [ ] All API calls should go to `habitere.com/api/*`
- [ ] No calls to `exerate-poll.emergent.host`

---

## 🚨 COMMON ERRORS & SOLUTIONS

### **Error 1: "redirect_uri_mismatch"**
**Solution:** Update Google Cloud Console (Step 2-4 above)

### **Error 2: "Failed to load resource: 401"**
**Cause:** Cookie not being set or sent
**Solutions:**
1. Clear browser cookies for habitere.com
2. Try in incognito mode
3. Check backend logs for authentication errors
4. Verify backend is running

### **Error 3: API calls going to wrong domain**
**Cause:** Frontend cached with old backend URL
**Solution:**
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
3. Verify frontend .env is updated
4. Restart frontend: `sudo supervisorctl restart frontend`

### **Error 4: CORS errors**
**Cause:** Backend CORS not configured for new domain
**Status:** Already configured for habitere.com ✅

---

## 📝 CONFIGURATION SUMMARY

### **Backend (.env) - UPDATED ✅**
```bash
GOOGLE_REDIRECT_URI=https://habitere.com/api/auth/google/callback
FRONTEND_URL=https://habitere.com
```

### **Frontend (.env) - UPDATED ✅**
```bash
REACT_APP_BACKEND_URL=https://habitere.com
```

### **Services - RESTARTED ✅**
```
backend: RUNNING ✅
frontend: RUNNING ✅
mongodb: RUNNING ✅
```

---

## 🎯 EXPECTED BEHAVIOR AFTER FIX

### **Google OAuth Flow:**
1. User clicks "Sign in with Google" on https://habitere.com
2. Redirects to Google login page
3. User authorizes Habitere
4. Google redirects to: https://habitere.com/api/auth/google/callback
5. Backend processes OAuth token
6. Backend sets session cookie
7. User redirected to dashboard
8. User is logged in ✅

### **Email/Password Flow:**
1. User registers at https://habitere.com/auth/register
2. Backend creates account
3. Backend sets session cookie
4. User redirected to role selection or dashboard
5. User is logged in ✅

---

## 🔒 SECURITY NOTES

**Important for Production:**

1. **HTTPS Only:**
   - Cookies with `secure=True` only work on HTTPS ✅
   - Your domain has HTTPS ✅

2. **Same-Origin:**
   - Frontend and backend on same domain (habitere.com) ✅
   - Cookies will work properly ✅

3. **Cookie Settings:**
   - `httponly=True` - Prevents JavaScript access ✅
   - `secure=True` - HTTPS only ✅
   - `samesite=lax` - Good for same-domain ✅

---

## 📞 TESTING AFTER GOOGLE UPDATE

**Wait 5-10 minutes** after updating Google Cloud Console, then test:

```bash
# Test from command line:
curl -I https://habitere.com/api/health

# Should return 200 OK
```

**Browser Testing:**
1. Clear all cookies for habitere.com
2. Clear browser cache
3. Open https://habitere.com in incognito mode
4. Try Google OAuth login
5. Should work without errors ✅

---

## 🎉 SUCCESS INDICATORS

**You'll know it's working when:**
- ✅ No "redirect_uri_mismatch" error
- ✅ Google login redirects back to habitere.com
- ✅ Session cookie is set (visible in DevTools)
- ✅ User stays logged in after page refresh
- ✅ API calls go to habitere.com/api/*
- ✅ No 401 errors on /api/auth/me

---

## 🚀 NEXT STEPS AFTER FIX

1. **Test all authentication flows:**
   - Email/Password registration
   - Email/Password login
   - Google OAuth login
   - Logout

2. **Test protected features:**
   - Property listings (authenticated)
   - Booking creation
   - Messaging
   - Reviews

3. **Monitor for errors:**
   - Backend logs: `tail -f /var/log/supervisor/backend.err.log`
   - Frontend console (browser DevTools)
   - User feedback

4. **Create real admin account:**
   - Use production credentials
   - Change default admin password
   - Test admin dashboard

---

## ⚠️ IMPORTANT REMINDERS

1. **Update Google Cloud Console FIRST** - This is critical!
2. **Wait 5-10 minutes** for Google changes to propagate
3. **Clear browser cache** before testing
4. **Test in incognito mode** to avoid cached data
5. **Check backend logs** if issues persist

---

**URGENT ACTION REQUIRED:**
👉 **Update Google Cloud Console redirect URI NOW**
👉 **URL:** https://console.cloud.google.com/apis/credentials

---

*Configuration Updated: [Current Date]*
*Services Status: All Running ✅*
*Next Action: Update Google Cloud Console*
