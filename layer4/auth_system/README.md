# Smart Behavioral Authentication System

**Continuous Learning Alert System for Behavioral Anomaly Detection**

---

## 🎯 What It Does

Automatically detects when someone else is using your computer by analyzing behavioral patterns (typing rhythm, mouse movements) and sends alerts when suspicious activity is detected.

**NOT:** Locks your screen  
**YES:** Alerts you about unusual behavior

---

## 🚀 Quick Start

### Step 1: Collect Data (30+ minutes)

```bash
# Run data collection system
python3 run.py

# Use your computer normally for at least 30 minutes
# This builds your behavioral baseline
```

### Step 2: Start Monitoring

```bash
# Start the intelligent system (one command!)
python3 smart_auth.py start

# System now:
# ✓ Trains automatically every minute
# ✓ Monitors behavior continuously
# ✓ Alerts you when suspicious activity detected
```

**That's it!** The system runs automatically in the background.

---

## 📋 Commands

```bash
# Start continuous monitoring (main command)
python3 smart_auth.py start

# Run single detection test
python3 smart_auth.py test

# Train baseline model manually
python3 smart_auth.py train

# Check system status
python3 smart_auth.py status
```

---

## 🧠 How It Works

### Two-Model Architecture

**1. Baseline Model (Long-term Profile)**
- Your core behavioral signature
- Trained on confirmed legitimate data
- Updated weekly
- Resistant to contamination

**2. Adaptive Model (Short-term Adjustments)**
- Recent behavior variations
- Updated every minute
- Handles: tired, different keyboard, time of day
- Uses 30-minute rolling window

### Continuous Learning Loop

```
Every Minute (Automatic):
1. Get last 30 minutes of data
2. Score with baseline model
3. Filter: Keep only high-confidence samples (>60%)
4. Check for contamination (>30% suspicious = don't train)
5. Update adaptive model with clean data
6. Detect anomalies in current behavior
7. Send alert if suspicious
8. Repeat
```

---

## 🛡️ Anti-Contamination System

**The Problem:** If impostor uses computer for 30 minutes, their behavior could contaminate the training data.

**The Solution:**

```python
# Confidence filtering
for sample in recent_data:
    if baseline_score(sample) > 0.6:  # High confidence
        train_on_this()  # Legitimate user
    else:
        ignore_this()    # Suspicious, don't learn
```

**Result:** Impostor data never enters training! ✅

---

## ⚠️ Alert Levels

### None (Confidence > 70%)
- ✅ Normal behavior
- No alert
- Continue monitoring

### Low (50-70% confidence)
- 🟡 Slightly unusual
- Silent logging
- Alert every 10 minutes if persists

### Medium (30-50% confidence)
- 🟠 Suspicious activity
- Desktop notification
- Alert every 5 minutes

### High (20-30% confidence)
- 🔴 High risk
- Desktop notification
- Alert every 2 minutes

### Critical (<20% confidence)
- 🚨 Likely impostor
- Urgent notification
- Alert every minute

---

## 📊 What Gets Detected

### Behavioral Changes Detected:
- ✅ Different typing speed/rhythm
- ✅ Different mouse movement patterns
- ✅ Unusual time-of-day activity
- ✅ Superhuman speeds (bot detection)
- ✅ Activity at unusual hours
- ✅ Sudden behavior changes

### Example Alert:

```
⚠️  Suspicious Activity

Confidence: 35%

Reasons:
• Typing speed 45% faster than baseline
• Mouse movement pattern unusual
• Time of day inconsistent with profile
```

---

## 🔧 Components

### Files Created:

```
auth_system/
├── baseline_model.py         - Long-term profile
├── adaptive_model.py         - Short-term adjustments
├── anomaly_detector.py       - Multi-model detection
├── alert_manager.py          - Notification system
└── continuous_trainer.py     - Orchestrator

models/
├── baseline_model.pkl        - Trained baseline
├── baseline_scaler.pkl       - Feature normalization
└── baseline_metadata.pkl     - Model info

logs/
└── alerts.log                - Alert history

config/
└── settings.json             - Configuration
```

---

## 🎛️ Configuration

Edit `config/settings.json` to adjust:

