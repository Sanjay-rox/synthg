"""
Unified Identity Verification System - Red Flag Detection
==========================================================

Comprehensive fraud indicator detection with context awareness.
"""

import re
from typing import Any, Dict, List, Set, Tuple,Optional

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
# RED FLAG DETECTOR
# =============================================================================

class RedFlagDetector:
    """
    Detect fraud indicators in identity data.
    Context-aware: students get relaxed thresholds.
    """
    
    def __init__(self, is_student: bool = False, is_indian: bool = False):
        """
        Initialize detector.
        
        Args:
            is_student: Apply student context (relaxed thresholds)
            is_indian: Apply Indian context (Aadhaar/PAN logic)
        """
        self.is_student = is_student
        self.is_indian = is_indian
        self.penalty_multiplier = 0.4 if is_student else 1.0
    
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
        
        # 1. Email red flags
        flags.extend(self._check_email(identity, enrichment))
        
        # 2. Phone red flags
        flags.extend(self._check_phone(identity, enrichment))
        
        # 3. Temporal red flags
        flags.extend(self._check_temporal(enrichment))
        
        # 4. Indian document red flags
        if self.is_indian:
            flags.extend(self._check_indian_documents(identity, enrichment))
        
        # 5. OSINT red flags
        if osint_data:
            flags.extend(self._check_osint(osint_data))
        
        # 6. Cross-validation red flags
        flags.extend(self._check_cross_validation(identity, enrichment))
        
        # Calculate total penalty
        total_penalty = sum(f.penalty for f in flags)
        
        return flags, total_penalty
    
    def _check_email(
        self,
        identity: Dict,
        enrichment: Dict,
    ) -> List[RedFlag]:
        """Check email for fraud indicators."""
        flags = []
        email = identity.get('email', '')
        
        if not email or '@' not in email:
            return flags
        
        local_part, domain = email.lower().split('@', 1)
        email_data = enrichment.get('email', {})
        
        # 1. CRITICAL: Disposable email
        if domain in DISPOSABLE_EMAIL_DOMAINS:
            flags.append(RedFlag(
                code="DISPOSABLE_EMAIL",
                description=f"Disposable email domain: {domain}",
                severity=RedFlagSeverity.CRITICAL,
                penalty=50.0,
                evidence=domain,
            ))
        
        # 2. MEDIUM: Random pattern (but not student IDs)
        is_educational = any(edu in domain for edu in EDUCATIONAL_DOMAINS)
        looks_like_roll_number = re.match(r'^\d{6,12}$', local_part)
        looks_random = (
            re.match(r'^[a-z0-9]{10,}$', local_part) and
            not re.search(r'[aeiou]{2,}', local_part)
        )
        
        if looks_random and not looks_like_roll_number and not is_educational:
            flags.append(RedFlag(
                code="RANDOM_EMAIL_PATTERN",
                description="Email appears randomly generated",
                severity=RedFlagSeverity.MEDIUM,
                penalty=15.0 * self.penalty_multiplier,
                evidence=local_part,
            ))
        
        # 3. HIGH: Multiple breaches
        breach_count = email_data.get('breach_count', 0)
        if breach_count > 10:
            flags.append(RedFlag(
                code="EXCESSIVE_BREACHES",
                description=f"Email in {breach_count} data breaches",
                severity=RedFlagSeverity.HIGH,
                penalty=12.0 * self.penalty_multiplier,
                evidence=str(breach_count),
            ))
        
        # 4. LOW: Unknown/suspicious domain (not student context)
        if not self.is_student and not is_educational:
            if domain not in ESTABLISHED_EMAIL_PROVIDERS and not email_data.get('is_corporate'):
                # Check if it looks suspicious
                if len(domain.split('.')[0]) <= 3 or domain.count('.') > 2:
                    flags.append(RedFlag(
                        code="SUSPICIOUS_EMAIL_DOMAIN",
                        description=f"Unusual email domain: {domain}",
                        severity=RedFlagSeverity.LOW,
                        penalty=5.0 * self.penalty_multiplier,
                        evidence=domain,
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
        
        # Invalid phone
        if phone_data.get('valid') is False:
            flags.append(RedFlag(
                code="INVALID_PHONE",
                description="Phone number validation failed",
                severity=RedFlagSeverity.HIGH,
                penalty=20.0 * self.penalty_multiplier,
            ))
        
        # Very new phone (Jio launched 2016)
        reg_age = phone_data.get('registration_age_years', 5)
        if reg_age < 1 and not self.is_student:
            flags.append(RedFlag(
                code="NEW_PHONE",
                description="Phone number less than 1 year old",
                severity=RedFlagSeverity.MEDIUM,
                penalty=10.0 * self.penalty_multiplier,
            ))
        
        return flags
    
    def _check_temporal(self, enrichment: Dict) -> List[RedFlag]:
        """Check temporal consistency."""
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
        
        # CRITICAL: Brand new footprint
        if max_age < 1 and not self.is_student:
            flags.append(RedFlag(
                code="BRAND_NEW_FOOTPRINT",
                description="All identity elements less than 1 year old",
                severity=RedFlagSeverity.CRITICAL,
                penalty=40.0,
            ))
        # HIGH: Recent footprint
        elif max_age < 2 and not self.is_student:
            flags.append(RedFlag(
                code="RECENT_FOOTPRINT",
                description="All identity elements less than 2 years old",
                severity=RedFlagSeverity.HIGH,
                penalty=25.0 * self.penalty_multiplier,
            ))
        
        return flags
    
    def _check_indian_documents(
        self,
        identity: Dict,
        enrichment: Dict,
    ) -> List[RedFlag]:
        """Check Indian document consistency."""
        flags = []
        
        aadhaar_data = enrichment.get('aadhaar', {})
        pan_data = enrichment.get('pan', {})
        
        # Aadhaar before 2010 (impossible)
        aadhaar_year = aadhaar_data.get('enrollment_year')
        if aadhaar_year and aadhaar_year < 2010:
            flags.append(RedFlag(
                code="IMPOSSIBLE_AADHAAR_DATE",
                description=f"Aadhaar enrollment year {aadhaar_year} before system launch (2010)",
                severity=RedFlagSeverity.CRITICAL,
                penalty=35.0,
                evidence=str(aadhaar_year),
            ))
        
        # PAN before age 18 (unusual)
        dob = identity.get('dob', '')
        pan_year = pan_data.get('issue_year')
        if dob and pan_year:
            try:
                birth_year = int(dob[:4])
                if pan_year - birth_year < 16:
                    flags.append(RedFlag(
                        code="PAN_TOO_YOUNG",
                        description=f"PAN issued when person was {pan_year - birth_year} years old",
                        severity=RedFlagSeverity.MEDIUM,
                        penalty=12.0 * self.penalty_multiplier,
                    ))
            except:
                pass
        
        return flags
    
    def _check_osint(self, osint_data: Dict) -> List[RedFlag]:
        """Check OSINT results for red flags."""
        flags = []
        
        total_hits = osint_data.get('total_hits', 0)
        
        # No online presence (non-student)
        if total_hits == 0 and not self.is_student:
            flags.append(RedFlag(
                code="NO_ONLINE_PRESENCE",
                description="Zero search results found",
                severity=RedFlagSeverity.CRITICAL,
                penalty=45.0,
            ))
        # Minimal presence
        elif total_hits < 3 and not self.is_student:
            flags.append(RedFlag(
                code="MINIMAL_ONLINE_PRESENCE",
                description=f"Only {total_hits} search results found",
                severity=RedFlagSeverity.HIGH,
                penalty=20.0 * self.penalty_multiplier,
            ))
        
        # No high-trust domains
        high_trust = osint_data.get('high_trust_count', 0)
        if total_hits > 5 and high_trust == 0 and not self.is_student:
            flags.append(RedFlag(
                code="NO_TRUSTED_SOURCES",
                description="No mentions on established platforms",
                severity=RedFlagSeverity.MEDIUM,
                penalty=12.0 * self.penalty_multiplier,
            ))
        
        return flags
    
    def _check_cross_validation(
        self,
        identity: Dict,
        enrichment: Dict,
    ) -> List[RedFlag]:
        """Check cross-validation between data sources."""
        flags = []
        
        # Address/PIN validation
        address_data = enrichment.get('address', {})
        if address_data.get('valid') is False:
            flags.append(RedFlag(
                code="INVALID_ADDRESS",
                description="PIN code validation failed",
                severity=RedFlagSeverity.MEDIUM,
                penalty=10.0 * self.penalty_multiplier,
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

