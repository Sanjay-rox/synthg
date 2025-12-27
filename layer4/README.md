# Behavioral Authentication Data Collection System

A sophisticated, privacy-first behavioral biometric data collection framework designed for continuous authentication research and ML model training. Collects 80 behavioral features across keystroke dynamics, mouse movements, session patterns, and system context.

---

## 🎯 Overview

This system implements an **intelligent behavioral authentication data collector** that captures user interaction patterns while maintaining strict privacy and security standards. Designed for researchers, students, and security professionals working on behavioral biometrics and continuous authentication systems.

### Key Highlights

- **80 Multi-Modal Features** across 4 behavioral categories
- **Privacy-First Design** with key anonymization and coordinate relativization
- **AES-256 Encryption** for data at rest
- **ML-Ready Data Format** optimized for Isolation Forest and ensemble methods
- **Cross-Platform Support** (macOS, Linux, Windows)
- **Intelligent Bootstrap System** with automatic dependency management
- **Zero Configuration** required - works out of the box

---

## 🚀 Quick Start

### Installation

Simply run the intelligent bootstrap script:

```bash
python3 run.py
```

The system will automatically:
- ✅ Check Python version and dependencies
- ✅ Install missing packages
- ✅ Validate system permissions
- ✅ Configure security settings
- ✅ Initialize database schema
- ✅ Start data collection

**That's it!** No manual setup required.

### System Requirements

- **Python:** 3.7 or higher
- **OS:** macOS, Linux, or Windows
- **Disk Space:** Minimum 100 MB, recommended 1 GB
- **Permissions:** Keyboard and mouse access (system will guide you)

### Dependencies

All dependencies are installed automatically by `run.py`:

```
numpy>=1.24.0
pandas>=2.0.0
pynput>=1.7.6
psutil>=5.9.0
cryptography>=41.0.0
```

---

## 📊 Features

### 1. Comprehensive Behavioral Feature Extraction (80 Features)

#### **Keystroke Dynamics (22 Features)**

Captures typing patterns and rhythm unique to each user:

- **Timing Features:** Hold time, flight time, digraph time
- **Speed Metrics:** Typing speed (WPM), typing momentum
- **Rhythm Analysis:** Rhythm consistency, burst typing ratio, sequence consistency
- **Error Patterns:** Error rate, backspace frequency, correction patterns
- **Key Usage:** Shift/caps usage, special key ratio, key repetition rate
- **Behavioral Indicators:** Fatigue indicator, pause frequency, inter-key variance
- **Pressure Proxy:** Key pressure estimation via hold time analysis

**Privacy:** All key values are anonymized to categories (`[LETTER]`, `[DIGIT]`, `[SPECIAL]`) - **NO actual text is stored**.

#### **Mouse Dynamics (20 Features)**

Analyzes mouse movement patterns and characteristics:

- **Kinematics:** Average speed, acceleration, jerk (rate of acceleration change)
- **Trajectory Analysis:** Efficiency, curvature, straightness, overshoot rate
- **Movement Patterns:** Direction changes, angular velocity, micro-movements
- **Click Behavior:** Click frequency, double-click speed, left/right ratio
- **Pause Patterns:** Pause frequency, idle time ratio
- **Scroll Behavior:** Scroll speed and patterns
- **Movement Variance:** Speed standard deviation, movement consistency

**Privacy:** Uses relative coordinates only - **NO absolute screen positions stored**.

#### **Session Patterns (15 Features)**

Captures temporal and usage patterns:

- **Temporal Features:** Time of day, day of week, session duration
- **Activity Metrics:** Activity intensity, interaction frequency
- **Work Patterns:** Focus duration, work rhythm score, regularity score
- **Break Analysis:** Idle periods, active periods, burst activity ratio
- **Context Switching:** Context switch rate, session frequency
- **Long-term Trends:** Average session length, break pattern consistency

#### **System Context (13 Features)**

Environmental and system state information:

- **Resource Usage:** CPU usage, memory usage, disk I/O
- **System Load:** Process count, multitasking level, system load impact
- **Network Activity:** Network I/O monitoring
- **Hardware State:** Battery level (on laptops)
- **Performance Indicators:** Screen brightness proxy, notification patterns

#### **Composite Features (10 Features)**

Multi-modal correlation and high-level behavioral indicators:

