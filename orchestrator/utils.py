"""
Utility Functions for SynthGuard Orchestrator
=============================================
Helper functions for logging, data processing, and common operations
"""

import hashlib
import uuid
import base64
import io
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from models import LayerStatusEnum


# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logger(name: str, log_file: Optional[str] = None, level: str = "INFO") -> logging.Logger:
    """
    Set up logger with console and optional file output
    
    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# =============================================================================
# ID GENERATION
# =============================================================================

def generate_verification_id() -> str:
    """
    Generate unique verification ID
    
    Returns:
        Unique ID string (e.g., ver_abc123xyz)
    """
    return f"ver_{uuid.uuid4().hex[:12]}"


def generate_session_id() -> str:
    """
    Generate unique session ID
    
    Returns:
        Unique session ID (e.g., sess_abc123xyz)
    """
    return f"sess_{uuid.uuid4().hex[:12]}"


# =============================================================================
# HASHING & ENCODING
# =============================================================================

def hash_identity(ssn: str, name: str, dob: str) -> str:
    """
    Create consistent hash for identity (used by Layer 5)
    
    Args:
        ssn: SSN or Aadhaar number
        name: Full name
        dob: Date of birth
    
    Returns:
        SHA-256 hash as hex string
    """
    # Normalize inputs
    ssn_clean = ssn.replace('-', '').replace(' ', '').strip()
    name_clean = name.strip().upper()
    dob_clean = dob.strip()
    
    # Create composite string
    identity_string = f"{ssn_clean}|{name_clean}|{dob_clean}"
    
    # Hash
    return hashlib.sha256(identity_string.encode()).hexdigest()


def decode_base64_image(base64_string: str) -> bytes:
    """
    Decode base64 image string to bytes
    
    Args:
        base64_string: Base64 encoded image (with or without data URI prefix)
    
    Returns:
        Image bytes
    """
    # Remove data URI prefix if present
    if ',' in base64_string and base64_string.startswith('data:'):
        base64_string = base64_string.split(',', 1)[1]
    
    return base64.b64decode(base64_string)


def encode_image_to_base64(image_bytes: bytes) -> str:
    """
    Encode image bytes to base64 string
    
    Args:
        image_bytes: Raw image bytes
    
    Returns:
        Base64 encoded string
    """
    return base64.b64encode(image_bytes).decode('utf-8')


# =============================================================================
# DATA VALIDATION
# =============================================================================

def validate_aadhaar(aadhaar: str) -> bool:
    """
    Validate Aadhaar number format
    
    Args:
        aadhaar: Aadhaar number
    
    Returns:
        True if valid format
    """
    # Remove spaces and dashes
    aadhaar_clean = aadhaar.replace(' ', '').replace('-', '')
    
    # Must be exactly 12 digits
    if len(aadhaar_clean) != 12 or not aadhaar_clean.isdigit():
        return False
    
    return True


def validate_pan(pan: str) -> bool:
    """
    Validate PAN number format
    
    Args:
        pan: PAN number
    
    Returns:
        True if valid format
    """
    # Remove spaces
    pan_clean = pan.replace(' ', '').upper()
    
    # Must be exactly 10 characters
    if len(pan_clean) != 10:
        return False
    
    # Format: ABCDE1234F (5 letters, 4 digits, 1 letter)
    if not (pan_clean[:5].isalpha() and 
            pan_clean[5:9].isdigit() and 
            pan_clean[9].isalpha()):
        return False
    
    return True


def validate_phone(phone: str) -> bool:
    """
    Basic phone number validation
    
    Args:
        phone: Phone number with country code
    
    Returns:
        True if valid format
    """
    # Must start with +
    if not phone.startswith('+'):
        return False
    
    # Remove formatting
    phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')
    
    # Must be 10-15 digits
    if not phone_clean.isdigit() or len(phone_clean) < 10 or len(phone_clean) > 15:
        return False
    
    return True


# =============================================================================
# SCORE CALCULATIONS
# =============================================================================

def calculate_weighted_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """
    Calculate weighted average score
    
    Args:
        scores: Dict of layer_id -> score
        weights: Dict of layer_id -> weight
    
    Returns:
        Weighted average score (0-100)
    """
    total_score = 0.0
    total_weight = 0.0
    
    for layer_id, score in scores.items():
        if layer_id in weights and score is not None:
            weight = weights[layer_id]
            total_score += score * weight
            total_weight += weight
    
    if total_weight == 0:
        return 0.0
    
    # Normalize if weights don't sum to 1
    return round(total_score / total_weight, 2) if total_weight != 1.0 else round(total_score, 2)


def determine_confidence(final_score: float, layer_results: Dict[str, Any]) -> str:
    """
    Determine confidence level based on score and layer agreement
    
    Args:
        final_score: Final weighted score
        layer_results: Results from all layers
    
    Returns:
        Confidence level: LOW, MEDIUM, HIGH
    """
    # Count successful layers
    successful_layers = sum(
        1 for r in layer_results.values()
        if hasattr(r, "status") and r.status == LayerStatusEnum.SUCCESS
    )
    total_layers = len(layer_results)
    
    success_rate = successful_layers / total_layers if total_layers > 0 else 0
    
    # Score variance - check if layers agree
    scores = [r.score for r in layer_results.values() if r.status == LayerStatusEnum.SUCCESS]

    if len(scores) > 1:
        score_variance = max(scores) - min(scores)
    else:
        score_variance = 0
    
    # Determine confidence
    if success_rate >= 0.75 and score_variance < 20:
        if final_score > 80 or final_score < 40:
            return "HIGH"
        else:
            return "MEDIUM"
    elif success_rate >= 0.5:
        return "MEDIUM"
    else:
        return "LOW"


def get_verdict_recommendation(verdict: str, confidence: str) -> str:
    """
    Get recommendation text based on verdict and confidence
    
    Args:
        verdict: VERIFIED, SUSPICIOUS, or REJECT
        confidence: LOW, MEDIUM, or HIGH
    
    Returns:
        Human-readable recommendation
    """
    recommendations = {
        ("VERIFIED", "HIGH"): "Identity verified - proceed with confidence",
        ("VERIFIED", "MEDIUM"): "Identity likely authentic - proceed with standard checks",
        ("VERIFIED", "LOW"): "Identity appears authentic - recommend additional verification",
        ("SUSPICIOUS", "HIGH"): "Manual review strongly recommended - multiple red flags detected",
        ("SUSPICIOUS", "MEDIUM"): "Manual review recommended - some concerns identified",
        ("SUSPICIOUS", "LOW"): "Further investigation suggested - limited data available",
        ("REJECT", "HIGH"): "Identity rejected - strong fraud indicators detected",
        ("REJECT", "MEDIUM"): "Identity rejected - multiple suspicious indicators",
        ("REJECT", "LOW"): "Identity rejected - recommend thorough investigation"
    }
    
    return recommendations.get((verdict, confidence), "Manual review recommended")


# =============================================================================
# TIME & DATE UTILITIES
# =============================================================================

def get_timestamp() -> str:
    """
    Get current timestamp in ISO format
    
    Returns:
        ISO 8601 timestamp string
    """
    return datetime.utcnow().isoformat()


def calculate_age(dob: str) -> Optional[int]:
    """
    Calculate age from date of birth
    
    Args:
        dob: Date of birth string (YYYY-MM-DD)
    
    Returns:
        Age in years, or None if invalid format
    """
    try:
        birth_date = datetime.strptime(dob, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except:
        return None


# =============================================================================
# ERROR HANDLING
# =============================================================================

def format_error_response(error: Exception, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Format exception into error response
    
    Args:
        error: Exception object
        details: Optional additional details
    
    Returns:
        Error response dict
    """
    return {
        "error": type(error).__name__,
        "message": str(error),
        "details": details or {},
        "timestamp": get_timestamp()
    }


