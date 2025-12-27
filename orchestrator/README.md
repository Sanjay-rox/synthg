# 🎯 SynthGuard Orchestrator

**AI-Powered Synthetic Identity Fraud Detection System - Integration Layer**

The orchestrator is the central hub that integrates all 5 layers of SynthGuard into a unified identity verification system.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Orchestrator](#running-the-orchestrator)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Integration with Frontend](#integration-with-frontend)

---

## 🎯 Overview

The orchestrator provides:

✅ **Unified API** - Single endpoint for complete identity verification  
✅ **Parallel Execution** - All layers run simultaneously for speed  
✅ **Weighted Scoring** - Configurable weights for each layer  
✅ **Business Rules** - Auto-reject logic for critical flags  
✅ **Error Handling** - Graceful degradation if layers fail  
✅ **Real-time Monitoring** - Health checks and status endpoints  
✅ **Comprehensive Logging** - Detailed logs for debugging

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (Port 9000)                 │
│                     FastAPI + AsyncIO                       │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    [HTTP POST]         [HTTP POST]      [Python Import]
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Layer 1    │    │  Layer 2&3   │    │   Layer 5    │
│  Port 5000   │    │  Port 8000   │    │  blockchain_ │
│   Flask      │    │   FastAPI    │    │  service.py  │
│  Document    │    │ OSINT+Graph  │    │  Blockchain  │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Data Flow

1. **User submits identity data** → Orchestrator
2. **Orchestrator dispatches** → All layers in parallel
3. **Layers process** → Return individual scores
4. **Orchestrator calculates** → Weighted final score
5. **Business rules applied** → Auto-reject if needed
6. **Response returned** → Complete verification result

---

## 📋 Prerequisites

### Required Services

All layers must be running before starting the orchestrator:

| Layer         | Service            | Port | Status                   |
| ------------- | ------------------ | ---- | ------------------------ |
| **Layer 1**   | Document Forensics | 5000 | ✅ Must be running       |
| **Layer 2&3** | OSINT + Graph      | 8000 | ✅ Must be running       |
| **Layer 4**   | Behavioral         | 6000 | ⚠️ Optional (if enabled) |
| **Layer 5**   | Blockchain         | -    | ✅ Python import         |

### Python Requirements

- Python 3.10+
- pip or conda

---

## 🚀 Installation

### Step 1: Navigate to Orchestrator Directory

```bash
cd synthguard2/orchestrator
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n synthguard python=3.10
conda activate synthguard
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or your preferred editor
```

---

## ⚙️ Configuration

### Environment Variables

Edit `.env` file:

```bash
# Orchestrator Settings
ORCHESTRATOR_PORT=9000
ORCHESTRATOR_DEBUG=true

# Layer Endpoints
LAYER1_URL=http://localhost:5000
LAYER2_3_URL=http://localhost:8000
LAYER4_URL=http://localhost:6000

# Enable/Disable Layers
LAYER1_ENABLED=true
LAYER2_3_ENABLED=true
LAYER4_ENABLED=false  # Set to true when Layer 4 is ready
LAYER5_ENABLED=true

# Scoring Weights (must sum to 1.0)
WEIGHT_LAYER1=0.25
WEIGHT_LAYER2_3=0.50
WEIGHT_LAYER4=0.15
WEIGHT_LAYER5=0.10

# Verdict Thresholds
THRESHOLD_VERIFIED=90    # 90-100 = VERIFIED
THRESHOLD_SUSPICIOUS=50  # 50-89 = SUSPICIOUS, 0-49 = REJECT

# Blockchain Configuration (Layer 5)
POLYGON_RPC_URL=https://polygon-amoy.g.alchemy.com/v2/YOUR_KEY
PRIVATE_KEY=0xYOUR_PRIVATE_KEY
CONTRACT_ADDRESS=0xYOUR_CONTRACT_ADDRESS
```

### Scoring Weights Explained

| Layer     | Default Weight | Purpose                         |
| --------- | -------------- | ------------------------------- |
| Layer 1   | 25%            | Document authenticity           |
| Layer 2&3 | 50%            | OSINT + Graph (core innovation) |
| Layer 4   | 15%            | Behavioral patterns             |
| Layer 5   | 10%            | Blockchain verification         |

**Note:** Weights must sum to 1.0. The orchestrator will normalize them if they don't.

---

## 🎮 Running the Orchestrator

### Method 1: Direct Python

```bash
python app.py
```

### Method 2: Uvicorn (Production)

```bash
uvicorn app:app --host 0.0.0.0 --port 9000 --reload
```

### Expected Output

```
🚀 SYNTHGUARD ORCHESTRATOR STARTING UP
✅ Orchestrator client initialized
✅ Scoring engine initialized
🏥 Checking layer health...
✅ layer_1: Healthy
✅ layer_2_3: Healthy
❌ layer_4: Unavailable
✅ layer_5: Healthy
🌐 Server running on http://0.0.0.0:9000
```

---

## 📚 API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:9000/docs
- **ReDoc**: http://localhost:9000/redoc

### Main Endpoints

#### 1. **Verify Identity** (Main Endpoint)

```http
POST /api/verify-identity
Content-Type: application/json
```

**Request Body:**

```json
{
  "identity_data": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+91 98765 43210",
    "dob": "1990-01-15",
    "aadhaar": "123456789012",
    "pan": "ABCDE1234F",
    "address": "123 MG Road, Bangalore",
    "location": "Bangalore 560001",
    "username": "johndoe",
    "company": "Acme Corp",
    "context": "professional"
  },
  "documents": [
    {
      "type": "aadhaar_card",
      "file_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
      "filename": "aadhaar.jpg"
    }
  ],
  "behavioral_data": {
    "session_id": "sess_123",
    "form_completion_time": 234
  }
}
```

**Response:**

```json
{
  "verification_id": "ver_abc123xyz",
  "timestamp": "2025-12-24T10:35:00",
  "final_score": 78.5,
  "verdict": "SUSPICIOUS",
  "confidence": "MEDIUM",
  "recommendation": "Manual review recommended",
  "score_breakdown": {
    "final_score": 78.5,
    "verdict": "SUSPICIOUS",
    "confidence": "MEDIUM",
    "recommendation": "Manual review recommended",
    "layer_contributions": [
      {
        "layer_id": "layer_1",
        "layer_name": "Document Forensics",
        "score": 85,
        "weight": 0.25,
        "contribution": 21.25,
        "status": "SUCCESS",
        "key_findings": ["Document appears authentic"]
      }
    ],
    "red_flags": [
      {
        "layer": "layer_2_3",
        "severity": "MEDIUM",
        "message": "Limited social media presence"
      }
    ],
    "trust_indicators": [
      "Email registered 8+ years ago",
      "LinkedIn profile found"
    ]
  },
  "layer_results": {
    /* Full results from all layers */
  },
  "visualization_data": {
    "graph_nodes": [
      /* Graph nodes for visualization */
    ],
    "graph_edges": [
      /* Graph edges */
    ],
    "score_chart": {
      /* Chart data */
    }
  },
  "total_processing_time_ms": 8543,
  "layers_executed": 4,
  "layers_failed": 0
}
```

#### 2. **Health Check**

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "orchestrator_version": "1.0.0",
  "layers_status": {
    "layer_1": true,
    "layer_2_3": true,
    "layer_4": false,
    "layer_5": true
  }
}
```

#### 3. **Layer Status**

```http
GET /api/layer-status
```

**Response:**

```json
{
  "timestamp": "2025-12-24T10:35:00",
  "layers": {
    "layer_1": {
      "name": "Document Forensics",
      "enabled": true,
      "healthy": true,
      "weight": 0.25
    }
  }
}
```

#### 4. **Simplified Verification**

```http
POST /api/verify-identity-simple
```

Returns only essential information (score, verdict, top red flags).

---

## 🧪 Testing

### Using cURL

```bash
curl -X POST http://localhost:9000/api/verify-identity \
  -H "Content-Type: application/json" \
  -d '{
    "identity_data": {
      "name": "Test User",
      "email": "test@example.com",
      "phone": "+91 9876543210",
      "dob": "1990-01-01"
    }
  }'
