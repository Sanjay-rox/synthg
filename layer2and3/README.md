# 🛡️ SynthGuard - AI-Powered Synthetic Identity Fraud Detection

> **PECHACKS 2025 - FinTech Track** | Comprehensive identity verification combining OSINT, Graph Analysis, and AI.

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![React](https://img.shields.io/badge/react-18+-cyan)

---

## 🎯 The Problem

**Synthetic Identity Fraud** is the fastest-growing financial crime:

- **$35+ billion** annual losses
- **311% surge** in synthetic ID fraud (Q1 2025)
- **44%** of all fintech fraud cases

AI can create perfect fake documents in minutes, but it **can't create 10 years of real digital history**.

---

## 🎯 Overview

The **Unified Identity Verification System** is a production-ready platform that combines multiple intelligence sources to verify the authenticity of an identity:

| Feature               | Description                                                          |
| --------------------- | -------------------------------------------------------------------- |
| **🔎 OSINT Analysis** | 50+ Google Dorking patterns for comprehensive web footprint analysis |
| **🕸️ Graph Mapping**  | NetworkX-based relationship visualization                            |
| **🧠 AI Verdicts**    | Claude-powered authenticity assessment                               |
| **📡 API Enrichment** | Real integrations with HaveIBeenPwned, Numverify, India Post         |
| **🇮🇳 India Ready**    | Full support for Aadhaar, PAN, and Indian carriers                   |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React + Vis.js)                     │
│   ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌─────────────┐  │
│   │ IdentityForm│  │ ScoreDisplay │  │GraphVisualizer│ │RedFlagsPanel│ │
│   └─────────────┘  └──────────────┘  └─────────────┘  └─────────────┘  │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ REST API
┌───────────────────────────────▼─────────────────────────────────────────┐
│                           BACKEND (FastAPI)                             │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                         app.py (Main Server)                       │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ osint_engine │  │ graph_engine │  │claude_analyzer│ │scoring_engine│ │
│  │ (Dorking)    │  │ (NetworkX)   │  │ (AI Verdicts)│ │ (12+ signals)│ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘ │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     api_integrations.py                            │ │
│  │  ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────┐       │ │
│  │  │ Tavily  │  │   HIBP   │  │ Numverify │  │  India Post  │       │ │
│  │  │(Search) │  │(Breaches)│  │  (Phone)  │  │   (PIN)      │       │ │
│  │  └─────────┘  └──────────┘  └───────────┘  └──────────────┘       │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- API Keys (see below)

### Installation

```bash
# Clone and navigate to unified folder
cd unified

# Copy environment file and add your API keys
cp env_example backend/.env

# Start everything
./start.sh
```

### Manual Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## 🔑 API Keys Required