- **Coordination Score:** Keyboard-mouse synchronization
- **Cognitive Load:** Mental effort estimation from error rates and multitasking
- **Stress Indicators:** Fast typing + errors = elevated stress
- **Familiarity Score:** System familiarity based on rhythm consistency
- **Confidence Level:** User confidence from behavioral patterns
- **Behavioral Entropy:** Shannon entropy for pattern randomness
- **Pattern Deviation:** Variance from typical behavior
- **Temporal Consistency:** Regularity across sessions
- **Multi-Modal Correlation:** Cross-modality behavioral alignment
- **Authenticity Score:** Combined legitimacy indicator

---

### 2. Privacy & Security Features

#### **Privacy Mode (Enabled by Default)**

**Key Anonymization:**
```
What you type:  "MyPassword123!"
What we store:  "[LETTER][LETTER][LETTER][LETTER][LETTER][LETTER][LETTER][LETTER][DIGIT][DIGIT][DIGIT][SPECIAL]"
```

- ✅ Passwords **NEVER** captured
- ✅ Credit cards **NEVER** captured  
- ✅ Private messages **NEVER** captured
- ✅ Only timing patterns stored (HOW you type, not WHAT)

**Mouse Anonymization:**
```
Real position:    (1234, 567) → NOT stored
Stored position:  (0, 0) then relative movements
```

- ✅ No absolute screen coordinates
- ✅ Impossible to reconstruct click locations
- ✅ Movement dynamics preserved

#### **AES-256 Encryption**

- Unique encryption key per user
- Key stored with restricted permissions (chmod 600)
- Fernet symmetric encryption (NIST standard)
- Data encrypted at rest

#### **Multi-Layer User Identification**

Generates truly unique user IDs using:

1. **MAC Address** (hardware-based)
2. **System UUID** (motherboard/hardware ID)
3. **User Account Name** (differentiates users on same machine)
4. **Home Directory Path** (unique per user)
5. **Hostname** (fallback identifier)

Result: Each user on each machine gets a unique, persistent ID.

#### **Local-Only Data Storage**

- ✅ **Zero network transmission**
- ✅ **No cloud uploads**
- ✅ **No telemetry**
- ✅ **Complete data ownership**
- ✅ **GDPR compliant** (data minimization, purpose limitation)

---

### 3. Intelligent System Architecture

#### **Thread-Safe Concurrent Collection**

- Multiple collectors run simultaneously without conflicts
- Thread locks protect shared data structures
- Circular buffers (deque) prevent memory overflow
- Background aggregation every 10 seconds

#### **Automatic Dependency Management**

The `run.py` bootstrap script:

- Detects operating system and adapts configuration
- Checks Python version compatibility
- Auto-installs missing packages via pip
- Validates system permissions (keyboard/mouse access)
- Guides users through OS-specific permission granting
- Performs health checks before starting

#### **Graceful Error Handling**

- Returns zero values if insufficient data
- Try-except blocks in all event handlers
- No crashes on missing/corrupted data
- Safe division checks (prevents division by zero)
- Continues collection even if individual features fail

#### **Database Schema Optimization**

**4 Tables for Efficiency:**

1. **`master_features`** - Aggregated 80-feature vectors (ML-ready)
2. **`raw_keystrokes`** - Raw keystroke events (for analysis)
3. **`raw_mouse`** - Raw mouse events (for analysis)
4. **`sessions`** - Session metadata and statistics

**Indexed for Performance:**
- `(user_id, timestamp)` index on master_features
- `(session_id, timestamp)` indices on raw event tables

---

### 4. ML Model Integration

#### **Direct Compatibility**

The exported data is **immediately usable** with scikit-learn:

```python
import pandas as pd
from sklearn.ensemble import IsolationForest

# Load data
df = pd.read_csv('master_dataset.csv')
X = df.drop(['id', 'user_id', 'session_id', 'timestamp'], axis=1)

# Train model (no preprocessing needed!)
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X)

# Predict
predictions = model.predict(X)  # -1 = anomaly, 1 = normal
scores = model.score_samples(X)  # Lower = more anomalous
```

#### **Recommended ML Algorithms**

**Primary: Isolation Forest**
- Detects anomalies (impostors) without labeled data
- Handles high-dimensional data excellently
- Fast training and prediction
- `contamination=0.1` (expect 10% anomalies)

**Secondary: Random Forest**
- Feature importance analysis
- Classification with labeled data
- Ensemble robustness

