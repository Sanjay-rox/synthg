# 🚀 Quick Start Guide - Behavioral Auth System

---

## ✅ Complete System Ready!

You now have **TWO systems**:

1. **Data Collection** - Collects behavioral data
2. **Smart Authentication** - Detects anomalies and alerts

---

## 📋 Step-by-Step Setup

### Step 1: Install Dependencies

```bash
pip3 install -r requirements.txt
```

**New packages installed:**
- `scikit-learn` - Machine learning
- `plyer` - Desktop notifications

---

### Step 2: Collect Initial Data (30+ minutes)

```bash
python3 run.py
```

**What to do:**
- Use your computer normally
- Type, browse, work as usual
- Let it run for at least 30 minutes (longer is better!)
- Press Ctrl+C when done

**This creates:** `behavioral_data.db` with your behavioral profile

---

### Step 3: Start Smart Auth System

```bash
python3 smart_auth.py start
```

**What happens:**
1. ✅ System trains baseline model on your data
2. ✅ Starts monitoring every 60 seconds
3. ✅ Sends test notification
4. ✅ Begins continuous learning

**You'll see:**
```
======================================================================
STARTING BEHAVIORAL AUTHENTICATION SYSTEM
======================================================================

[System] Loading existing baseline model...
[Baseline] Model loaded (trained 2025-11-14)
[Baseline] Trained on 150 samples

[System] Testing notification system...
[Alert] ✓ Test notification sent successfully

[System] Starting continuous monitoring...
[System] Updates every 60 seconds
[System] Press Ctrl+C to stop
======================================================================

[10:30:15] ✓ Normal | Confidence: 87%
[10:31:15] ✓ Normal | Confidence: 85%
```

---

## 🧪 Test It Works

### Method 1: Have Someone Else Type

1. Let a friend/colleague use your keyboard
2. They should type and move mouse differently
3. Within 1-2 minutes, you should get alert:

```
⚠️  Suspicious Activity
Confidence: 35%

Reasons:
• Typing speed 45% faster than baseline
• Mouse movement pattern unusual
```

### Method 2: Type Deliberately Different

1. Type much faster or slower than usual
2. Use mouse with opposite hand
3. System should detect the change

---

## 📊 Check System Status

```bash
python3 smart_auth.py status
```

**Shows:**
- Database stats
- Baseline model info
- Whether model needs retraining

---

## 🛑 Stop the System

Press **Ctrl+C** in the terminal where `smart_auth.py start` is running

**You'll see final statistics:**
```
[System] Stopping...

======================================================================
FINAL STATISTICS
======================================================================
Total Runtime:   2:30:15
Total Iterations: 150
Detections:      150
Anomalies Found: 3
Anomaly Rate:    2.0%
Alerts Sent:     2
======================================================================
```

---

## 📁 Files Created

```
DataCollection/
├── behavioral_data.db          ✅ Your behavioral data
├── models/                     🆕 Trained models
│   ├── baseline_model.pkl
│   ├── baseline_scaler.pkl
│   └── baseline_metadata.pkl
├── logs/                       🆕 Alert logs
│   └── alerts.log
└── config/                     🆕 Configuration
    └── settings.json
```

---

## ⚙️ Configuration

Edit `config/settings.json` to adjust:

```json
{
  "monitoring": {
    "update_interval_seconds": 60   // Change to 30 for faster updates
  },
  
  "thresholds": {
    "critical": 0.2,   // Lower = more sensitive
    "high": 0.3,
    "medium": 0.5,
    "low": 0.7
  }
}
```

---

## 💡 Tips

### For Best Results:
1. **Collect 1-2 hours of data** initially (longer = better baseline)
2. **Use computer normally** during collection (don't try to fool it!)
3. **Review first day of alerts** to see if sensitivity is right
4. **Adjust thresholds** if too many/few alerts

### Expected Behavior:
- **Normal use:** 95%+ confidence, no alerts
- **Tired/stressed:** 70-85% confidence, occasional low alerts
- **Different keyboard:** 60-80% confidence for first 30 min, then adapts
- **Impostor:** <50% confidence, immediate alerts

---

## 🔧 Commands Reference

```bash
# Data Collection
python3 run.py                    # Collect behavioral data

# Smart Auth System
python3 smart_auth.py start       # Start monitoring (main command)
python3 smart_auth.py test        # Test single detection
python3 smart_auth.py train       # Train baseline model
python3 smart_auth.py status      # Check system status
```

---

## 🐛 Common Issues

### "No baseline model found"
**Solution:** System will auto-train on first run. Or manually: `python3 smart_auth.py train`

### "Not enough data"
**Solution:** Collect more data with `python3 run.py` (aim for 30+ minutes)

### "Notifications not working"
**Solution:** Check if `plyer` installed: `pip install plyer`

### "Too many false alerts"
**Solution:** Edit `config/settings.json`, increase threshold values (e.g., medium: 0.5 → 0.6)

### "No alerts at all"
**Solution:** Edit `config/settings.json`, decrease threshold values (e.g., medium: 0.5 → 0.4)

---

## 📖 Full Documentation

- **Data Collection:** See main `README.md`
- **Smart Auth System:** See `auth_system/README.md`
- **Tool Utilities:** See `tools/README.md`

---

## 🎯 What's Next?

### Day 1: Setup & Test
- ✅ Collect initial data
- ✅ Start monitoring
- ✅ Test with someone else typing
- ✅ Verify alerts work

### Week 1: Calibration
- Monitor alert frequency
- Adjust thresholds if needed
- Let system learn your patterns
- Review alert log

### Ongoing: Continuous Use
- Leave system running
- It adapts automatically
- Baseline retrains weekly
- Review alerts periodically

---

## 🎉 You're All Set!

The system is now:
- ✅ Collecting behavioral data continuously
- ✅ Training automatically every minute
- ✅ Detecting anomalies in real-time
- ✅ Sending alerts when suspicious behavior detected
- ✅ Learning from clean data only (no contamination)
- ✅ Adapting to your behavioral changes

**Just let it run and it will protect you!** 🛡️

---

**Questions?** Check:
- `python3 smart_auth.py status` - System health
- `logs/alerts.log` - Alert history
- `auth_system/README.md` - Detailed docs

**Built with ❤️ for intelligent security!**

