# Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: `Error in training loop: 'status'`

**Symptoms:**
```
[System] Error in training loop: 'status'
[System] Error in training loop: 'status'
[System] Error in training loop: 'status'
```

**Cause:** 
Bug in `continuous_trainer.py` line 140 - tries to access a dictionary key that doesn't always exist.

**Status:** ✅ **FIXED** in latest version

**Solution:**
Update your files to the latest version where this bug is fixed.

---

### Issue 2: `plyer not installed` / Notifications Disabled

**Symptoms:**
```
[Alert] Warning: plyer not installed. Notifications disabled.
[Alert] Install with: pip install plyer
```

**Cause:** 
Missing `plyer` package needed for desktop notifications.

**Solution:**

**Windows:**
```bash
pip install plyer
# OR reinstall all dependencies
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
pip3 install plyer
# OR reinstall all dependencies
pip3 install -r requirements.txt
```

---

### Issue 3: 100% Anomaly Rate on First Run

**Symptoms:**
```
Anomaly Rate: 100.0%
All detections flagged as anomalies
```

**Cause:** 
This is **EXPECTED** on the first run! The baseline model was just trained and the adaptive model hasn't learned your recent patterns yet.

**Solution:**
✅ **This is NORMAL** - after 30-60 minutes of continuous monitoring, the adaptive model will learn and the anomaly rate will drop to normal levels (typically 5-15%).

**What's happening:**
1. **First 30 min:** System is very sensitive (high false positive rate)
2. **After 30-60 min:** Adaptive model stabilizes
3. **After 24 hours:** System becomes highly accurate

---

### Issue 4: No Data to Analyze

**Symptoms:**
```
[10:30:45] No new data to analyze
[10:31:45] No new data to analyze
```

**Cause:** 
The data collector (`run.py`) is not running or hasn't collected enough data yet.

**Solution:**

**Run BOTH scripts in separate terminals:**

**Terminal 1 (Data Collection):**
```bash
python3 run.py
```
Keep this running continuously to collect data.

**Terminal 2 (Monitoring/Authentication):**
```bash
python3 smart_auth.py start
```
This analyzes the data being collected.

**Important:** Both need to run simultaneously!

---

### Issue 5: Database Not Found

**Symptoms:**
```
[System] ✗ Failed to train baseline: [Errno 2] No such file or directory
```

**Cause:** 
No data has been collected yet - `behavioral_data.db` doesn't exist.

**Solution:**
1. First, run the data collector for at least 5-10 minutes:
   ```bash
   python3 run.py
   ```
   
2. Press Ctrl+C to stop after collecting some data

3. Then start the authentication system:
   ```bash
   python3 smart_auth.py start
   ```

---

### Issue 6: Permission Denied on macOS

**Symptoms:**
```
Error: Permission denied to monitor keyboard/mouse
```

**Cause:** 
macOS requires accessibility permissions for keyboard/mouse monitoring.

**Solution:**
1. Go to **System Preferences** → **Security & Privacy** → **Privacy** tab
2. Select **Accessibility** from the left sidebar
3. Click the lock icon to make changes
4. Add your Terminal app or Python to the list
5. Restart the terminal and try again

---

### Issue 7: ImportError: No module named 'xxx'

**Symptoms:**
```
ImportError: No module named 'sklearn'
ImportError: No module named 'cryptography'
```

**Cause:** 
Missing Python dependencies.

**Solution:**

**Option 1: Reinstall all dependencies**
```bash
pip install -r requirements.txt
```

**Option 2: Install specific missing package**
```bash
pip install scikit-learn
pip install cryptography
pip install plyer
pip install joblib
```

---

## Recommended Workflow

### For Daily Use:

**Setup (One Time):**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Collect initial data (10-15 minutes minimum)
python3 run.py
# Press Ctrl+C after 10-15 minutes
```

**Daily Monitoring:**

Open **TWO terminals** and run:

**Terminal 1:**
```bash
python3 run.py
```
Leave this running 24/7 to continuously collect behavioral data.

**Terminal 2:**
```bash
python3 smart_auth.py start
```
This monitors for suspicious activity and sends alerts.

Both scripts work independently but share the same database.

---

## System Status Check

To check if everything is working correctly:

```bash
python3 smart_auth.py status
```

This will show:
- ✓ Database status (samples collected)
- ✓ Baseline model (trained/not trained)
- ✓ Adaptive model (initialized/not initialized)
- ✓ Configuration settings

---

## Performance Tuning

### Reduce False Positives

If you're getting too many false alerts, edit `config/settings.json`:

```json
{
  "detection_thresholds": {
    "high_confidence": 0.6,     ← Lower from 0.7
    "medium_confidence": 0.4,   ← Lower from 0.5
    "low_confidence": 0.2,      ← Lower from 0.3
    "critical_confidence": 0.1
  }
}
```

Lower thresholds = fewer alerts (less sensitive)

### Increase Sensitivity

If you want MORE alerts (catch more anomalies):

```json
{
  "detection_thresholds": {
    "high_confidence": 0.8,     ← Raise from 0.7
    "medium_confidence": 0.6,   ← Raise from 0.5
    "low_confidence": 0.4,      ← Raise from 0.3
    "critical_confidence": 0.2
  }
}
```

Higher thresholds = more alerts (more sensitive)

---

## Getting Help

If you're still having issues:

1. **Check your Python version:**
   ```bash
   python3 --version
   ```
   Should be Python 3.8 or higher

2. **Check installed packages:**
   ```bash
   pip list | grep -E "(numpy|pandas|scikit-learn|pynput|psutil|cryptography|plyer|joblib)"
   ```

3. **Check database exists:**
   ```bash
   ls -lh behavioral_data.db
   ```

4. **Run system status:**
   ```bash
   python3 smart_auth.py status
   ```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python3 run.py` | Collect behavioral data |
| `python3 smart_auth.py start` | Start monitoring/alerting |
| `python3 smart_auth.py status` | Check system status |
| `python3 smart_auth.py train` | Manually retrain baseline |
| `python3 smart_auth.py test` | Run single detection test |

---

**Last Updated:** November 14, 2025
**Version:** 1.0.1 (Bug fixes applied)