**Advanced: Neural Networks**
- Autoencoder for anomaly detection
- LSTM for temporal pattern learning
- Deep learning for complex patterns

#### **Feature Engineering Benefits**

- ✅ All features are numeric (no encoding needed)
- ✅ Normalized ranges (most features 0-1 or reasonable scale)
- ✅ No missing values (graceful defaults)
- ✅ No categorical variables
- ✅ Time-series ready (timestamp included)
- ✅ Multi-modal (captures different behavior aspects)

---

## 🏗️ System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  BehavioralDataCollector                    │
│                   (Main Orchestrator)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌───────────────┐ ┌─────────────┐ ┌─────────────────┐
│  Keystroke    │ │    Mouse    │ │     System      │
│  Collector    │ │  Collector  │ │    Context      │
│               │ │             │ │   Collector     │
│ • Timing      │ │ • Position  │ │ • CPU/Memory   │
│ • Rhythm      │ │ • Speed     │ │ • Processes    │
│ • Errors      │ │ • Clicks    │ │ • Network      │
└───────────────┘ └─────────────┘ └─────────────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Feature Extraction  │
            │   (every 10 sec)     │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │   SQLite Database    │
            │  • master_features   │
            │  • raw_events        │
            │  • sessions          │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │   CSV Export         │
            │  (ML-ready format)   │
            └──────────────────────┘
```

### Data Flow

1. **Input Capture:** `pynput` listeners capture keyboard/mouse events
2. **Privacy Filter:** Anonymize keys to categories, relativize coordinates
3. **Event Storage:** Store in thread-safe circular buffers
4. **Aggregation:** Every 10 seconds, extract statistical features
5. **Composite Calculation:** Compute multi-modal correlation features
6. **Database Storage:** Save to SQLite with user_id and timestamp
7. **Export:** On stop, export to CSV for ML training

---

## 📖 Usage

### Basic Usage

```bash
# Start data collection
python3 run.py

# The system will display:
# - User profile information
# - Security settings
# - Collection statistics every 30 seconds

# Stop collection
# Press Ctrl+C (or Cmd+C on Mac)
```

### What to Do While Collecting

**Just use your computer normally!**

- ✅ Type emails, documents, code
- ✅ Browse the web
- ✅ Move and click your mouse
- ✅ Switch between applications
- ✅ Take breaks (helps capture temporal patterns)

**Recommended Collection Duration:**
- **Quick test:** 5-10 minutes (basic patterns)
- **Research:** 30-60 minutes (good dataset)
- **Production:** Multiple sessions over days/weeks (best accuracy)

### Output Files

After stopping, you'll have:

```
DataCollection/
├── behavioral_data.db          # SQLite database (all data)
├── master_dataset.csv          # Exported 80-feature dataset (ML-ready)
└── (config files in ~/.behavioral_auth_*)
```

### Multi-Session Collection

The system accumulates data across sessions:

```bash
# Day 1 - Morning session
python3 run.py  # Collect for 30 mins, Ctrl+C

# Day 1 - Afternoon session  
python3 run.py  # More data added to same database

# Day 2 - Another session
python3 run.py  # Continues building your behavioral profile
```

Each session is tracked separately but tied to your unique user_id.

---

## 🔧 Configuration

### Default Settings (in run.py)

```python
collector = BehavioralDataCollector(
    enable_encryption=True,    # AES-256 encryption
    privacy_mode=True          # Key anonymization
)
```

### Customization Options

Edit `behavioral_data_collector.py` if you need to customize:

```python
# Disable privacy mode (NOT RECOMMENDED)
collector = BehavioralDataCollector(privacy_mode=False)

# Change aggregation interval (default: 10 seconds)
time.sleep(10)  # Line 406 in _collection_loop()

# Change buffer sizes (default: 1000 keystrokes, 2000 mouse events)
KeystrokeCollector(buffer_size=1000)  # Line 640
MouseCollector(buffer_size=2000)      # Line 830