# =============================================================================
# DATA SANITIZATION
# =============================================================================

def sanitize_phone(phone: str) -> str:
    """
    Sanitize phone number to consistent format
    
    Args:
        phone: Raw phone number
    
    Returns:
        Sanitized phone number
    """
    # Keep only digits and +
    return '+' + ''.join(c for c in phone if c.isdigit())


def sanitize_aadhaar(aadhaar: str) -> str:
    """
    Sanitize Aadhaar to consistent format
    
    Args:
        aadhaar: Raw Aadhaar number
    
    Returns:
        Sanitized Aadhaar (12 digits, no spaces/dashes)
    """
    return ''.join(c for c in aadhaar if c.isdigit())


def sanitize_pan(pan: str) -> str:
    """
    Sanitize PAN to consistent format
    
    Args:
        pan: Raw PAN number
    
    Returns:
        Sanitized PAN (uppercase, no spaces)
    """
    return pan.replace(' ', '').upper()


# =============================================================================
# FILE UTILITIES
# =============================================================================

def ensure_directory_exists(directory: str) -> Path:
    """
    Ensure directory exists, create if not
    
    Args:
        directory: Directory path
    
    Returns:
        Path object
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_temp_file(data: bytes, filename: str, directory: str = "/tmp/synthguard") -> str:
    """
    Save temporary file
    
    Args:
        data: File data bytes
        filename: Filename
        directory: Directory to save to
    
    Returns:
        Full file path
    """
    ensure_directory_exists(directory)
    filepath = Path(directory) / filename
    
    with open(filepath, 'wb') as f:
        f.write(data)
    
    return str(filepath)


# =============================================================================
# VISUALIZATION HELPERS
# =============================================================================

def prepare_score_chart_data(layer_contributions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Prepare data for score breakdown chart
    
    Args:
        layer_contributions: List of layer contribution dicts
    
    Returns:
        Chart-ready data structure
    """
    return {
        "labels": [lc["layer_name"] for lc in layer_contributions],
        "scores": [lc["score"] for lc in layer_contributions],
        "weights": [lc["weight"] for lc in layer_contributions],
        "contributions": [lc["contribution"] for lc in layer_contributions]
    }


# =============================================================================
# CONSTANTS
# =============================================================================

# Default weights
DEFAULT_WEIGHTS = {
    "layer_1": 0.25,
    "layer_2_3": 0.50,
    "layer_4": 0.15,
    "layer_5": 0.10
}

# Verdict thresholds
THRESHOLD_VERIFIED = 90
THRESHOLD_SUSPICIOUS = 50

# Layer names
LAYER_NAMES = {
    "layer_1": "Document Forensics",
    "layer_2_3": "OSINT + Graph Analysis",
    "layer_4": "Behavioral Patterns",
    "layer_5": "Blockchain Verification"
}