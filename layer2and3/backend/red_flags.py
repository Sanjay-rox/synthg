"""
Unified Identity Verification System - Red Flag Detection (FULLY FIXED)
========================================================================

FIXED:
1. Improved email pattern detection (student IDs, legitimate patterns)
2. Corrected Aadhaar year validation
3. More lenient scoring for real identities
4. Better context awareness
"""

import re
from typing import Any, Dict, List, Set, Tuple, Optional

from models import RedFlag, RedFlagSeverity


# =============================================================================
# KNOWN FRAUD INDICATORS
# =============================================================================

DISPOSABLE_EMAIL_DOMAINS: Set[str] = {
    "tempmail.com", "guerrillamail.com", "10minutemail.com", "mailinator.com",
    "throwaway.email", "fakeinbox.com", "trashmail.com", "getnada.com",
    "temp-mail.org", "dispostable.com", "maildrop.cc", "yopmail.com",
    "mohmal.com", "emailondeck.com", "mintemail.com", "sharklasers.com",
    "spamgourmet.com", "mytemp.email", "tempail.com", "tmpmail.org",
    "guerrillamailblock.com", "grr.la", "pokemail.net", "spam4.me",
    "mailcatch.com", "tempsky.com", "wegwerfmail.de", "byom.de",
    "spambog.com", "trash-mail.at", "mailnesia.com", "mailsac.com",
    "burnermail.io", "tempinbox.com", "emailfake.com", "crazymailing.com",
    "dropmail.me", "getairmail.com", "fakemailgenerator.com",
}

EDUCATIONAL_DOMAINS: Set[str] = {
    ".edu", ".edu.in", ".edu.au", ".edu.uk", ".ac.in", ".ac.uk",
    ".ac.jp", ".edu.cn", ".edu.br", ".ac.nz",
}

ESTABLISHED_EMAIL_PROVIDERS: Set[str] = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "icloud.com", "protonmail.com", "aol.com", "live.com",
}


# =============================================================================
# IMPROVED EMAIL PATTERN DETECTION
# =============================================================================

def is_legitimate_email_pattern(local_part: str, domain: str) -> bool:
    """
    Determine if email pattern is legitimate.
    
    Returns True if pattern looks legitimate, False if suspicious.
    """
    local_lower = local_part.lower()
    
    # 1. Student ID patterns (numbers with optional prefix/suffix)
    # Examples: 221801014@, cs21b001@, 2021bcs001@
    if re.match(r'^[a-z]{0,4}\d{6,12}[a-z]{0,4}$', local_lower):
        return True
    
    # 2. Name-based patterns (firstname.lastname, firstname_lastname)
    # Examples: john.doe@, jane_smith@, rajkumar123@
    if re.match(r'^[a-z]+[\._-]?[a-z]+\d{0,3}$', local_lower):
        return True
    
    # 3. Name with numbers (common legitimate pattern)
    # Examples: john123@, raj.kumar99@
    if re.match(r'^[a-z]+[\._-]?[a-z]*\d{1,4}$', local_lower):
        return True
    
    # 4. Professional email formats
    professional_prefixes = ['info', 'contact', 'support', 'admin', 'sales', 
                            'hello', 'team', 'help', 'service', 'office']
    if local_lower in professional_prefixes:
        return True
    
    # 5. Educational domains likely legitimate
    if any(edu in domain for edu in EDUCATIONAL_DOMAINS):
        return True
    
    # 6. Check for truly random pattern (red flag)
    if len(local_lower) >= 12:
        vowel_count = sum(1 for c in local_lower if c in 'aeiou')
        if vowel_count < 2 and not re.search(r'\d', local_lower):
            return False
        
        if re.match(r'^\d{15,}$', local_lower):
            return False
        
        if re.match(r'^[a-f0-9]{20,}$', local_lower):
            return False
    
    # Default: assume legitimate
    return True


# =============================================================================
# RED FLAG DETECTOR (FULLY FIXED)
# =============================================================================