# Specify custom user_id (instead of auto-generation)
collector = BehavioralDataCollector(user_id="my_custom_id")
```

---

## 🖥️ Platform Support

### macOS

**Status:** ✅ Fully Supported

**Requirements:**
- Accessibility permissions (system will prompt)
- Grant via: System Preferences → Security & Privacy → Privacy → Accessibility

**Hardware ID Method:** System UUID from `system_profiler`

### Linux

**Status:** ✅ Fully Supported

**Requirements:**
- X11 or Wayland display server
- May need `input` group membership: `sudo usermod -a -G input $USER`

**Hardware ID Method:** `/etc/machine-id`

### Windows

**Status:** ✅ Fully Supported

**Requirements:**
- Usually works without special permissions

**Hardware ID Method:** WMIC UUID

---

## 📊 Data Format & Export

### Master Features Table Schema

```sql
CREATE TABLE master_features (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    timestamp REAL NOT NULL,
    
    -- 22 Keystroke features (ks_*)
    ks_avg_hold_time REAL,
    ks_typing_speed REAL,
    ...
    
    -- 20 Mouse features (ms_*)
    ms_avg_speed REAL,
    ms_trajectory_efficiency REAL,
    ...
    
    -- 15 Session features (ss_*)
    ss_duration REAL,
    ss_time_of_day REAL,
    ...
    
    -- 13 System features (sys_*)
    sys_cpu_usage REAL,
    sys_memory_usage REAL,
    ...
    
    -- 10 Composite features (comp_*)
    comp_coordination_score REAL,
    comp_authenticity_score REAL,
    ...
)
```

### CSV Export Format

```csv
id,user_id,session_id,timestamp,ks_avg_hold_time,ks_typing_speed,...
1,a3f5c9d2e1b4f8a7,3e8b9f2c,1699999.5,0.092,5.4,...
2,a3f5c9d2e1b4f8a7,3e8b9f2c,1700009.5,0.088,5.6,...
```

**Perfect for pandas:**
```python
df = pd.read_csv('master_dataset.csv')
print(df.shape)  # (N_samples, 84)  # 80 features + 4 metadata cols
```

---

## 🧪 Example ML Workflow

### Complete Example: Training Isolation Forest

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# 1. Load data
df = pd.read_csv('master_dataset.csv')
print(f"Loaded {len(df)} samples")

# 2. Prepare features (drop metadata columns)
X = df.drop(['id', 'user_id', 'session_id', 'timestamp'], axis=1)
print(f"Feature shape: {X.shape}")  # Should be (N, 80)

# 3. Train Isolation Forest
model = IsolationForest(
    contamination=0.1,        # Expect 10% anomalies
    random_state=42,
    n_estimators=100,
    max_samples='auto',
    verbose=1
)

print("Training Isolation Forest...")
model.fit(X)

# 4. Predict (1 = normal, -1 = anomaly)
predictions = model.predict(X)
anomaly_scores = model.score_samples(X)

# 5. Analyze results
n_anomalies = np.sum(predictions == -1)
print(f"Detected {n_anomalies} anomalies ({n_anomalies/len(X)*100:.1f}%)")

# 6. Identify suspicious samples
anomaly_threshold = np.percentile(anomaly_scores, 10)
suspicious = df[anomaly_scores < anomaly_threshold]
print(f"\nMost suspicious sessions:")
print(suspicious[['session_id', 'timestamp']].head())

# 7. Save model for deployment
import joblib
joblib.dump(model, 'behavioral_auth_model.pkl')
print("Model saved!")
```

### Feature Importance Analysis

```python
from sklearn.ensemble import RandomForestClassifier

# Create binary labels (0 = normal, 1 = anomaly)
# Based on manual labeling or semi-supervised approach
y = (predictions == -1).astype(int)

# Train Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X, y)

# Get feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 10 Most Important Features:")
print(feature_importance.head(10))
```

---

## 🛡️ Security Considerations

### What This System Protects Against

✅ **Password capture** - Keys anonymized to categories  
✅ **Keylogger-style attacks** - No actual text stored  
✅ **Screen position tracking** - Relative coordinates only  
✅ **Data theft** - AES-256 encryption  
✅ **Unauthorized access** - File permissions (0600)  
✅ **Network interception** - No network activity  

### What This System Does NOT Protect Against

⚠️ **Root/admin access** - OS-level users can access files  
⚠️ **Malware as same user** - Runs with user privileges  
⚠️ **Physical access** - Unlocked computer is vulnerable  
⚠️ **Memory dumps** - Data unencrypted in RAM while running  
⚠️ **OS kernel compromises** - Relies on OS security  

### Best Practices

