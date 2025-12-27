"""
Pydantic Models for SynthGuard Orchestrator
============================================
Defines all data models for request/response validation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class VerdictEnum(str, Enum):
    """Final verification verdict"""
    VERIFIED = "VERIFIED"
    SUSPICIOUS = "SUSPICIOUS"
    REJECT = "REJECT"


class LayerStatusEnum(str, Enum):
    """Status of individual layer execution"""
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    DISABLED = "DISABLED"


class SeverityEnum(str, Enum):
    """Red flag severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# =============================================================================
# REQUEST MODELS
# =============================================================================

class DocumentData(BaseModel):
    """Document upload data for Layer 1"""
    type: str = Field(..., description="Document type: aadhaar_card, pan_card, etc.")
    file_base64: str = Field(..., description="Base64 encoded image data")
    filename: Optional[str] = Field(None, description="Original filename")


class BehavioralData(BaseModel):
    """Behavioral data for Layer 4"""
    session_id: str = Field(..., description="Unique session identifier")
    mouse_movements: Optional[List[Dict[str, Any]]] = Field(default=[], description="Mouse movement coordinates")
    keystroke_data: Optional[List[Dict[str, Any]]] = Field(default=[], description="Keystroke timing data")
    form_completion_time: Optional[int] = Field(None, description="Total form completion time in seconds")
    navigation_patterns: Optional[List[str]] = Field(default=[], description="Page navigation sequence")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123",
                "mouse_movements": [{"x": 100, "y": 200, "timestamp": 1234567890}],
                "keystroke_data": [{"key": "a", "duration": 50, "timestamp": 1234567890}],
                "form_completion_time": 234,
                "navigation_patterns": ["field1", "field2", "field3"]
            }
        }


class IdentityData(BaseModel):
    """Core identity information for Layer 2&3"""
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number with country code")
    dob: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    aadhaar: Optional[str] = Field(None, description="12-digit Aadhaar number")
    pan: Optional[str] = Field(None, description="10-character PAN number")
    address: Optional[str] = Field(None, description="Full address")
    location: Optional[str] = Field(None, description="City and PIN code")
    username: Optional[str] = Field(None, description="Social media username")
    company: Optional[str] = Field(None, description="Company name")
    context: Optional[str] = Field("professional", description="Context: student, professional, etc.")
    
    @validator('phone')
    def validate_phone(cls, v):
        """Basic phone validation"""
        if v and not v.startswith('+'):
            raise ValueError('Phone number must include country code (e.g., +91)')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
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
            }
        }


class VerificationRequest(BaseModel):
    """Complete verification request"""
    identity_data: IdentityData = Field(..., description="Identity information")
    documents: Optional[List[DocumentData]] = Field(default=[], description="Document images")
    behavioral_data: Optional[BehavioralData] = Field(None, description="Behavioral tracking data")
    
    # Optional metadata
    request_id: Optional[str] = Field(None, description="Client-provided request ID")
    platform: Optional[str] = Field("web", description="Platform: web, mobile, api")
    
    class Config:
        json_schema_extra = {
            "example": {
                "identity_data": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+91 98765 43210",
                    "dob": "1990-01-15",
                    "aadhaar": "123456789012",
                    "pan": "ABCDE1234F"
                },
                "documents": [
                    {
                        "type": "aadhaar_card",
                        "file_base64": "data:image/jpeg;base64,/9j/4AAQ...",
                        "filename": "aadhaar.jpg"
                    }
                ],
                "behavioral_data": {
                    "session_id": "sess_123",
                    "form_completion_time": 234
                }
            }
        }


# =============================================================================
# LAYER RESPONSE MODELS
# =============================================================================

class LayerResult(BaseModel):
    """Generic layer result"""
    layer_id: str = Field(..., description="Layer identifier")
    layer_name: str = Field(..., description="Human-readable layer name")
    score: float = Field(..., ge=0, le=100, description="Layer score (0-100)")
    status: LayerStatusEnum = Field(..., description="Execution status")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    raw_response: Optional[Dict[str, Any]] = Field(None, description="Full layer response")


class Layer1Result(LayerResult):
    """Layer 1: Document Forensics result"""
    is_indian_document: Optional[bool] = None
    document_type: Optional[str] = None
    verdict: Optional[str] = None
    risk_level: Optional[str] = None
    key_findings: List[str] = Field(default=[])


class Layer23Result(LayerResult):
    """Layer 2&3: OSINT + Graph Analysis result"""
    bucket: Optional[str] = None
    interpretation: Optional[str] = None
    claude_verdict: Optional[str] = None
    claude_confidence: Optional[int] = None
    graph_nodes: List[Dict[str, Any]] = Field(default=[])
    graph_edges: List[Dict[str, Any]] = Field(default=[])
    red_flags: List[Dict[str, Any]] = Field(default=[])
    trust_indicators: List[str] = Field(default=[])


class Layer4Result(LayerResult):
    """Layer 4: Behavioral Patterns result"""
    behavioral_score: Optional[float] = None
    anomaly_detected: Optional[bool] = None
    bot_probability: Optional[float] = None
    human_indicators: List[str] = Field(default=[])
    suspicious_indicators: List[str] = Field(default=[])


class Layer5Result(LayerResult):
    """Layer 5: Blockchain Verification result"""
    exists: Optional[bool] = None
    trust_score: Optional[int] = None
    is_flagged: Optional[bool] = None
    flag_reason: Optional[str] = None
    verification_count: Optional[int] = None
    last_verified: Optional[str] = None
    age_days: Optional[int] = None


# =============================================================================
# SCORING MODELS
# =============================================================================

class LayerContribution(BaseModel):
    """Individual layer's contribution to final score"""
    layer_id: str
    layer_name: str
    score: float = Field(..., ge=0, le=100)
    weight: float = Field(..., ge=0, le=1)
    contribution: float = Field(..., description="score × weight")
    status: str
    key_findings: List[str] = Field(default=[])


class RedFlag(BaseModel):
    """Red flag or warning indicator"""
    layer: str
    severity: SeverityEnum
    message: str
    details: Optional[str] = None


class ScoreBreakdown(BaseModel):
    """Detailed score breakdown"""
    final_score: float = Field(..., ge=0, le=100)
    verdict: VerdictEnum
    confidence: str = Field(..., description="LOW, MEDIUM, HIGH")
    recommendation: str
    
    layer_contributions: List[LayerContribution]
    red_flags: List[RedFlag]
    trust_indicators: List[str]


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class VerificationResponse(BaseModel):
    """Complete verification response"""
    verification_id: str = Field(..., description="Unique verification ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Final verdict
    final_score: float = Field(..., ge=0, le=100)
    verdict: VerdictEnum
    confidence: str
    recommendation: str
    
    # Score breakdown
    score_breakdown: ScoreBreakdown
    
    # Individual layer results
    layer_results: Dict[str, LayerResult]
    
    # Visualization data
    visualization_data: Dict[str, Any] = Field(default={})
    
    # Performance metrics
    total_processing_time_ms: int
    layers_executed: int
    layers_failed: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "verification_id": "ver_abc123xyz",
                "timestamp": "2025-12-24T10:35:00",
                "final_score": 78.5,
                "verdict": "SUSPICIOUS",
                "confidence": "MEDIUM",
                "recommendation": "Manual review recommended",
                "total_processing_time_ms": 8543,
                "layers_executed": 4,
                "layers_failed": 0
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    orchestrator_version: str
    layers_status: Dict[str, bool]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)