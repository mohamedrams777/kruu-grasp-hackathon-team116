# 🔧 Quick Troubleshooting Guide

## Current Status

The project is **almost ready** but has two issues preventing it from running:

### ✅ What's Working
- Backend API server (port 3000) ✓
- Vite development server (port 5173) ✓
- ML service processes started ✓

### ❌ What Needs Fixing

#### 1. ML Services Not Loading (Priority: HIGH)

**Problem**: Python services started but models aren't loading because torch installation failed.

**Fix**:
```powershell
cd ml-services

# Kill existing Python processes
Get-Process python | Stop-Process -Force

# Install updated dependencies
pip install -r requirements.txt

# Restart services
.\start_services.ps1
```

Wait for these messages:
```
✅ Emotion model loaded successfully!
✅ Intent model loaded successfully!  
✅ ChromaDB initialized with X documents
```

#### 2. Frontend Not Rendering (Priority: MEDIUM)

**Problem**: React app showing blank white page despite Vite running.

**Quick Fix - Try These in Order**:

**Option A: Hard Refresh**
1. Open http://localhost:5173
2. Press `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
3. Wait 5 seconds

**Option B: Restart Frontend**
1. In the terminal running `npm run dev`, press `Ctrl + C`
2. Run: `npm run dev` again
3. Open http://localhost:5173

**Option C: Clear Vite Cache**
```powershell
# Stop frontend (Ctrl+C in npm run dev terminal)
Remove-Item -Recurse -Force node_modules\.vite
npm run dev
```

---

## Testing Steps (After Fixes)

### 1. Verify ML Services

Open three URLs in browser:
- http://localhost:8001/health (Emotion)
- http://localhost:8002/health (Intent)  
- http://localhost:8003/health (RAG)

Each should show: `{"status":"ok","service":"..."}`

### 2. Test Frontend

1. Go to http://localhost:5173
2. You should see:
   - Title: "🛡️ Harm Detection System"
   - Text input area
   - "How It Works" section with 3 steps

### 3. End-to-End Test

**Input this text**:
```
They are mixing poison in vaccines. Share this urgently before it's too late!
```

**Click**: "🔍 Analyze Statement"

**Expected Results** (after ~2-3 seconds):
- **Risk Meter**: 70-90 (Red/High)
- **Emotion Bars**:
  - Anger: 60-80%
  - Fear: 60-80%
  - Other emotions: Low
- **Explanation Panel**: 
  - Intent: Alarmist or Inciting
  - Explicit CTA: Yes
  - Similarity to false narratives: High
  - Potential outcomes listed

---

## If Still Having Issues

### Frontend Blank Page Diagnosis

Run in browser console (F12):
```javascript
document.getElementById('root').innerHTML
```

If it returns `""` (empty), the React app isn't mounting. Try:

1. Check terminal running `npm run dev` for errors
2. Look for TypeScript compilation errors
3. Try rebuilding:
   ```powershell
   npm run build
   npm run preview
   ```

### ML Services Not Responding

Check if processes are running:
```powershell
Get-Process python
```

Check specific port:
```powershell
netstat -ano | findstr :8001
```

If ports are in use but not responding:
1. Kill all Python: `Get-Process python | Stop-Process -Force`
2. Reinstall ML dependencies
3. Restart services one-by-one to see which fails

---

## Quick Reference: All Commands

```powershell
# Start everything from scratch

# Terminal 1: Frontend
npm run dev

# Terminal 2: Backend
cd server
npm run dev

# Terminal 3: ML Services  
cd ml-services
pip install -r requirements.txt
.\start_services.ps1
```

---

## Common Error Messages & Solutions

| Error | Solution |
|-------|----------|
| `torch not found` | Run: `pip install torch==2.10.0` |
| `Port 3000 already in use` | Kill existing server or use different port |
| `Cannot connect to localhost:8001` | ML service not running - check Terminal 3 |
| `Blank white page` | Hard refresh (Ctrl+Shift+R) or clear Vite cache |
| `Failed to analyze text` | Backend can't reach ML services - check all 3 are running |

---

**Next Step**: Run the ML service fix (Option 1 above) and test the system!
