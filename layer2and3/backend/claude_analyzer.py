"""
Unified Identity Verification System - Claude AI Analyzer (FULLY FIXED)
========================================================================

FIXED:
1. Aadhaar enrollment year calculation (enforces 2010+ minimum)
2. Better DOB parsing and validation
3. More accurate age estimation logic
4. Improved prompting for better AI analysis
"""

import json
import os
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

import aiohttp

from models import ClaudeVerdict, IdentityContext
from api_integrations import APIConfig, EDUCATIONAL_DOMAINS


# =============================================================================
# CLAUDE ANALYZER (FULLY FIXED)
# =============================================================================

class ClaudeAnalyzer:
    """
    Claude AI-powered identity analysis.
    Provides holistic verdicts on identity authenticity.
    
    FIXED: 
    - Aadhaar year calculation correctly enforces 2010+ minimum
    - Better email pattern recognition
    - More lenient scoring for legitimate identities
    """
    
    def __init__(self):
        self.api_key = APIConfig.GROQ_API_KEY
        self.model = APIConfig.GROQ_MODEL
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.current_year = datetime.now().year

    
    async def analyze_identity(
        self,
        identity: Dict[str, Any],
        osint_results: Optional[List[Dict]] = None,
        enrichment_data: Optional[Dict] = None,
    ) -> ClaudeVerdict:
        """
        Perform comprehensive identity analysis.
        
        Returns:
            ClaudeVerdict with verdict, confidence, reasoning
        """
        if not self.api_key:
            print("⚠️ Claude API key not configured")
            return ClaudeVerdict(
                verdict="LIKELY_REAL",
                confidence=60,
                reasoning="Claude AI not available - assuming legitimate based on available data",
            )
        
        try:
            prompt = self._build_comprehensive_prompt(
                identity, osint_results, enrichment_data
            )
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }   
                
                payload = {
                    "model": self.model,
                    "temperature": 0.1,
                    "max_tokens": 2500,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an elite identity verification analyst. Be MORE LENIENT with legitimate identities. Focus on POSITIVE fraud indicators, not absence of data. Many real people have minimal online presence."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
                
                async with session.post(
                    self.endpoint,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=90)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        text = data["choices"][0]["message"]["content"]
                        
                        verdict = self._parse_verdict(text)
                        print(f"✅ Claude: {verdict.verdict} ({verdict.confidence}%)")
                        return verdict
                    else:
                        error = await response.text()
                        print(f"❌ Claude API error: {response.status} - {error[:100]}")
                        return ClaudeVerdict(
                            verdict="LIKELY_REAL",
                            confidence=60,
                            reasoning=f"API error - assuming legitimate based on available data",
                        )
                        
        except Exception as e:
            print(f"❌ Claude exception: {e}")
            return ClaudeVerdict(
                verdict="LIKELY_REAL",
                confidence=60,
                reasoning=f"Analysis error - assuming legitimate based on available data",
            )
    
    def _build_comprehensive_prompt(
        self,
        identity: Dict,
        osint_results: Optional[List[Dict]],
        enrichment: Optional[Dict],
    ) -> str:
        """Build comprehensive analysis prompt with improved guidance."""
        
        # Detect context
        email = identity.get('email', '')
        is_student = identity.get('context') == 'student'
        if email:
            domain = email.split('@')[1] if '@' in email else ''
            if any(edu in domain for edu in EDUCATIONAL_DOMAINS):
                is_student = True
        
        has_aadhaar = bool(identity.get('aadhaar'))
        has_pan = bool(identity.get('pan'))
        is_indian = has_aadhaar or has_pan
        
        # Build prompt
        prompt = f"""═══════════════════════════════════════════════════════════════════════
UNIFIED IDENTITY VERIFICATION ANALYSIS - BE LENIENT WITH REAL IDENTITIES
═══════════════════════════════════════════════════════════════════════

You are an elite identity verification analyst. Analyze this identity to
determine if it's REAL or SYNTHETIC (fake/manufactured).

CRITICAL INSTRUCTIONS:
1. Many REAL people have LIMITED online presence - this is NORMAL
2. Focus on POSITIVE fraud indicators (disposable email, impossible dates)
3. Absence of data is NOT fraud evidence
4. Be MORE LENIENT with legitimate patterns
5. Default to LIKELY_REAL unless clear fraud evidence exists

══════════════════════════════════════════════════════════════════════
IDENTITY DATA
══════════════════════════════════════════════════════════════════════

Name:     {identity.get('name', 'Not provided')}
Email:    {identity.get('email', 'Not provided')}
Phone:    {identity.get('phone', 'Not provided')}
Username: {identity.get('username', 'Not provided')}
Company:  {identity.get('company', 'Not provided')}
Location: {identity.get('location', 'Not provided')}
DOB:      {identity.get('dob', 'Not provided')}
"""
        
        if is_indian:
            prompt += f"""
INDIAN DOCUMENTS:
Aadhaar:  {identity.get('aadhaar', 'Not provided')}
PAN:      {identity.get('pan', 'Not provided')}
"""
        
        # Add enrichment data
        if enrichment:
            prompt += """
══════════════════════════════════════════════════════════════════════
API ENRICHMENT DATA
══════════════════════════════════════════════════════════════════════
"""
            if enrichment.get('email'):
                e = enrichment['email']
                prompt += f"""
EMAIL ANALYSIS:
  - Account age: {e.get('account_age_years', 'Unknown')} years
  - Breach count: {e.get('breach_count', 0)} (MORE breaches = MORE real)
  - Breaches: {', '.join(e.get('breaches', [])[:5]) or 'None'}
  - Domain reputation: {e.get('domain_reputation', 'Unknown')}
  - Is disposable: {e.get('is_disposable', False)} (TRUE = RED FLAG)
  - Is educational: {e.get('is_educational', False)}
"""
            
            if enrichment.get('phone'):
                p = enrichment['phone']
                prompt += f"""
PHONE ANALYSIS:
  - Carrier: {p.get('carrier', 'Unknown')}
  - Valid: {p.get('valid', 'Unknown')}
  - Registration age: {p.get('registration_age_years', 'Unknown')} years
  - Location: {p.get('location', 'Unknown')}
"""
            
            if enrichment.get('aadhaar'):
                a = enrichment['aadhaar']
                prompt += f"""
AADHAAR ANALYSIS:
  - Years active: {a.get('years_active', 0)}
  - Enrollment year: {a.get('enrollment_year', 'Unknown')}
  - CRITICAL: Aadhaar started in 2010 - ANY year before 2010 is IMPOSSIBLE
"""
            
            if enrichment.get('pan'):
                p = enrichment['pan']
                prompt += f"""
PAN ANALYSIS:
  - Years active: {p.get('years_active', 0)}
  - Issue year: {p.get('issue_year', 'Unknown')}
"""
            
            if enrichment.get('address'):
                a = enrichment['address']
                prompt += f"""
ADDRESS ANALYSIS:
  - City: {a.get('city', 'Unknown')}
  - State: {a.get('state', 'Unknown')}
  - PIN valid: {a.get('valid', 'Unknown')}
"""
        
        # Add OSINT results
        if osint_results and len(osint_results) > 0:
            prompt += f"""
══════════════════════════════════════════════════════════════════════
OSINT SEARCH RESULTS ({len(osint_results)} found)
══════════════════════════════════════════════════════════════════════
"""
            for i, hit in enumerate(osint_results[:15], 1):
                prompt += f"""
{i}. [{hit.get('domain', 'unknown')}] {hit.get('title', '')[:80]}
   URL: {hit.get('url', '')}
   Date: {hit.get('published', 'unknown')}
   >>> {hit.get('snippet', '')[:250]}
"""
        else:
            prompt += """
══════════════════════════════════════════════════════════════════════
OSINT SEARCH RESULTS: NONE FOUND
══════════════════════════════════════════════════════════════════════

IMPORTANT: No search results does NOT automatically mean synthetic!
Many REAL people have minimal online presence:
- Students with institutional emails
- People in regions with less web indexing  
- Privacy-conscious individuals
- Young professionals just starting careers
- People who don't use social media

ONLY mark as suspicious if there are POSITIVE fraud indicators:
- Disposable email domains
- Impossible dates (Aadhaar before 2010)
- Invalid phone numbers
- Truly random/generated email patterns
"""
        
        # Add context notes
        if is_student:
            prompt += """
══════════════════════════════════════════════════════════════════════
CONTEXT: STUDENT DETECTED - BE VERY LENIENT
══════════════════════════════════════════════════════════════════════
✓ Students have LIMITED online presence - COMPLETELY NORMAL
✓ Student ID emails like 221801014@ are LEGITIMATE formats
✓ Absence of LinkedIn/professional profiles is EXPECTED
✓ 1-4 year digital footprint is TYPICAL for college students
✓ Email patterns with numbers are NORMAL (roll numbers)
✓ Minimal OSINT results are EXPECTED

DEFAULT VERDICT for students: LIKELY_REAL unless clear fraud evidence
"""
        
        if is_indian:
            prompt += """
══════════════════════════════════════════════════════════════════════
CONTEXT: INDIAN IDENTITY
══════════════════════════════════════════════════════════════════════
- Aadhaar enrollment started in 2010 (NOTHING BEFORE 2010 POSSIBLE)
- PAN typically issued when person is 18+
- Indian phone carriers: Jio (2016), Airtel (1995), VI (2018), BSNL (2000)
- PIN codes are 6 digits
"""
        
        # Output format
        prompt += f"""
══════════════════════════════════════════════════════════════════════
REQUIRED OUTPUT (JSON ONLY) - Current Year: {self.current_year}
══════════════════════════════════════════════════════════════════════

Return ONLY valid JSON:

{{
  "verdict": "REAL" | "LIKELY_REAL" | "INCONCLUSIVE" | "SUSPICIOUS" | "SYNTHETIC",
  "confidence": 0-100,
  "reasoning": "2-3 sentence explanation focusing on REAL fraud indicators",
  
  "identity_correlation": {{
    "name_email_linked": true/false,
    "name_phone_linked": true/false,
    "email_phone_linked": true/false,
    "documents_consistent": true/false
  }},
  
  "temporal_analysis": {{
    "estimated_footprint_years": <int>,
    "temporal_consistency": "consistent" | "suspicious" | "too_recent",
    "aadhaar_years": <int or 0>,
    "pan_years": <int or 0>,
    "email_years": <int or 0>,
    "phone_years": <int or 0>
  }},
  
  "platform_presence": {{
    "has_linkedin": true/false,
    "has_github": true/false,
    "has_social_media": true/false,
    "profile_count": <int>
  }},
  
  "trust_indicators": ["list of positive signals"],
  "synthetic_indicators": ["ONLY REAL fraud evidence - not absence of data"],
  
  "format_analysis": {{
    "email_legitimate": true/false,
    "phone_legitimate": true/false,
    "name_legitimate": true/false,
    "documents_legitimate": true/false
  }},
  
  "context": "student" | "professional" | "general"
}}

VERDICT GUIDELINES (BE MORE LENIENT):
- REAL: Strong evidence of real person (70-100% confidence)
- LIKELY_REAL: No major red flags, legitimate formats (50-70% confidence)
  * DEFAULT for students with no fraud indicators
  * DEFAULT for anyone with legitimate email/phone
- INCONCLUSIVE: Cannot determine clearly (30-50% confidence)
- SUSPICIOUS: Clear inconsistencies found (20-30% confidence)
- SYNTHETIC: Strong POSITIVE fraud evidence (0-20% confidence)
  * Disposable email
  * Impossible dates
  * Invalid/fake documents

CRITICAL RULES:
1. "Limited online presence" is NOT fraud evidence
2. Email with numbers (221801014@) is NORMAL for students
3. For students, DEFAULT to LIKELY_REAL unless clear fraud
4. Breach history indicates REAL person (shows account history)
5. ONLY mark SYNTHETIC if POSITIVE fraud indicators exist

Return ONLY the JSON object, no other text.
"""
        
        return prompt
    
    def _parse_verdict(self, text: str) -> ClaudeVerdict:
        """Parse Claude's response into ClaudeVerdict."""
        
        # Extract JSON
        json_match = re.search(r'```json?\s*([\s\S]*?)\s*```', text)
        if json_match:
            text = json_match.group(1)
        
        start = text.find('{')
        end = text.rfind('}')
        
        if start == -1 or end == -1:
            return ClaudeVerdict(
                verdict="LIKELY_REAL",
                confidence=65,
                reasoning="Could not parse AI response - assuming legitimate based on data",
            )
        
        try:
            # Clean JSON
            json_str = text[start:end + 1]
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            
            data = json.loads(json_str)
            
            verdict = data.get('verdict', 'LIKELY_REAL').upper()
            confidence = data.get('confidence', 65)
            
            # Safety check: ensure reasonable confidence
            if confidence < 0:
                confidence = 0
            elif confidence > 100:
                confidence = 100
            
            return ClaudeVerdict(
                verdict=verdict,
                confidence=confidence,
                reasoning=data.get('reasoning', 'Analysis completed'),
                trust_indicators=data.get('trust_indicators', []),
                synthetic_indicators=data.get('synthetic_indicators', []),
                context=data.get('context', 'general'),
            )
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            return ClaudeVerdict(
                verdict="LIKELY_REAL",
                confidence=65,
                reasoning="Failed to parse AI response - assuming legitimate",
            )
    
    async def estimate_document_ages(
        self,
        identity: Dict[str, Any],
    ) -> Dict[str, int]:
        """
        Estimate ages of Indian documents based on DOB.
        
        FIXED: Now correctly enforces Aadhaar minimum year of 2010
        
        Returns:
            Dict with aadhaar_years, pan_years, email_years, phone_years
        """
        if not self.api_key:
            return self._fallback_age_estimation(identity)
        
        try:
            dob = identity.get('dob', '')
            
            prompt = f"""Estimate document ages for Indian identity:

Name: {identity.get('name', 'Unknown')}
DOB: {dob}
Aadhaar: {identity.get('aadhaar', 'Not provided')}
PAN: {identity.get('pan', 'Not provided')}
Email: {identity.get('email', 'Not provided')}
Phone: {identity.get('phone', 'Not provided')}

Current year: {self.current_year}

CRITICAL RULES:
1. Aadhaar system started in 2010 - MINIMUM enrollment year is 2010
2. If person was born before 2010, enrollment could be 2010-{self.current_year}
3. If person was born in/after 2010, enrollment is birth year
4. PAN typically issued at age 18+ when person starts working
5. Email age based on provider (Gmail 2004, Outlook 2012)
6. Phone based on Indian carrier (Jio 2016, others earlier)

Return JSON only:
{{
  "aadhaar_years": <int between 0 and {self.current_year - 2010}>,
  "pan_years": <int>,
  "email_years": <int>,
  "phone_years": <int>
}}

EXAMPLE for DOB 1995-01-01:
- Person is {self.current_year - 1995} years old
- Aadhaar enrollment likely 2010-2012, so aadhaar_years = 12-14
- PAN issued around 2013 (age 18), so pan_years = {self.current_year - 2013}

EXAMPLE for DOB 2015-01-01:
- Person is {self.current_year - 2015} years old
- Aadhaar enrollment at birth (2015), so aadhaar_years = {self.current_year - 2015}
- No PAN yet, so pan_years = 0"""
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                
                payload = {
                    "model": self.model,
                    "temperature": 0.1,
                    "max_tokens": 500,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a document age estimation specialist. ALWAYS enforce: Aadhaar minimum year is 2010. Return ONLY valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
                
                async with session.post(
                    self.endpoint,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        text = data["choices"][0]["message"]["content"]
                        
                        start = text.find('{')
                        end = text.rfind('}')
                        if start != -1 and end != -1:
                            result = json.loads(text[start:end + 1])
                            
                            # SAFETY CHECK: Enforce Aadhaar minimum
                            max_aadhaar_years = self.current_year - 2010
                            if result.get('aadhaar_years', 0) > max_aadhaar_years:
                                result['aadhaar_years'] = max_aadhaar_years
                            
                            if result.get('aadhaar_years', 0) < 0:
                                result['aadhaar_years'] = 0
                            
                            return result
            
            return self._fallback_age_estimation(identity)
            
        except Exception as e:
            print(f"⚠️ Age estimation error: {e}")
            return self._fallback_age_estimation(identity)
    
    def _fallback_age_estimation(self, identity: Dict) -> Dict[str, int]:
        """
        Fallback age estimation without API.
        
        FIXED: Now correctly enforces Aadhaar 2010 minimum
        """
        ages = {
            "aadhaar_years": 0,
            "pan_years": 0,
            "email_years": 0,
            "phone_years": 0,
        }
        
        # Try to calculate from DOB
        dob = identity.get('dob', '')
        if dob:
            try:
                # Parse DOB (format: YYYY-MM-DD or YYYY/MM/DD)
                if '-' in dob:
                    birth_year = int(dob.split('-')[0])
                elif '/' in dob:
                    birth_year = int(dob.split('/')[0])
                else:
                    birth_year = int(dob[:4])
                
                person_age = self.current_year - birth_year
                
                # FIXED: Aadhaar logic with 2010 minimum
                if birth_year >= 2010:
                    # Person born in/after 2010: enrolled at birth
                    ages["aadhaar_years"] = self.current_year - birth_year
                else:
                    # Person born before 2010: enrolled when system launched
                    # Conservative estimate: assume enrollment in 2011
                    estimated_enrollment = 2011
                    ages["aadhaar_years"] = max(0, self.current_year - estimated_enrollment)
                
                # Ensure max is (current_year - 2010)
                max_aadhaar_years = self.current_year - 2010
                ages["aadhaar_years"] = min(ages["aadhaar_years"], max_aadhaar_years)
                
                # PAN: typically at 18
                if person_age >= 18:
                    ages["pan_years"] = min(person_age - 18, person_age)
                
            except Exception as e:
                print(f"⚠️ DOB parsing error: {e}")
                # Default estimates if parsing fails
                ages["aadhaar_years"] = 10
                ages["pan_years"] = 5
        else:
            # No DOB provided, use conservative defaults
            ages["aadhaar_years"] = 10
            ages["pan_years"] = 5
        
        # Email: conservative estimate
        ages["email_years"] = 5
        
        # Phone: conservative estimate
        ages["phone_years"] = 5
        
        return ages