```

### Using Python

```python
import requests
import json

url = "http://localhost:9000/api/verify-identity"

data = {
    "identity_data": {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+91 9876543210",
        "dob": "1990-01-01",
        "aadhaar": "123456789012",
        "pan": "ABCDE1234F"
    }
}

response = requests.post(url, json=data)
result = response.json()

print(f"Score: {result['final_score']}")
print(f"Verdict: {result['verdict']}")
print(f"Confidence: {result['confidence']}")
```

### Using Postman

1. Import the API from: http://localhost:9000/docs
2. Create a POST request to `/api/verify-identity`
3. Add JSON body from examples above
4. Send request

---

## 🔧 Troubleshooting

### Issue: "Orchestrator services not initialized"

**Solution:**

- Check that all required environment variables are set in `.env`
- Ensure Layer 5 blockchain service is properly configured

### Issue: "Layer X timeout"

**Solution:**

- Check that Layer X service is running
- Verify the URL and port in `.env`
- Increase `REQUEST_TIMEOUT` in `.env`

### Issue: "Layer 5 not available"

**Solution:**

```bash
# Ensure Layer 5 path is correct
cd ../layer5
python -c "from backend.blockchain_service import BlockchainService; print('✅ Layer 5 OK')"
```

If import fails:

```bash
# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/../layer5"
```

### Issue: Low final score despite good individual scores

**Solution:**

- Check scoring weights in `.env`
- Review auto-reject rules in `scoring_engine.py`
- Check for red flags in response

### Issue: All layers return errors

**Solution:**

```bash
# Check if layers are running
curl http://localhost:5000/health  # Layer 1
curl http://localhost:8000/health  # Layer 2&3

# Start layers if not running
cd ../layer1 && python app.py &
cd ../layer2&3 && ./start.sh &
```

---

## 🎨 Integration with Frontend

### React Example

```javascript
import axios from "axios";

