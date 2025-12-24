"""
Unified Identity Verification System - Data Models
===================================================

Pydantic models for the unified OSINT + Graph identity verification system.
Supports both global identities and Indian-specific documents (Aadhaar, PAN).
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field, field_validator
import re


# =============================================================================
# ENUMS
# =============================================================================

class IdentityContext(str, Enum):
    """Context affects scoring thresholds."""
    STUDENT = "student"
    PROFESSIONAL = "professional"
    EXECUTIVE = "executive"


class VerificationBucket(str, Enum):
    """Final verification result buckets."""
    REAL = "real"
    LIKELY_REAL = "likely_real"
    SUSPICIOUS = "suspicious"
    SYNTHETIC = "synthetic"


class RedFlagSeverity(str, Enum):
    """Red flag severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TrustStrength(str, Enum):
    """Trust indicator strength."""
    STRONG = "strong"
    MEDIUM = "medium"
    WEAK = "weak"


class NodeType(str, Enum):
    """Graph node types."""
    PERSON = "Person"
    EMAIL = "Email"
    PHONE = "Phone"
    AADHAAR = "Aadhaar"
    PAN = "PAN"
    ADDRESS = "Address"
    SOCIAL_PROFILE = "SocialProfile"
    DOMAIN = "Domain"
    BREACH = "Breach"


class DorkCategory(str, Enum):
    """Google Dork query categories."""
    IDENTITY_CORE = "identity_core"
    SOCIAL_MEDIA = "social_media"
    PROFESSIONAL = "professional"
    ACADEMIC = "academic"
    DATA_LEAKS = "data_leaks"
    DOCUMENTS = "documents"
    HISTORICAL = "historical"
    BEHAVIORAL = "behavioral"


# =============================================================================
# INPUT MODELS
# =============================================================================

class IdentityInput(BaseModel):
    """
    Input identity data for verification.
    Supports global identities + Indian documents.
    """
    # Core identifiers (at least one required)
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = Field(None)
    phone: Optional[str] = Field(None)
    
    # Optional identifiers
    username: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    
    # Indian-specific (optional)
    dob: Optional[str] = Field(None, description="Date of birth YYYY-MM-DD")
    aadhaar: Optional[str] = Field(None, description="12-digit Aadhaar number")
    pan: Optional[str] = Field(None, description="10-character PAN")
    
    # Context
    context: IdentityContext = Field(default=IdentityContext.PROFESSIONAL)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower() if v else v
    
    @field_validator('aadhaar')
    @classmethod
    def validate_aadhaar(cls, v):
        if v:
            clean = re.sub(r'\D', '', v)
            if len(clean) != 12:
                raise ValueError('Aadhaar must be 12 digits')
            return clean
        return v
    
    @field_validator('pan')
    @classmethod
    def validate_pan(cls, v):
        if v:
            clean = v.upper().strip()
            if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', clean):
                raise ValueError('Invalid PAN format (should be ABCDE1234F)')
            return clean
        return v
    
    def has_identifiers(self) -> bool:
        """Check if at least one identifier is provided."""
        return bool(self.name or self.email or self.phone or self.aadhaar)
    
    def get_identifiers(self) -> Dict[str, Optional[str]]:
        """Return all non-None identifiers."""
        result = {}
        for field in ['name', 'email', 'phone', 'username', 'company', 
                      'location', 'dob', 'aadhaar', 'pan']:
            val = getattr(self, field)
            if val:
                result[field] = val
        return result


# =============================================================================
# SEARCH & OSINT MODELS
# =============================================================================

class DorkQuery(BaseModel):
    """A Google Dork search query."""
    query: str
    category: DorkCategory
    priority: int = Field(ge=1, le=10)
    description: str
    expected_signal: str


class SearchHit(BaseModel):
    """A search result from web search."""
    query: str
    title: str
    url: str
    snippet: str
    published: Optional[str] = None
    domain: Optional[str] = None
    trust_level: Optional[str] = None
    dork_category: Optional[str] = None


class OSINTAnalysis(BaseModel):
    """OSINT analysis results."""
    total_hits: int = 0
    unique_domains: int = 0
    high_trust_domains: List[str] = Field(default_factory=list)
    social_profiles: List[Dict[str, Any]] = Field(default_factory=list)
    temporal_spread: Dict[str, Any] = Field(default_factory=dict)
    breach_exposure: Dict[str, Any] = Field(default_factory=dict)
    search_queries_executed: int = 0


# =============================================================================
# GRAPH MODELS
# =============================================================================

class GraphNode(BaseModel):
    """A node in the identity graph."""
    id: str
    label: str
    type: str
    color: str = "#4CAF50"
    size: int = 25
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """An edge in the identity graph."""
    from_node: str
    to_node: str
    label: str
    color: str = "#666"
    age_years: float = 0.0
    relationship_type: str = "RELATED"