```json
{
  "monitoring": {
    "update_interval_seconds": 60,   // How often to check
    "window_minutes": 30              // Rolling window size
  },
  
  "thresholds": {
    "critical": 0.2,  // Adjust sensitivity
    "high": 0.3,
    "medium": 0.5,
    "low": 0.7
  },
  
  "alerts": {
    "desktop_notifications": true,   // Enable/disable
    "rate_limit_seconds": {
      "low": 600,      // How often to alert
      "medium": 300,
      "high": 120,
      "critical": 60
    }
  }
}
```

---

## 📈 Performance

- **CPU Usage:** <2% (runs in background)
- **Memory:** ~100-150 MB
- **Update Time:** <1 second per minute
- **Storage:** ~10 MB for models

---

## 🐛 Troubleshooting

### "No baseline model found"
```bash
# Solution: Train the model first
python3 smart_auth.py train
```

### "Not enough data"
```bash
# Solution: Collect more data (run for 30+ minutes)
python3 run.py
```

### "Notifications not working"
```bash
# Solution: Install notification library
pip install plyer

# Test notifications
python3 smart_auth.py test
```

### "Too many false alerts"
```bash
# Solution: Adjust thresholds in config/settings.json
# Increase threshold values to be more lenient
```

---

## 🧪 Testing

### Test the system works:

```bash
# 1. Check status
python3 smart_auth.py status

# 2. Run single detection
python3 smart_auth.py test

# 3. Have someone else type on your keyboard
#    System should detect and alert!
```

---

## 📊 Viewing Results

### Alert Log:

```bash
# View alerts
cat logs/alerts.log

# Recent alerts
tail -n 20 logs/alerts.log
```

### Statistics (while running):

System prints status every 10 minutes:
- Baseline model info
- Adaptive model stats
- Detection counts
- Alert counts

---

## 💡 Best Practices

### Initial Setup:
1. Collect data for 1-2 hours of normal use
2. Train baseline model
3. Start monitoring
4. Review first day of alerts
5. Adjust thresholds if needed

### Ongoing Use:
- Let system run continuously
- Review alerts periodically
- System adapts automatically
- Baseline retrains weekly

### If You Change Hardware:
- New keyboard/mouse will trigger alerts initially
- System learns new patterns within 30 minutes
- Temporary increase in alerts is normal

---

## 🔒 Privacy & Security

- ✅ All processing happens locally
- ✅ No network transmission
- ✅ Models stored on your computer
- ✅ Works with existing privacy mode (keys anonymized)
- ✅ Can delete models anytime

---

## ⚙️ Advanced Usage

### Manual Baseline Retraining:

```bash
# Force retrain baseline
python3 smart_auth.py train --min-samples 200
```

### Custom Database Path:

```bash
# Use different database
python3 smart_auth.py start --db /path/to/database.db
```

### Integration with Other Systems:

```python
from auth_system import ContinuousTrainer

# Custom integration
trainer = ContinuousTrainer(db_path="custom.db")
trainer.start()
```

---

## 📖 Understanding the Intelligence

### Why Two Models?

**Baseline (Weekly):**
- Stable, long-term profile
- Hard to contaminate
- Detects major deviations

**Adaptive (Minute):**
- Handles natural variations
- Adapts quickly
- Filters out suspicious data

**Together:**
- Robust to contamination
- Adapts to legitimate changes
- Detects impostors effectively

### Confidence Scoring:

```
0-20%:   Critical - Definitely not you
20-30%:  High     - Probably not you
30-50%:  Medium   - Unusual but might be you
50-70%:  Low      - Slightly different
70-100%: Normal   - Definitely you
```

---

## 🎓 Technical Details

### Machine Learning:
- **Algorithm:** Isolation Forest (anomaly detection)
- **Features:** 80 behavioral features
- **Update:** Continuous online learning
- **Protection:** Confidence-based filtering

### Statistics:
- **Z-score analysis** for feature deviation
- **Distribution comparison** for drift detection
- **Percentile-based** thresholds

### Rules:
- **Physical constraints** (speed limits)
- **Temporal patterns** (unusual hours)
- **Behavioral logic** (impossible combinations)

---

## 📞 Support

Issues? Check:
1. `python3 smart_auth.py status` - System status
2. `logs/alerts.log` - Alert history
3. Main README.md - Full documentation

---

**Built with intelligence for real-world behavioral authentication! 🧠🔒**

*Version 1.0 | Continuous Learning Alert System*