| API           | Purpose            | Get Key                                                 |
| ------------- | ------------------ | ------------------------------------------------------- |
| **Anthropic** | Claude AI analysis | [console.anthropic.com](https://console.anthropic.com/) |
| **Tavily**    | OSINT web search   | [app.tavily.com](https://app.tavily.com/)               |
| **Numverify** | Phone validation   | [numverify.com](https://numverify.com/)                 |

### Optional (work without keys)

- **HaveIBeenPwned** - Email breach detection (rate-limited)
- **India Post** - PIN code validation (free)

---

## 📊 Scoring System

The system uses **12+ signals** with weighted scoring:

### OSINT Signals (65%)

| Signal            | Weight | Description                          |
| ----------------- | ------ | ------------------------------------ |
| Format Legitimacy | 10%    | Email/phone pattern analysis         |
| Temporal Analysis | 15%    | Digital footprint age                |
| Cross-Reference   | 10%    | Identifiers appearing together       |
| Platform Presence | 10%    | LinkedIn, GitHub, etc.               |
| Domain Trust      | 8%     | High-trust domain mentions           |
| Behavioral        | 7%     | Activity patterns                    |
| Breach History    | 3%     | HIBP records (indicates real person) |
| Geographic        | 2%     | Address/PIN validation               |

### Graph Signals (20%)

| Signal           | Weight | Description           |
| ---------------- | ------ | --------------------- |
| Connection Count | 8%     | Number of graph edges |
| Temporal Depth   | 8%     | Oldest relationship   |
| Diversity        | 4%     | Node type variety     |

### AI Verdict (15%)

Claude's holistic assessment with confidence weighting.

---

## 🔍 OSINT Capabilities

### Google Dorking Categories

1. **Identity Core** - Exact matches, cross-correlations
2. **Social Media** - 20+ platforms scanned
3. **Professional** - LinkedIn, Crunchbase, press releases
4. **Academic** - ResearchGate, ORCID, .edu sites
5. **Data Leaks** - Paste sites, breach mentions
6. **Documents** - PDFs, DOCs with name/email
7. **Historical** - Web archives, temporal analysis
8. **Behavioral** - Forum posts, contributions
9. **Geolocation** - Location-based searches
10. **Cross-Reference** - Multi-identifier searches

### Example Dork Queries

```
"{name}" "{email}"                    # Identity correlation
site:linkedin.com "{name}"            # LinkedIn profile
"{email}" before:2020                 # Historical presence
"{name}" (patent OR inventor)         # Professional recognition
```

---

## 🚩 Red Flag Detection

### Critical Flags (-50 points)

- Disposable email domain
- Impossible Aadhaar date (before 2010)

### High Flags (-20-30 points)

- Zero online presence (non-student)
- Invalid phone number
- All documents less than 1 year old

### Medium Flags (-10-15 points)

- Random email pattern
- Excessive breaches (10+)
- PAN issued too young

### Context Awareness

Students get **60% reduced penalties** - limited online presence is expected!

---

## 🇮🇳 Indian Document Support

### Aadhaar

- Format validation (12 digits)
- Enrollment year estimation
- Cross-linking with PAN and address

### PAN

- Format validation (ABCDE1234F)
- Issue year estimation based on DOB
- Tax registration age calculation

### Phone Carriers

- Jio, Airtel, VI, BSNL, MTNL detection
- Registration age based on carrier launch dates

### PIN Codes

- India Post API validation
- State/district/city extraction

---

## 🕸️ Graph Visualization (Layer 3 - Core Innovation)

### The Key Insight

> Real identities have **dense, interconnected webs** spanning years.
> Synthetic identities have **sparse, isolated nodes** from last month.

### Synthetic Detection Metrics

| Metric                  | Real Person | Synthetic |
| ----------------------- | ----------- | --------- |
| **Graph Density**       | > 1.5       | < 1.0     |
| **Oldest Relationship** | 5-10+ years | < 2 years |
| **Cross-References**    | Multiple    | None      |
| **Node Count**          | 15+         | 3-5       |

### Node Types

- 👤 **Person** - Central identity node
- ✉️ **Email** - Email addresses (with breach history)
- 📱 **Phone** - Phone numbers (with carrier age)
- 🪪 **Aadhaar** - Aadhaar cards
- 💳 **PAN** - PAN cards
- 📍 **Address** - Physical locations
- 🌐 **Profile** - Social profiles
- 🔴 **Breach** - Data breaches (with REAL dates)

### Edge Types

- **VERIFIED_TOGETHER** - Email+Phone found together online (strong!)
- **HAS_PROFILE** - Discovered social profile
- **APPEARED_ON** - Mentioned on domain
- **BREACHED_IN** - Part of data breach (with year)

### Edge Colors (Temporal)

- 🟢 Green - 10+ year relationship
- 🟡 Yellow - 3-10 year relationship
- 🔴 Red - Less than 1 year (suspicious)

---

## 📚 API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoint

```bash
POST /api/analyze
```

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+91 98765 43210",
  "username": "johndoe",
  "company": "Acme Corp",
  "location": "Bangalore 560001",
  "dob": "1990-01-15",
  "aadhaar": "123456789012",
  "pan": "ABCDE1234F",
  "context": "professional"
}
```

### Response Structure

```json
{
  "total_score": 72.5,
  "bucket": "likely_real",
  "interpretation": "LIKELY AUTHENTIC - Good verification, minor gaps",
  "claude_verdict": "LIKELY_REAL",
  "claude_confidence": 78,
  "nodes": [...],
  "edges": [...],
  "red_flags": [...],
  "trust_indicators": [...],
  "osint_analysis": {...},
  "enrichment": {...}
}
```

---

## 🛠️ Development

### Backend Structure

```
backend/
├── app.py              # FastAPI main server
├── models.py           # Pydantic data models
├── api_integrations.py # External API clients
├── osint_engine.py     # Google Dorking engine
├── graph_engine.py     # NetworkX graph builder
├── claude_analyzer.py  # AI analysis
├── red_flags.py        # Fraud detection
├── scoring_engine.py   # 12+ signal scoring
└── requirements.txt
```

### Frontend Structure

```
frontend/
├── src/
│   ├── App.jsx
│   ├── api.js
│   ├── index.css
│   └── components/
│       ├── IdentityForm.jsx
│       ├── ScoreDisplay.jsx
│       ├── GraphVisualizer.jsx
│       └── RedFlagsPanel.jsx
├── package.json
└── vite.config.js
```

---

## 🎨 Screenshots

### Identity Form

Modern dark theme with cyberpunk aesthetics. Supports global identities + Indian documents.

### Score Display

Circular progress with 12-signal breakdown. Real-time Claude AI verdicts.

### Identity Graph

Interactive vis-network visualization. Color-coded by relationship age.

### Red Flags Panel

Severity-based fraud indicators. Trust indicator list.

---

## 📄 License

Built for **PECHACKS 2025 - FinTech Track** hackathon.

---

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com/) - Claude AI
- [Tavily](https://tavily.com/) - Search API
- [HaveIBeenPwned](https://haveibeenpwned.com/) - Breach data
- [Vis.js](https://visjs.org/) - Graph visualization

---

<div align="center">

# 🛡️ SynthGuard

**Stopping Synthetic Identity Fraud with Graph Intelligence**

_Built with ❤️ for PECHACKS 2025_

</div>