1. **Use full-disk encryption** (FileVault, BitLocker, LUKS)
2. **Lock computer when away** (prevents physical access)
3. **Keep OS updated** (security patches)
4. **Strong user password** (protects account)
5. **Run antivirus** (though false positives are common)
6. **Audit the code** (it's open source for a reason!)

---

## 🔬 Research Applications

### Suitable For

- **Behavioral Biometrics Research**
- **Continuous Authentication Systems**
- **User Modeling and Profiling**
- **Human-Computer Interaction Studies**
- **Anomaly Detection Research**
- **Security and Privacy Research**
- **Machine Learning Competitions**

### Academic Citation

If you use this system in research, please consider citing:

```bibtex
@software{behavioral_auth_collector,
  author = {Your Name},
  title = {Behavioral Authentication Data Collection System},
  year = {2025},
  version = {1.0},
  url = {https://github.com/yourname/behavioral-auth}
}
```

---

## 🐛 Troubleshooting

### Common Issues

**Problem: "Permission denied" on macOS**
```
Solution: Grant Accessibility permissions
1. System Preferences → Security & Privacy → Privacy
2. Select "Accessibility"
3. Add Terminal (or your terminal app)
4. Restart the script
```

**Problem: "Module not found" error**
```
Solution: Dependencies not installed
Run: python3 run.py
(The script auto-installs dependencies)
```

**Problem: Database locked error**
```
Solution: Another instance is running
1. Stop all instances: Ctrl+C
2. Check: ps aux | grep behavioral
3. Kill if needed: kill <PID>
```

**Problem: No data being collected**
```
Check:
1. Are you typing/moving mouse?
2. Check permissions (run.py shows status)
3. Look for error messages in output
4. Check disk space (run.py validates)
```

**Problem: Low feature counts**
```
Solution: Insufficient activity
- Collect for at least 5-10 minutes
- Type and move mouse regularly
- First aggregation may have zeros (normal)
```

---

## 📁 Project Structure

```
DataCollection/
├── run.py                          # Intelligent bootstrap script
├── behavioral_data_collector.py    # Main data collection system
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── behavioral_data.db              # SQLite database (created on first run)
├── master_dataset.csv              # Exported features (created on stop)
│
└── ~/.behavioral_auth_key.bin      # Encryption key (user's home)
└── ~/.behavioral_auth_config.json  # User profile (user's home)
```

---

## 📈 Performance

### Resource Usage

- **CPU:** <5% on modern systems
- **Memory:** ~50-100 MB
- **Disk I/O:** Minimal (writes every 10 seconds)
- **Database Size:** ~1 MB per hour of collection

### Scalability

- **Buffer Size:** Circular buffers prevent memory overflow
- **Long-term Collection:** Can run for days/weeks
- **Multi-session:** Handles thousands of sessions per user
- **Database:** SQLite scales to hundreds of GB

---

## 🤝 Contributing

### Guidelines

1. **Code Style:** Follow PEP 8
2. **Privacy First:** Never compromise privacy features
3. **Test:** Test on all platforms before PR
4. **Document:** Update README for new features
5. **Security:** Report vulnerabilities privately

### Development Setup

```bash
git clone <repository>
cd DataCollection
python3 run.py  # Test existing system

# Make changes to behavioral_data_collector.py
# Test thoroughly
# Submit PR with description
```

---

## 📄 License

This project is released under the **MIT License**.

```
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

[Full MIT License text]
```

---

## 🙏 Acknowledgments

- **pynput** - Keyboard and mouse input monitoring
- **psutil** - System and process utilities
- **cryptography** - AES encryption implementation
- **scikit-learn** - ML model compatibility
- **pandas** - Data manipulation and export

---

## 📞 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/yourname/behavioral-auth/issues)
- **Email:** your-email@example.com
- **Documentation:** [Full Docs](https://github.com/yourname/behavioral-auth/wiki)

---

## 🎓 Learn More

### Recommended Reading

- [Keystroke Dynamics as a Biometric](https://en.wikipedia.org/wiki/Keystroke_dynamics)
- [Mouse Dynamics for Continuous Authentication](https://ieeexplore.ieee.org/)
- [Isolation Forest Algorithm](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [Behavioral Biometrics](https://en.wikipedia.org/wiki/Behavioural_biometrics)

### Related Projects

- **BiometricKit** - General biometric authentication
- **KeystrokeML** - Keystroke-only authentication
- **ContinuousAuth** - Multi-factor continuous authentication

---

**Built with ❤️ for the security research community**

*Version 1.0 | Last Updated: November 14, 2025*

