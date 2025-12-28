############################################################
# 🔐 SynthGuard — AI-Powered Synthetic Identity Fraud System🔐
############################################################

project:
  name: SynthGuard
  tagline: "AI can fake identities. SynthGuard proves real human history."
  description: >
    SynthGuard is a multi-layer AI-powered system designed to detect synthetic
    identity fraud by validating identity depth rather than just document validity.
    It integrates document forensics, OSINT intelligence, graph analytics,
    behavioral biometrics, and blockchain-based trust into a unified verification framework.
  domain: FinTech / Cybersecurity
  architecture: 5-layer parallel scoring system with weighted orchestration
  verdicts:
    verified: "90-100"
    manual_review: "50-89"
    reject: "0-49"

############################################################
# 🎛️ Orchestrator — Central Control Engine🎛️
############################################################

orchestrator:
  description: >
    Central orchestration engine that triggers all layers in parallel,
    collects their scores, applies weighted fusion, and produces the final verdict.
  weights:
    layer1_document_forensics: 0.25
    layer2_3_identity_depth: 0.50
    layer4_behavioral: 0.15
    layer5_blockchain: 0.10
  execution:
    command: "python orchestrator/run.py --session_id <SESSION_ID>"
    output: "Final verdict with layer-wise scores"

############################################################
# 🧱 Layers — Multi-Layer Defense Architecture🧱
############################################################

layers:

  ##########################################################
  # 🧾 Layer 1 — Document Forensics🧾
  ##########################################################
  layer1:
    name: Document Forensics
    purpose: Detect AI-generated or tampered identity documents.
    input:
      - id_image_path
    output:
      - document_authenticity_score_0_100
    description: >
      Analyzes EXIF metadata, pixel-level inconsistencies, structural patterns,
      and AI artifacts to determine how the document was created.
    tech:
      - Python
      - OpenCV
      - scikit-image
      - ExifTool
    execution:
      command: "python layer1_forensics/run.py --image data/id.jpg"
      returns: "JSON with document_authenticity_score"

  ##########################################################
  # 🌐 Layer 2 — OSINT Intelligence🌐
  ##########################################################
  layer2:
    name: OSINT Intelligence
    purpose: Discover digital footprint and temporal depth of identity.
    input:
      - name
      - email
      - phone
      - usernames
    output:
      - osint_signals
    description: >
      Uses open-source intelligence to find where and when an identity appeared
      online, helping estimate digital age and consistency.
    tech:
      - Python
      - Tavily API
    execution:
      command: >
        python layer2_osint/run.py
        --name "John Doe"
        --email john@example.com
        --phone "+911234567890"
      returns: "JSON with footprint signals and first_seen timestamps"

  ##########################################################
  # 🕸️ Layer 3 — Graph Identity Depth🕸️
  ##########################################################
  layer3:
    name: Graph Identity Depth
    purpose: Measure relationship depth across identity attributes.
    input:
      - osint_signals
      - identity_attributes
    output:
      - identity_depth_score_0_100
    description: >
      Builds a relationship graph between email, phone, address, and IDs,
      and analyzes density and temporal continuity to distinguish real vs synthetic identities.
    tech:
      - Python
      - Neo4j
    execution:
      command: "python layer3_graph/run.py --session_id <SESSION_ID>"
      returns: "JSON with identity_depth_score and graph metrics"

  ##########################################################
  # 🧍 Layer 4 — Behavioral Biometrics🧍
  ##########################################################
  layer4:
    name: Behavioral Biometrics
    purpose: Distinguish real humans from bots during onboarding.
    input:
      - mouse_events
      - keystroke_events
      - navigation_events
      - timing_data
    output:
      - behavioral_authenticity_score_0_100
    description: >
      Captures live interaction patterns and analyzes rhythm, randomness,
      speed, and hesitation to detect automated or scripted behavior.
    tech:
      - JavaScript (event capture)
      - Python
      - Scikit-learn
    execution:
      capture_endpoint: "POST /behavior/capture"
      score_command: "python layer4_behavior/run.py --session_id <SESSION_ID>"
      returns: "JSON with behavioral_authenticity_score"

  ##########################################################
  # 🔗 Layer 5 — Blockchain Trust Verification🔗
  ##########################################################
  layer5:
    name: Blockchain Trust Verification
    purpose: Prevent reuse of synthetic identities across platforms.
    input:
      - hashed_identity_fingerprint
    output:
      - consortium_trust_score_0_100
    description: >
      Checks and updates a consortium blockchain ledger to ensure fraud history
      is immutable and shared across institutions.
    tech:
      - Solidity
      - Web3.py
      - Polygon/Ethereum Testnet
    execution:
      command: "python layer5_blockchain/run.py --hash <IDENTITY_HASH>"
      returns: "JSON with trust_score and flagged_status"

############################################################
# 🔌 API Layer🔌
############################################################

api:
  base_url: "http://localhost:8000"
  endpoints:
    verify: "POST /verify"
    behavior_capture: "POST /behavior/capture"
    scores: "GET /score/{session_id}"
    verdict: "GET /verdict/{session_id}"

############################################################
# 🚀 Deployment🚀
############################################################

deployment:
  backend:
    command: "python app.py"
  frontend:
    command: "open frontend/index.html"
  graph_db:
    command: "neo4j start"
  blockchain:
    command: "npx hardhat node"

############################################################
# 📂 Project Structure📂
############################################################

project_structure:
  - layer1_forensics/
  - layer2_osint/
  - layer3_graph/
  - layer4_behavior/
  - layer5_blockchain/
  - orchestrator/
  - api/
  - frontend/
  - docs/

############################################################
# 🌍 Impact🌍
############################################################

impact:
  - "Blocks synthetic identities at onboarding"
  - "Reduces financial fraud losses"
  - "Builds cross-platform digital trust"

############################################################
# 🔮 Future Scope🔮
############################################################

future_scope:
  - "Government DB integration (Aadhaar/PAN)"
  - "Nationwide fraud consortium"
  - "Continuous learning AI models"
  - "Production-scale deployment"

############################################################
# 🤝 Team🤝
############################################################

team:
  name: Team PatientZero
  institution: Rajalakshmi Engineering College, Chennai
