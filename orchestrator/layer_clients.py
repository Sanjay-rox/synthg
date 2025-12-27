"""
Layer Clients for SynthGuard Orchestrator
=========================================
HTTP clients for communicating with individual layers
"""

import httpx
import asyncio
import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from io import BytesIO

# Import Layer 5 blockchain service
sys.path.append(str(Path(__file__).parent.parent / "layer5"))
try:
    from backend.blockchain_service import BlockchainService
    LAYER5_AVAILABLE = True
except ImportError:
    LAYER5_AVAILABLE = False
    print("⚠️  Warning: Layer 5 (blockchain_service) not found. Layer 5 will be disabled.")

from models import (
    Layer1Result, Layer23Result, Layer4Result, Layer5Result,
    LayerStatusEnum, DocumentData, IdentityData, BehavioralData
)
from utils import (
    setup_logger, decode_base64_image, hash_identity,
    sanitize_aadhaar, sanitize_phone, sanitize_pan
)


# Setup logger
logger = setup_logger(__name__)


# =============================================================================
# BASE LAYER CLIENT
# =============================================================================

class BaseLayerClient:
    """Base class for layer clients"""
    
    def __init__(self, base_url: str, endpoint: str, timeout: int = 30):
        """
        Initialize layer client
        
        Args:
            base_url: Base URL of the layer service
            endpoint: API endpoint path
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.endpoint = endpoint
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def health_check(self) -> bool:
        """
        Check if layer service is available
        
        Returns:
            True if service is healthy
        """
        try:
            response = await self.client.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False


# =============================================================================
# LAYER 1 CLIENT - DOCUMENT FORENSICS
# =============================================================================

class Layer1Client(BaseLayerClient):
    """Client for Layer 1: Document Forensics (Flask server on port 5000)"""
    
    async def analyze_document(self, document: DocumentData) -> Layer1Result:
        """
        Analyze document using Layer 1
        
        Args:
            document: Document data with base64 image
        
        Returns:
            Layer1Result with analysis
        """
        start_time = time.time()
        
        try:
            # Decode base64 image
            image_bytes = decode_base64_image(document.file_base64)
            
            # Prepare multipart form data
            files = {
                'document': (document.filename or 'document.jpg', BytesIO(image_bytes), 'image/jpeg')
            }
            
            # Make request to Layer 1
            url = f"{self.base_url}{self.endpoint}"
            logger.info(f" Calling Layer 1: {url}")
            
            response = await self.client.post(url, files=files)
            response.raise_for_status()
            
            data = response.json()
            processing_time = int((time.time() - start_time) * 1000)
            
            logger.info(f" Layer 1 completed in {processing_time}ms - Score: {data.get('overall_score', 0)}")
            
            # Extract key findings
            key_findings = []
            if data.get('verdict'):
                key_findings.append(f"Verdict: {data['verdict']}")
            if data.get('risk_level'):
                key_findings.append(f"Risk Level: {data['risk_level']}")
            if data.get('document_type'):
                key_findings.append(f"Document Type: {data['document_type']}")
            
            return Layer1Result(
                layer_id="layer_1",
                layer_name="Document Forensics",
                score=data.get('overall_score', 0),
                status=LayerStatusEnum.SUCCESS,
                processing_time_ms=processing_time,
                is_indian_document=data.get('is_indian_document'),
                document_type=data.get('document_type'),
                verdict=data.get('verdict'),
                risk_level=data.get('risk_level'),
                key_findings=key_findings,
                raw_response=data
            )
            
        except httpx.TimeoutException:
            processing_time = int((time.time() - start_time) * 1000)
            logger.error(f"⏱  Layer 1 timeout after {processing_time}ms")
            return Layer1Result(
                layer_id="layer_1",
                layer_name="Document Forensics",
                score=0,
                status=LayerStatusEnum.TIMEOUT,
                processing_time_ms=processing_time,
                error_message="Request timeout",
                key_findings=["Layer 1 timeout"]
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            logger.error(f" Layer 1 error: {str(e)}")
            return Layer1Result(
                layer_id="layer_1",
                layer_name="Document Forensics",
                score=0,
                status=LayerStatusEnum.ERROR,
                processing_time_ms=processing_time,
                error_message=str(e),
                key_findings=[f"Error: {str(e)}"]
            )


# =============================================================================
# LAYER 2&3 CLIENT - OSINT + GRAPH ANALYSIS
# =============================================================================

class Layer23Client(BaseLayerClient):
    """Client for Layer 2&3: OSINT + Graph Analysis (FastAPI server on port 8000)"""
    
    async def analyze_identity(self, identity: IdentityData) -> Layer23Result:
        """
        Analyze identity using Layer 2&3
        
        Args:
            identity: Identity data
        
        Returns:
            Layer23Result with OSINT and graph analysis
        """
        start_time = time.time()
        
        try:
            # Prepare request payload
            payload = identity.model_dump(exclude_none=True)
            
            # Make request to Layer 2&3
            url = f"{self.base_url}{self.endpoint}"
            logger.info(f" Calling Layer 2&3: {url}")
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            processing_time = int((time.time() - start_time) * 1000)
            
            logger.info(f"Layer 2&3 completed in {processing_time}ms - Score: {data.get('total_score', 0)}")
            
            # Extract key findings
            key_findings = []
            if data.get('interpretation'):
                key_findings.append(data['interpretation'])
            if data.get('claude_verdict'):
                key_findings.append(f"Claude Verdict: {data['claude_verdict']}")
            if data.get('trust_indicators'):
                key_findings.extend(data['trust_indicators'][:3])  # Top 3
            
            return Layer23Result(
                layer_id="layer_2_3",
                layer_name="OSINT + Graph Analysis",
                score=data.get('total_score', 0),
                status=LayerStatusEnum.SUCCESS,
                processing_time_ms=processing_time,
                bucket=data.get('bucket'),
                interpretation=data.get('interpretation'),
                claude_verdict=data.get('claude_verdict'),
                claude_confidence=data.get('claude_confidence'),
                graph_nodes=data.get('nodes', []),
                graph_edges=data.get('edges', []),
                red_flags=data.get('red_flags', []),
                trust_indicators=[
                    f"{ti.get('signal')} ({ti.get('strength')})"
                    for ti in data.get("trust_indicators", [])
                ],
                key_findings=key_findings,
                raw_response=data
            )
            
        except httpx.TimeoutException:
            processing_time = int((time.time() - start_time) * 1000)
            logger.error(f"  Layer 2&3 timeout after {processing_time}ms")
            return Layer23Result(
                layer_id="layer_2_3",
                layer_name="OSINT + Graph Analysis",
                score=0,
                status=LayerStatusEnum.TIMEOUT,
                processing_time_ms=processing_time,
                error_message="Request timeout",
                key_findings=["Layer 2&3 timeout"]
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            logger.error(f" Layer 2&3 error: {str(e)}")
            return Layer23Result(
                layer_id="layer_2_3",
                layer_name="OSINT + Graph Analysis",
                score=0,
                status=LayerStatusEnum.ERROR,
                processing_time_ms=processing_time,
                error_message=str(e),
                key_findings=[f"Error: {str(e)}"]
            )


# =============================================================================
# LAYER 4 CLIENT - BEHAVIORAL PATTERNS
# =============================================================================

# =============================================================================
# LAYER 4 CLIENT - BEHAVIORAL PATTERNS (LIGHTWEIGHT)
# =============================================================================
# Add this class to orchestrator/layer_clients.py
# Insert BEFORE the OrchestratorClient class definition
# =============================================================================

class Layer4Client:
    """
    Client for Layer 4: Behavioral Patterns (Lightweight Implementation)
    
    Uses heuristic scoring based on behavioral data collected from frontend:
    - Form completion time
    - Typing speed and rhythm
    - Mouse movement patterns
    - Interaction consistency
    
    This is a simplified implementation that doesn't require ML model training.
    For production, replace with full behavioral authentication system.
    """
    
    def __init__(self):
        """Initialize lightweight behavioral analyzer"""
        logger.info(" Layer 4 (Behavioral - Lightweight) initialized")

    async def health_check(self) -> bool:
        return True


    
    async def analyze_behavior(self, behavioral_data: BehavioralData) -> Layer4Result:
        """
        Analyze behavioral patterns using heuristic scoring
        
        Args:
            behavioral_data: Behavioral tracking data from frontend
        
        Returns:
            Layer4Result with behavioral score and indicators
        """
        start_time = time.time()
        
        try:
            logger.info(f"  Analyzing behavioral patterns...")
            
            # Extract data
            session_id = behavioral_data.session_id
            mouse_movements = behavioral_data.mouse_movements or []
            keystroke_data = behavioral_data.keystroke_data or []
            form_time = behavioral_data.form_completion_time or 0
            nav_patterns = behavioral_data.navigation_patterns or []
            
            # Initialize scores
            scores = []
            human_indicators = []
            suspicious_indicators = []
            
            # =====================================================================
            # METRIC 1: Form Completion Time (0-100)
            # =====================================================================
            time_score = self._analyze_form_time(form_time)
            scores.append(time_score)
            
            if form_time < 10:
                suspicious_indicators.append("⚠️ Extremely fast form completion (< 10s) - bot-like")
            elif form_time < 30:
                suspicious_indicators.append("⚠️ Very fast completion - possible automation")
            elif 30 <= form_time <= 300:
                human_indicators.append("✓ Normal form completion time")
            elif form_time > 600:
                suspicious_indicators.append("⚠️ Unusually slow completion - possible confusion")
            else:
                human_indicators.append("✓ Reasonable completion time")
            
            # =====================================================================
            # METRIC 2: Mouse Movement Analysis (0-100)
            # =====================================================================
            if mouse_movements and len(mouse_movements) > 5:
                mouse_score = self._analyze_mouse_movements(mouse_movements)
                scores.append(mouse_score)
                
                # Check movement count
                if len(mouse_movements) < 10:
                    suspicious_indicators.append("⚠️ Very few mouse movements detected")
                elif len(mouse_movements) > 50:
                    human_indicators.append("✓ Natural mouse movement patterns")
                else:
                    human_indicators.append("✓ Moderate mouse activity")
            else:
                # No mouse data - neutral score
                scores.append(50)
                suspicious_indicators.append("⚠️ Limited mouse movement data")
            
            # =====================================================================
            # METRIC 3: Keystroke Analysis (0-100)
            # =====================================================================
            if keystroke_data and len(keystroke_data) > 5:
                keystroke_score = self._analyze_keystrokes(keystroke_data)
                scores.append(keystroke_score)
                
                if len(keystroke_data) > 20:
                    human_indicators.append("✓ Natural typing rhythm detected")
                else:
                    human_indicators.append("✓ Minimal typing activity")
            else:
                # No keystroke data - neutral score
                scores.append(50)
            
            # =====================================================================
            # METRIC 4: Navigation Pattern Analysis (0-100)
            # =====================================================================
            if nav_patterns and len(nav_patterns) > 2:
                nav_score = self._analyze_navigation(nav_patterns)
                scores.append(nav_score)
                
                # Sequential field navigation is human-like
                if len(nav_patterns) >= 5:
                    human_indicators.append("✓ Systematic field navigation")
            else:
                scores.append(50)
            
            # =====================================================================
            # METRIC 5: Interaction Consistency (0-100)
            # =====================================================================
            consistency_score = self._calculate_consistency(
                form_time, 
                len(mouse_movements), 
                len(keystroke_data)
            )
            scores.append(consistency_score)
            
            # =====================================================================
            # FINAL SCORE CALCULATION
            # =====================================================================
            behavioral_score = sum(scores) / len(scores) if scores else 50
            
            # Detect anomalies
            anomaly_detected = behavioral_score < 40 or len(suspicious_indicators) >= 3
            bot_probability = max(0, (50 - behavioral_score) / 50) if behavioral_score < 50 else 0
            
            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)
            
            logger.info(f" Layer 4 completed in {processing_time}ms - Score: {behavioral_score:.1f}")
            
            # Extract key findings
            key_findings = []
            key_findings.extend(human_indicators[:3])  # Top 3 human indicators
            if suspicious_indicators:
                key_findings.extend(suspicious_indicators[:2])  # Top 2 suspicious
            
            return Layer4Result(
                layer_id="layer_4",
                layer_name="Behavioral Patterns",
                score=behavioral_score,
                status=LayerStatusEnum.SUCCESS,
                processing_time_ms=processing_time,
                behavioral_score=behavioral_score,
                anomaly_detected=anomaly_detected,
                bot_probability=bot_probability,
                human_indicators=human_indicators,
                suspicious_indicators=suspicious_indicators,
                key_findings=key_findings,
                raw_response={
                    "session_id": session_id,
                    "form_completion_time": form_time,
                    "mouse_movements_count": len(mouse_movements),
                    "keystroke_count": len(keystroke_data),
                    "navigation_steps": len(nav_patterns),
                    "individual_scores": {
                        "time_score": scores[0] if len(scores) > 0 else 0,
                        "mouse_score": scores[1] if len(scores) > 1 else 0,
                        "keystroke_score": scores[2] if len(scores) > 2 else 0,
                        "navigation_score": scores[3] if len(scores) > 3 else 0,
                        "consistency_score": scores[4] if len(scores) > 4 else 0
                    }
                }
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            logger.error(f" Layer 4 error: {str(e)}")
            return Layer4Result(
                layer_id="layer_4",
                layer_name="Behavioral Patterns",
                score=50,  # Neutral score on error
                status=LayerStatusEnum.ERROR,
                processing_time_ms=processing_time,
                error_message=str(e),
                key_findings=[f"Error: {str(e)} - using neutral score"]
            )
    
    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================
    
    def _analyze_form_time(self, form_time: float) -> float:
        """
        Score based on form completion time
        
        Scoring:
        - < 10s: 20 (too fast, likely bot)
        - 10-30s: 60 (fast but possible)
        - 30-120s: 90 (ideal human range)
        - 120-300s: 80 (slower but normal)
        - 300-600s: 60 (slow, distracted?)
        - > 600s: 40 (very slow, confused?)
        """
        if form_time < 10:
            return 20
        elif form_time < 30:
            return 60
        elif form_time < 120:
            return 90
        elif form_time < 300:
            return 80
        elif form_time < 600:
            return 60
        else:
            return 40
    
    def _analyze_mouse_movements(self, movements: list) -> float:
        """
        Analyze mouse movement patterns
        
        Human characteristics:
        - Variable speed (not constant)
        - Occasional pauses
        - Non-linear paths
        - 50-200 movements for typical form
        """
        count = len(movements)
        
        if count < 5:
            return 30  # Too few movements
        elif count < 20:
            return 60  # Minimal movements
        elif count < 100:
            return 85  # Good range
        elif count < 200:
            return 90  # Excellent human-like activity
        else:
            return 75  # Many movements (could be erratic)
    
    def _analyze_keystrokes(self, keystrokes: list) -> float:
        """
        Analyze keystroke patterns
        
        Human characteristics:
        - Variable timing between keys
        - Occasional corrections/deletions
        - Natural rhythm variations
        """
        count = len(keystrokes)
        
        if count < 5:
            return 40  # Very little typing
        elif count < 20:
            return 70  # Minimal typing
        elif count < 100:
            return 85  # Good amount
        elif count < 200:
            return 90  # Lots of typing
        else:
            return 80  # Excessive (possibly pasting?)
        
        # Could add timing analysis here if keystroke_data includes timestamps
        # For now, simple count-based heuristic
    
    def _analyze_navigation(self, patterns: list) -> float:
        """
        Analyze field navigation patterns
        
        Human characteristics:
        - Sequential field navigation (tab/click)
        - Some backtracking (corrections)
        - Logical progression through form
        """
        count = len(patterns)
        
        if count < 3:
            return 50  # Minimal navigation
        elif count < 8:
            return 85  # Normal navigation
        elif count < 15:
            return 90  # Good interaction
        else:
            return 75  # Lots of navigation (confusion?)
    
    def _calculate_consistency(self, form_time: float, mouse_count: int, 
                               keystroke_count: int) -> float:
        """
        Check if behavioral metrics are consistent with each other
        
        Inconsistencies that are suspicious:
        - Fast completion BUT lots of mouse/keyboard activity
        - Slow completion BUT minimal activity
        - High mouse activity BUT no keystrokes (vice versa)
        """
        # Expected activity per second
        activity_rate = (mouse_count + keystroke_count) / max(form_time, 1)
        
        # Normal range: 0.5 to 5 actions per second
        if 0.5 <= activity_rate <= 5:
            return 90  # Consistent
        elif 0.2 <= activity_rate <= 10:
            return 70  # Somewhat consistent
        else:
            return 50  # Inconsistent (suspicious)



# =============================================================================
# LAYER 5 CLIENT - BLOCKCHAIN VERIFICATION
# =============================================================================

class Layer5Client:
    """Client for Layer 5: Blockchain Verification (Direct Python import)"""
    
    def __init__(self):
        """Initialize blockchain service"""
        self.available = LAYER5_AVAILABLE
        if self.available:
            try:
                self.service = BlockchainService()
                logger.info(" Layer 5 (Blockchain) initialized successfully")
            except Exception as e:
                logger.error(f" Layer 5 initialization failed: {str(e)}")
                self.available = False
                self.service = None
        else:
            self.service = None
            logger.warning("  Layer 5 (Blockchain) not available")
    
    async def verify_identity(self, identity: IdentityData) -> Layer5Result:
        """
        Verify identity on blockchain
        
        Args:
            identity: Identity data
        
        Returns:
            Layer5Result with blockchain verification
        """
        start_time = time.time()
        
        if not self.available or not self.service:
            logger.warning("  Layer 5 disabled or unavailable")
            return Layer5Result(
                layer_id="layer_5",
                layer_name="Blockchain Verification",
                score=50,  # Neutral score when disabled
                status=LayerStatusEnum.DISABLED,
                processing_time_ms=0,
                error_message="Layer 5 not available",
                key_findings=["Blockchain verification disabled"]
            )
        
        try:
            # Use Aadhaar as SSN equivalent, or create hash from other data
            ssn = sanitize_aadhaar(identity.aadhaar) if identity.aadhaar else hash_identity(
                identity.email, identity.name, identity.dob or "1990-01-01"
            )[:12]
            
            # Check identity on blockchain
            logger.info(f" Calling Layer 5: Checking blockchain...")
            
            result = self.service.check_identity(
                ssn=ssn,
                name=identity.name,
                dob=identity.dob or "1990-01-01"
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            logger.info(f" Layer 5 completed in {processing_time}ms - Score: {result.get('trust_score', 50)}")
            
            # Extract key findings
            key_findings = []
            if result.get('exists'):
                key_findings.append(f"Previously verified {result.get('verification_count', 0)} times")
                if result.get('age_days'):
                    key_findings.append(f"Last verified {result['age_days']} days ago")
            else:
                key_findings.append("First-time verification")
            
            if result.get('is_flagged'):
                key_findings.append(f" FLAGGED: {result.get('flag_reason', 'Unknown reason')}")
            
            return Layer5Result(
                layer_id="layer_5",
                layer_name="Blockchain Verification",
                score=result.get('trust_score', 50),
                status=LayerStatusEnum.SUCCESS,
                processing_time_ms=processing_time,
                exists=result.get('exists'),
                trust_score=result.get('trust_score'),
                is_flagged=result.get('is_flagged'),
                flag_reason=result.get('flag_reason'),
                verification_count=result.get('verification_count'),
                last_verified=result.get('last_verified'),
                age_days=result.get('age_days'),
                key_findings=key_findings,
                raw_response=result
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            logger.error(f" Layer 5 error: {str(e)}")
            return Layer5Result(
                layer_id="layer_5",
                layer_name="Blockchain Verification",
                score=50,  # Neutral score on error
                status=LayerStatusEnum.ERROR,
                processing_time_ms=processing_time,
                error_message=str(e),
                key_findings=[f"Error: {str(e)} - using neutral score"]
            )


# =============================================================================
# ORCHESTRATOR CLIENT - MANAGES ALL LAYERS
# =============================================================================

class OrchestratorClient:
    """Main orchestrator that manages all layer clients"""
    
    def __init__(
        self,
        layer1_url: str,
        layer1_endpoint: str,
        layer23_url: str,
        layer23_endpoint: str,
        layer4_url: str,
        layer4_endpoint: str,
        timeout: int = 30,
        layer1_enabled: bool = True,
        layer23_enabled: bool = True,
        layer4_enabled: bool = True,
        layer5_enabled: bool = True
    ):
        """
        Initialize orchestrator with all layer clients
        
        Args:
            layer1_url: Layer 1 base URL
            layer1_endpoint: Layer 1 endpoint
            layer23_url: Layer 2&3 base URL
            layer23_endpoint: Layer 2&3 endpoint
            layer4_url: Layer 4 base URL
            layer4_endpoint: Layer 4 endpoint
            timeout: Request timeout
            layer1_enabled: Enable Layer 1
            layer23_enabled: Enable Layer 2&3
            layer4_enabled: Enable Layer 4
            layer5_enabled: Enable Layer 5
        """
        self.layer1 = Layer1Client(layer1_url, layer1_endpoint, timeout) if layer1_enabled else None
        self.layer23 = Layer23Client(layer23_url, layer23_endpoint, timeout) if layer23_enabled else None
        self.layer4 = Layer4Client() if layer4_enabled else None
        self.layer5 = Layer5Client() if layer5_enabled else None
        
        logger.info(f" Orchestrator initialized - L1: {layer1_enabled}, L2&3: {layer23_enabled}, L4: {layer4_enabled}, L5: {layer5_enabled}")
    
    async def close(self):
        """Close all HTTP clients"""
        if self.layer1:
            await self.layer1.close()
        if self.layer23:
            await self.layer23.close()
        if self.layer4:
            await self.layer4.close()
    
    async def check_health(self) -> Dict[str, bool]:
        """
        Check health of all layers
        
        Returns:
            Dict of layer_id -> is_healthy
        """
        health = {}
        
        if self.layer1:
            health['layer_1'] = await self.layer1.health_check()
        if self.layer23:
            health['layer_2_3'] = await self.layer23.health_check()
        if self.layer4:
            health['layer_4'] = await self.layer4.health_check()
        if self.layer5:
            health['layer_5'] = self.layer5.available
        
        return health