class RedFlagDetector:
    """
    Detect fraud indicators in identity data.
    Context-aware with lenient thresholds for legitimate identities.
    
    FULLY FIXED:
    - Better email pattern detection
    - Corrected Aadhaar year validation (2010+)
    - More lenient penalties
    - Better context handling
    """
    
    def __init__(self, is_student: bool = False, is_indian: bool = False):
        """
        Initialize detector.
        
        Args:
            is_student: Apply student context (very lenient)
            is_indian: Apply Indian context (Aadhaar/PAN validation)
        """
        self.is_student = is_student
        self.is_indian = is_indian
        # Reduced penalty multiplier for students
        self.penalty_multiplier = 0.3 if is_student else 0.7
    
    def detect_all(
        self,
        identity: Dict[str, Any],
        enrichment: Dict[str, Any],
        osint_data: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[RedFlag], float]:
        """
        Detect all red flags.
        
        Returns:
            Tuple of (red_flags, total_penalty)
        """
        flags: List[RedFlag] = []
        
        # 1. Email red flags (FIXED)
        flags.extend(self._check_email(identity, enrichment))
        
        # 2. Phone red flags
        flags.extend(self._check_phone(identity, enrichment))
        
        # 3. Temporal red flags (lenient)
        flags.extend(self._check_temporal(enrichment))
        
        # 4. Indian document red flags (FIXED Aadhaar logic)
        if self.is_indian:
            flags.extend(self._check_indian_documents(identity, enrichment))
        
        # 5. OSINT red flags (lenient)
        if osint_data:
            flags.extend(self._check_osint(osint_data))
        
        # 6. Cross-validation
        flags.extend(self._check_cross_validation(identity, enrichment))
        
        # Calculate total penalty
        total_penalty = sum(f.penalty for f in flags)
        
        return flags, total_penalty
    
    def _check_email(
        self,
        identity: Dict,
        enrichment: Dict,
    ) -> List[RedFlag]:
        """Check email for fraud indicators (FIXED)."""
        flags = []
        email = identity.get('email', '')
        
        if not email or '@' not in email:
            return flags
        
        local_part, domain = email.lower().split('@', 1)
        email_data = enrichment.get('email', {})
        
        # 1. CRITICAL: Disposable email (only real red flag)
        if domain in DISPOSABLE_EMAIL_DOMAINS:
            flags.append(RedFlag(
                code="DISPOSABLE_EMAIL",
                description=f"Disposable email domain: {domain}",
                severity=RedFlagSeverity.CRITICAL,
                penalty=50.0,
                evidence=domain,
            ))
            return flags  # This is critical, stop here
        
        # 2. Check pattern legitimacy (FIXED LOGIC)
        is_legitimate = is_legitimate_email_pattern(local_part, domain)
        
        if not is_legitimate:
            flags.append(RedFlag(
                code="SUSPICIOUS_EMAIL_PATTERN",
                description="Email pattern appears generated/random",
                severity=RedFlagSeverity.MEDIUM,
                penalty=10.0 * self.penalty_multiplier,
                evidence=local_part,
            ))
        
        # 3. Excessive breaches (very high threshold)
        breach_count = email_data.get('breach_count', 0)
        if breach_count > 15:
            flags.append(RedFlag(
                code="EXCESSIVE_BREACHES",
                description=f"Email in {breach_count} data breaches",
                severity=RedFlagSeverity.MEDIUM,
                penalty=8.0 * self.penalty_multiplier,
                evidence=str(breach_count),
            ))
        
        return flags
    
    def _check_phone(
        self,
        identity: Dict,
        enrichment: Dict,
    ) -> List[RedFlag]:
        """Check phone for fraud indicators."""
        flags = []
        phone_data = enrichment.get('phone', {})
        
        # Only flag if explicitly invalid
        if phone_data.get('valid') is False:
            flags.append(RedFlag(
                code="INVALID_PHONE",
                description="Phone number validation failed",
                severity=RedFlagSeverity.HIGH,
                penalty=15.0 * self.penalty_multiplier,
            ))
        
        # Very new phone (less than 6 months)
        reg_age = phone_data.get('registration_age_years', 5)
        if reg_age < 0.5 and not self.is_student:
            flags.append(RedFlag(
                code="NEW_PHONE",
                description="Phone number less than 6 months old",
                severity=RedFlagSeverity.LOW,
                penalty=5.0 * self.penalty_multiplier,
            ))
        
        return flags
    
    def _check_temporal(self, enrichment: Dict) -> List[RedFlag]:
        """Check temporal consistency (very lenient)."""
        flags = []
        
        # Get all ages
        ages = []
        if enrichment.get('email', {}).get('account_age_years'):
            ages.append(enrichment['email']['account_age_years'])
        if enrichment.get('phone', {}).get('registration_age_years'):
            ages.append(enrichment['phone']['registration_age_years'])
        if enrichment.get('aadhaar', {}).get('years_active'):
            ages.append(enrichment['aadhaar']['years_active'])
        if enrichment.get('pan', {}).get('years_active'):
            ages.append(enrichment['pan']['years_active'])
        
        if not ages:
            return flags
        
        max_age = max(ages)
        
        # Only flag EXTREMELY new (less than 3 months)
        if max_age < 0.25 and not self.is_student:
            flags.append(RedFlag(
                code="BRAND_NEW_FOOTPRINT",
                description="All identity elements less than 3 months old",
                severity=RedFlagSeverity.HIGH,
                penalty=25.0,
            ))
        
        return flags
    
    def _check_indian_documents(
        self,
        identity: Dict,
        enrichment: Dict,
    ) -> List[RedFlag]:
        """Check Indian documents (FIXED Aadhaar logic)."""
        flags = []
        
        aadhaar_data = enrichment.get('aadhaar', {})
        pan_data = enrichment.get('pan', {})
        
        # FIXED: Aadhaar before 2010 is IMPOSSIBLE
        aadhaar_year = aadhaar_data.get('enrollment_year')
        if aadhaar_year and aadhaar_year < 2010:
            flags.append(RedFlag(
                code="IMPOSSIBLE_AADHAAR_DATE",
                description=f"Aadhaar enrollment year {aadhaar_year} before system launch (2010)",
                severity=RedFlagSeverity.CRITICAL,
                penalty=35.0,
                evidence=str(aadhaar_year),
            ))
        
        # PAN before age 16 (lenient threshold)
        dob = identity.get('dob', '')
        pan_year = pan_data.get('issue_year')
        if dob and pan_year:
            try:
                birth_year = int(dob[:4])
                age_at_pan = pan_year - birth_year
                if age_at_pan < 16:
                    flags.append(RedFlag(
                        code="PAN_TOO_YOUNG",
                        description=f"PAN issued when person was {age_at_pan} years old",
                        severity=RedFlagSeverity.LOW,
                        penalty=8.0 * self.penalty_multiplier,
                    ))
            except:
                pass
        
        return flags
    
    def _check_osint(self, osint_data: Dict) -> List[RedFlag]:
        """Check OSINT results (lenient)."""
        flags = []
        
        total_hits = osint_data.get('total_hits', 0)
        
        # Only flag zero presence for non-students
        if total_hits == 0 and not self.is_student:
            flags.append(RedFlag(
                code="NO_ONLINE_PRESENCE",
                description="Zero search results found",
                severity=RedFlagSeverity.MEDIUM,
                penalty=20.0,
            ))
        
        return flags
    
    def _check_cross_validation(
        self,
        identity: Dict,
        enrichment: Dict,
    ) -> List[RedFlag]:
        """Check cross-validation."""
        flags = []
        
        # Invalid address (lenient)
        address_data = enrichment.get('address', {})
        if address_data.get('valid') is False:
            flags.append(RedFlag(
                code="INVALID_ADDRESS",
                description="PIN code validation failed",
                severity=RedFlagSeverity.LOW,
                penalty=5.0 * self.penalty_multiplier,
            ))
        
        return flags


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def detect_red_flags(
    identity: Dict[str, Any],
    enrichment: Dict[str, Any],
    osint_data: Optional[Dict[str, Any]] = None,
    context: str = "professional",
) -> Tuple[List[RedFlag], float]:
    """
    Convenience function to detect all red flags.
    
    Args:
        identity: Identity input data
        enrichment: API enrichment data
        osint_data: OSINT search results
        context: "student", "professional", or "executive"
        
    Returns:
        Tuple of (red_flags, total_penalty)
    """
    is_student = context == "student"
    
    # Auto-detect student from email
    email = identity.get('email', '')
    if email and '@' in email:
        domain = email.split('@')[1].lower()
        if any(edu in domain for edu in EDUCATIONAL_DOMAINS):
            is_student = True
    
    # Detect Indian context
    is_indian = bool(identity.get('aadhaar') or identity.get('pan'))
    
    detector = RedFlagDetector(is_student=is_student, is_indian=is_indian)
    return detector.detect_all(identity, enrichment, osint_data)