const verifyIdentity = async (identityData, documents) => {
  try {
    const response = await axios.post(
      "http://localhost:9000/api/verify-identity",
      {
        identity_data: identityData,
        documents: documents,
      }
    );

    const { final_score, verdict, confidence, score_breakdown } = response.data;

    console.log(`Score: ${final_score}/100`);
    console.log(`Verdict: ${verdict}`);
    console.log(`Confidence: ${confidence}`);

    return response.data;
  } catch (error) {
    console.error("Verification failed:", error);
    throw error;
  }
};

// Usage
const result = await verifyIdentity(
  {
    name: "John Doe",
    email: "john@example.com",
    phone: "+91 9876543210",
    dob: "1990-01-15",
  },
  [
    /* document objects */
  ]
);
```

### Displaying Results

```jsx
function VerificationResult({ result }) {
  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case "VERIFIED":
        return "green";
      case "SUSPICIOUS":
        return "orange";
      case "REJECT":
        return "red";
    }
  };

  return (
    <div>
      <h2 style={{ color: getVerdictColor(result.verdict) }}>
        {result.verdict}
      </h2>
      <p>Score: {result.final_score}/100</p>
      <p>Confidence: {result.confidence}</p>

      <h3>Layer Breakdown</h3>
      {result.score_breakdown.layer_contributions.map((layer) => (
        <div key={layer.layer_id}>
          <strong>{layer.layer_name}</strong>: {layer.score}/100
        </div>
      ))}

      {result.score_breakdown.red_flags.length > 0 && (
        <>
          <h3>Red Flags</h3>
          {result.score_breakdown.red_flags.map((flag, i) => (
            <div key={i} className={`flag-${flag.severity.toLowerCase()}`}>
              {flag.message}
            </div>
          ))}
        </>
      )}
    </div>
  );
}
```

---

## 📊 Performance Optimization

### Caching (Optional)

Enable caching in `.env`:

```bash
CACHE_ENABLED=true
CACHE_TTL_SECONDS=300
```

### Parallel Execution

The orchestrator already runs all layers in parallel using `asyncio.gather()`. No configuration needed.

### Timeout Configuration

Adjust timeouts per layer:

```bash
REQUEST_TIMEOUT=30  # Global timeout in seconds
```

---

## 🔒 Security Considerations

### Production Checklist

- [ ] Change `ORCHESTRATOR_DEBUG=false`
- [ ] Use HTTPS (set up reverse proxy with Nginx/Caddy)
- [ ] Rotate `PRIVATE_KEY` regularly
- [ ] Restrict CORS origins to your domain only
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting
- [ ] Review logs regularly
- [ ] Keep dependencies updated

### API Key Security

- ✅ Never commit `.env` to Git (already in `.gitignore`)
- ✅ Use environment-specific `.env` files
- ✅ Rotate Alchemy API key periodically
- ✅ Use separate wallets for testnet and mainnet

---

## 📈 Monitoring

### Logs

Logs are written to:

- Console (stdout)
- File: `orchestrator.log` (if configured)

### Key Metrics to Monitor

- **Response time** - `total_processing_time_ms`
- **Layer failures** - `layers_failed`
- **Verdict distribution** - Track VERIFIED/SUSPICIOUS/REJECT ratios
- **Red flag frequency** - Which layers generate most flags

### Example Log Analysis

```bash
# Count verdicts
grep "Final Verdict" orchestrator.log | sort | uniq -c

# Average response time
grep "Total Time" orchestrator.log | awk '{sum+=$NF; count++} END {print sum/count}'

# Layer failures
grep "Layer.*error" orchestrator.log | wc -l
```

---

## 🚀 Deployment

### Docker (Recommended for Production)

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9000"]
```

Build and run:

```bash
docker build -t synthguard-orchestrator .
docker run -p 9000:9000 --env-file .env synthguard-orchestrator
```

### Systemd Service (Linux)

Create `/etc/systemd/system/synthguard-orchestrator.service`:

```ini
[Unit]
Description=SynthGuard Orchestrator
After=network.target

[Service]
Type=simple
User=synthguard
WorkingDirectory=/home/synthguard/orchestrator
Environment="PATH=/home/synthguard/venv/bin"
ExecStart=/home/synthguard/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable synthguard-orchestrator
sudo systemctl start synthguard-orchestrator
```

---

## 📝 Development

### Adding a New Layer

1. Create layer client in `layer_clients.py`
2. Add layer result model in `models.py`
3. Update `OrchestratorClient` to include new layer
4. Update scoring weights in `.env`
5. Add layer logic to `app.py` verification endpoint

### Modifying Scoring Logic

Edit `scoring_engine.py`:

- Adjust weights
- Add/modify auto-reject rules
- Customize red flag detection
- Change verdict thresholds

---

## 🆘 Support

For issues or questions:

1. Check this README
2. Review logs: `tail -f orchestrator.log`
3. Test individual layers: `curl http://localhost:5000/health`
4. Check Swagger docs: http://localhost:9000/docs

---

## 📄 License

This project is part of PEC Hacks 3.0 - FinTech Track submission.

---

**Built with ❤️ for SynthGuard - Stopping Synthetic Identity Fraud**