# =============================================================================
# RED FLAG & TRUST MODELS
# =============================================================================

class RedFlag(BaseModel):
    """A detected fraud indicator."""
    code: str
    description: str
    severity: RedFlagSeverity
    penalty: float = Field(ge=0)
    evidence: Optional[str] = None


class TrustIndicator(BaseModel):
    """A positive trust signal."""
    signal: str
    strength: TrustStrength
    source: Optional[str] = None


# =============================================================================
# SCORING MODELS
# =============================================================================

class ScoreBreakdown(BaseModel):
    """Detailed score component breakdown."""
    # OSINT Components
    format_legitimacy: float = 0.0
    temporal_analysis: float = 0.0
    cross_reference: float = 0.0
    platform_presence: float = 0.0
    domain_trust: float = 0.0
    behavioral: float = 0.0
    breach_history: float = 0.0
    geographic: float = 0.0
    
    # Graph Components
    connection_count: float = 0.0
    temporal_depth: float = 0.0
    diversity: float = 0.0
    
    # Adjustments
    verdict_adjustment: float = 0.0
    red_flag_penalty: float = 0.0


class ClaudeVerdict(BaseModel):
    """Claude AI's verdict on identity authenticity."""
    verdict: str = "INCONCLUSIVE"
    confidence: int = Field(ge=0, le=100, default=0)
    reasoning: str = ""
    trust_indicators: List[str] = Field(default_factory=list)
    synthetic_indicators: List[str] = Field(default_factory=list)
    context: str = "general"


# =============================================================================
# ENRICHMENT DATA MODELS
# =============================================================================

class EmailEnrichment(BaseModel):
    """Email enrichment data."""
    email: str
    account_age_years: float = 0.0
    breach_count: int = 0
    breaches: List[str] = Field(default_factory=list)
    domain_reputation: str = "unknown"
    is_disposable: bool = False
    is_educational: bool = False
    verified: bool = False
    source: str = "unknown"


class PhoneEnrichment(BaseModel):
    """Phone enrichment data."""
    phone: str
    carrier: str = "Unknown"
    line_type: str = "mobile"
    location: Optional[str] = None
    registration_age_years: float = 0.0
    valid: Optional[bool] = None
    source: str = "unknown"


class AadhaarEnrichment(BaseModel):
    """Aadhaar enrichment data."""
    aadhaar: str
    enrollment_year: Optional[int] = None
    years_active: float = 0.0
    verified: bool = False
    source: str = "estimated"


class PANEnrichment(BaseModel):
    """PAN enrichment data."""
    pan: str
    issue_year: Optional[int] = None
    years_active: float = 0.0
    source: str = "estimated"


class AddressEnrichment(BaseModel):
    """Address enrichment data."""
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    years_at_address: float = 0.0
    valid: Optional[bool] = None
    source: str = "unknown"


class EnrichmentData(BaseModel):
    """All enrichment data combined."""
    email: Optional[EmailEnrichment] = None
    phone: Optional[PhoneEnrichment] = None
    aadhaar: Optional[AadhaarEnrichment] = None
    pan: Optional[PANEnrichment] = None
    address: Optional[AddressEnrichment] = None
    claude_verdict: Optional[ClaudeVerdict] = None


# =============================================================================
# FINAL RESULT MODEL
# =============================================================================

class VerificationResult(BaseModel):
    """Complete verification result."""
    # Identity info
    identity: Dict[str, Any]
    context: str
    
    # Main score
    total_score: float = Field(ge=0, le=100)
    bucket: VerificationBucket
    interpretation: str
    
    # AI Verdict
    claude_verdict: str = "INCONCLUSIVE"
    claude_confidence: int = 0
    claude_reasoning: str = ""
    
    # Score breakdown
    score_breakdown: ScoreBreakdown
    
    # Graph data
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    total_connections: int = 0
    
    # Graph analysis metrics (for synthetic detection)
    graph_density: float = 0.0
    oldest_relationship_years: float = 0.0
    cross_reference_count: int = 0
    synthetic_indicators: List[str] = Field(default_factory=list)
    
    # Red flags & trust
    red_flags: List[RedFlag] = Field(default_factory=list)
    trust_indicators: List[TrustIndicator] = Field(default_factory=list)
    
    # OSINT data
    osint_analysis: Optional[OSINTAnalysis] = None
    domains_seen: List[str] = Field(default_factory=list)
    social_profiles: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Enrichment
    enrichment: Optional[EnrichmentData] = None
    
    # Metadata
    analysis_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    analysis_duration_ms: Optional[int] = None
    queries_executed: int = 0

