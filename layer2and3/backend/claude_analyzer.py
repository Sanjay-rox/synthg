"""
Unified Identity Verification System - Claude AI Analyzer
==========================================================

Comprehensive AI-powered identity analysis using Claude.
Performs holistic OSINT-style verdict generation.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

import aiohttp

from models import ClaudeVerdict, IdentityContext
from api_integrations import APIConfig, EDUCATIONAL_DOMAINS


# =============================================================================
# CLAUDE ANALYZER
# =============================================================================

class ClaudeAnalyzer:
    """
    Claude AI-powered identity analysis.
    Provides holistic verdicts on identity authenticity.
    """
    
    def __init__(self):
        self.api_key = APIConfig.GROQ_API_KEY
        self.model = APIConfig.GROQ_MODEL
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    
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
                verdict="INCONCLUSIVE",
                confidence=0,
                reasoning="Claude AI not available - API key not configured",
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
                            "content": "You are an elite identity verification analyst."
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
                            verdict="INCONCLUSIVE",
                            confidence=0,
                            reasoning=f"API error: {response.status}",
                        )
                        
        except Exception as e:
            print(f"❌ Claude exception: {e}")
            return ClaudeVerdict(
                verdict="INCONCLUSIVE",
                confidence=0,
                reasoning=f"Analysis error: {str(e)}",
            )
    
    def _build_comprehensive_prompt(
        self,
        identity: Dict,
        osint_results: Optional[List[Dict]],
        enrichment: Optional[Dict],
    ) -> str:
        """Build comprehensive analysis prompt."""
        
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
UNIFIED IDENTITY VERIFICATION ANALYSIS
═══════════════════════════════════════════════════════════════════════

You are an elite identity verification analyst. Analyze this identity to
determine if it's REAL or SYNTHETIC (fake/manufactured).

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
  - Breach count: {e.get('breach_count', 0)}
  - Breaches: {', '.join(e.get('breaches', [])[:5]) or 'None'}
  - Domain reputation: {e.get('domain_reputation', 'Unknown')}
  - Is disposable: {e.get('is_disposable', False)}
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
        if osint_results:
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

NOTE: No search results does NOT automatically mean synthetic.
Many real people have minimal online presence, especially:
- Students with institutional emails
- People in regions with less web indexing
- Privacy-conscious individuals
"""
        
        # Add context notes
        if is_student:
            prompt += """
══════════════════════════════════════════════════════════════════════
CONTEXT: STUDENT DETECTED
══════════════════════════════════════════════════════════════════════
- Students typically have LIMITED online presence - this is NORMAL
- Student ID emails (221801014@...) are legitimate formats
- Absence of LinkedIn/professional profiles is expected
- 1-4 year digital footprint is typical for college students
- Focus on POSITIVE FRAUD indicators, not absence of data
"""
        
        if is_indian:
            prompt += """
══════════════════════════════════════════════════════════════════════
CONTEXT: INDIAN IDENTITY
══════════════════════════════════════════════════════════════════════
- Aadhaar enrollment started in 2010
- PAN typically issued when person is 18+
- Indian phone carriers: Jio (2016), Airtel (1995), VI (2018), BSNL (2000)
- PIN codes are 6 digits and verifiable via India Post
"""
        
        # Output format
        prompt += """
══════════════════════════════════════════════════════════════════════
REQUIRED OUTPUT (JSON ONLY)
══════════════════════════════════════════════════════════════════════

Return ONLY valid JSON:

{
  "verdict": "REAL" | "LIKELY_REAL" | "INCONCLUSIVE" | "SUSPICIOUS" | "SYNTHETIC",
  "confidence": 0-100,
  "reasoning": "2-3 sentence explanation",
  
  "identity_correlation": {
    "name_email_linked": true/false,
    "name_phone_linked": true/false,
    "email_phone_linked": true/false,
    "documents_consistent": true/false
  },
  
  "temporal_analysis": {
    "estimated_footprint_years": <int>,
    "temporal_consistency": "consistent" | "suspicious" | "too_recent",
    "aadhaar_years": <int or 0>,
    "pan_years": <int or 0>,
    "email_years": <int or 0>,
    "phone_years": <int or 0>
  },
  
  "platform_presence": {
    "has_linkedin": true/false,
    "has_github": true/false,
    "has_social_media": true/false,
    "profile_count": <int>
  },
  
  "trust_indicators": ["list of positive signals"],
  "synthetic_indicators": ["list of red flags - ONLY if positive fraud evidence"],
  
  "format_analysis": {
    "email_legitimate": true/false,
    "phone_legitimate": true/false,
    "name_legitimate": true/false,
    "documents_legitimate": true/false
  },
  
  "context": "student" | "professional" | "general"
}

VERDICT GUIDELINES:
- REAL: Clear evidence of real person
- LIKELY_REAL: No red flags, formats look legitimate
- INCONCLUSIVE: Cannot determine
- SUSPICIOUS: Some inconsistencies found
- SYNTHETIC: Strong positive evidence of fraud

CRITICAL: "Limited data" alone is NOT synthetic!
Only mark SYNTHETIC if there is POSITIVE fraud evidence.

Return ONLY the JSON object.
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
                verdict="INCONCLUSIVE",
                confidence=30,
                reasoning="Could not parse AI response",
            )
        
        try:
            # Clean JSON
            json_str = text[start:end + 1]
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            
            data = json.loads(json_str)
            
            # Extract temporal data for enrichment
            temporal = data.get('temporal_analysis', {})
            
            return ClaudeVerdict(
                verdict=data.get('verdict', 'INCONCLUSIVE').upper(),
                confidence=data.get('confidence', 50),
                reasoning=data.get('reasoning', 'No reasoning provided'),
                trust_indicators=data.get('trust_indicators', []),
                synthetic_indicators=data.get('synthetic_indicators', []),
                context=data.get('context', 'general'),
            )
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            return ClaudeVerdict(
                verdict="INCONCLUSIVE",
                confidence=30,
                reasoning="Failed to parse AI response",
            )
    
    async def estimate_document_ages(
        self,
        identity: Dict[str, Any],
    ) -> Dict[str, int]:
        """
        Estimate ages of Indian documents based on DOB.
        
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

Rules:
- Aadhaar started 2010. Enrollment based on age at 2010 or birth if after 2010.
- PAN typically issued at age 18+ when person starts working.
- Email age based on provider (Gmail 2004, Outlook 2012) and pattern.
- Phone based on Indian carrier (Jio 2016, others earlier).

Return JSON only:
{{
  "aadhaar_years": <int>,
  "pan_years": <int>,
  "email_years": <int>,
  "phone_years": <int>
}}"""
            
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
                            "content": "You are an elite identity verification analyst."
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
                            return result
            
            return self._fallback_age_estimation(identity)
            
        except Exception as e:
            print(f"⚠️ Age estimation error: {e}")
            return self._fallback_age_estimation(identity)
    
    def _fallback_age_estimation(self, identity: Dict) -> Dict[str, int]:
        """Fallback age estimation without API."""
        from datetime import datetime
        
        current_year = datetime.now().year
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
                birth_year = int(dob[:4])
                person_age = current_year - birth_year
                
                # Aadhaar: enrolled when available (2010) or at birth
                if birth_year >= 2010:
                    ages["aadhaar_years"] = current_year - birth_year
                else:
                    ages["aadhaar_years"] = min(current_year - 2010, person_age)
                
                # PAN: typically at 18
                if person_age >= 18:
                    ages["pan_years"] = min(person_age - 18, 15)
                
            except:
                pass
        
        # Email: default estimate
        ages["email_years"] = 5
        
        # Phone: default estimate
        ages["phone_years"] = 5
        
        return ages

