"""
Unified Identity Verification System - API Integrations
========================================================

Real API integrations for identity verification:
- Tavily / SerpAPI: Web search for OSINT
- HaveIBeenPwned: Email breach detection
- Numverify: Phone validation
- India Post: PIN code verification
- AbstractAPI: Email validation (optional)
"""

import asyncio
import os
import re
import ssl
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Load environment variables before reading them
from dotenv import load_dotenv
load_dotenv()  # .env in current directory
load_dotenv("../../.env")  # Parent Layer 2 folder
load_dotenv("../../env.example")  # Fallback

import aiohttp


# =============================================================================
# CONFIGURATION
# =============================================================================

class APIConfig:
    """API configuration and keys."""
    
    # Search APIs
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY') or os.getenv('SEARCH_API_KEY', '')
    SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY', '')
    SEARCH_PROVIDER = os.getenv('SEARCH_PROVIDER', 'tavily').lower()
    
    # Validation APIs
    NUMVERIFY_API_KEY = os.getenv('NUMVERIFY_API_KEY', '')
    ABSTRACT_API_KEY = os.getenv('ABSTRACT_API_KEY', '')
    
    # Claude AI
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "llama3-70b-8192"  # or mixtral-8x7b-32768

    # Endpoints
    TAVILY_ENDPOINT = os.getenv('TAVILY_ENDPOINT', 'https://api.tavily.com/search')
    SERPAPI_ENDPOINT = os.getenv('SERPAPI_ENDPOINT', 'https://serpapi.com/search')
    HIBP_ENDPOINT = 'https://haveibeenpwned.com/api/v3/breachedaccount'
    NUMVERIFY_ENDPOINT = 'http://apilayer.net/api/validate'
    INDIAPOST_ENDPOINT = 'https://api.postalpincode.in/pincode'
    
    @classmethod
    def get_status(cls) -> Dict[str, bool]:
        """Get API availability status."""
        return {
            'tavily': bool(cls.TAVILY_API_KEY),
            'serpapi': bool(cls.SERPAPI_API_KEY),
            'numverify': bool(cls.NUMVERIFY_API_KEY),
            'claude': bool(cls.ANTHROPIC_API_KEY),
            'hibp': True,  # No key needed
            'indiapost': True,  # No key needed
        }


# =============================================================================
# HIGH-TRUST AND KNOWN DOMAINS
# =============================================================================

HIGH_TRUST_DOMAINS = {
    # Professional
    "linkedin.com", "xing.com", "glassdoor.com", "indeed.com",
    "angel.co", "crunchbase.com", "wellfound.com",
    # Developer
    "github.com", "gitlab.com", "bitbucket.org", "stackoverflow.com",
    "dev.to", "hashnode.com", "kaggle.com", "huggingface.co",
    # Social
    "twitter.com", "x.com", "facebook.com", "instagram.com",
    "reddit.com", "quora.com", "youtube.com",
    # Academic
    "researchgate.net", "academia.edu", "orcid.org",
    # Content
    "medium.com", "substack.com", "wordpress.com",
}

NEWS_DOMAINS = {
    "nytimes.com", "bbc.com", "reuters.com", "bloomberg.com",
    "forbes.com", "techcrunch.com", "wired.com", "theverge.com",
}

DISPOSABLE_EMAIL_DOMAINS = {
    "tempmail.com", "guerrillamail.com", "10minutemail.com", "mailinator.com",
    "throwaway.email", "fakeinbox.com", "trashmail.com", "getnada.com",
    "temp-mail.org", "dispostable.com", "maildrop.cc", "yopmail.com",
    "mohmal.com", "sharklasers.com", "spamgourmet.com", "tmpmail.org",
}

EDUCATIONAL_DOMAINS = {".edu", ".edu.in", ".ac.in", ".ac.uk", ".edu.au"}

INDIAN_CARRIERS = {
    "jio": {"name": "Reliance Jio", "launch": 2016},
    "airtel": {"name": "Bharti Airtel", "launch": 1995},
    "vodafone": {"name": "Vodafone Idea", "launch": 2018},
    "vi": {"name": "Vodafone Idea", "launch": 2018},
    "bsnl": {"name": "BSNL", "launch": 2000},
    "mtnl": {"name": "MTNL", "launch": 1986},
}


# =============================================================================
# WEB SEARCH APIs
# =============================================================================

class WebSearchAPI:
    """
    Unified web search client supporting Tavily and SerpAPI.
    """
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.request_count = 0
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        provider: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a web search query.
        
        Returns:
            List of search results with title, url, snippet, published
        """
        provider = provider or APIConfig.SEARCH_PROVIDER
        
        if provider == 'tavily' and APIConfig.TAVILY_API_KEY:
            return await self._search_tavily(query, max_results)
        elif provider == 'serpapi' and APIConfig.SERPAPI_API_KEY:
            return await self._search_serpapi(query, max_results)
        else:
            print(f"⚠️ No search API configured for provider: {provider}")
            return []
    
    async def _search_tavily(self, query: str, max_results: int) -> List[Dict]:
        """Tavily API search."""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "api_key": APIConfig.TAVILY_API_KEY,
                    "query": query,
                    "max_results": max_results,
                    "include_answer": False,
                    "search_depth": "advanced",
                }
                
                async with session.post(
                    APIConfig.TAVILY_ENDPOINT,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.request_count += 1
                        
                        results = []
                        for item in data.get("results", []):
                            results.append({
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "snippet": item.get("content") or item.get("snippet", ""),
                                "published": item.get("published_date"),
                                "domain": urlparse(item.get("url", "")).netloc.lower(),
                            })
                        
                        print(f"✅ Tavily: {len(results)} results for '{query[:40]}...'")
                        return results
                    else:
                        print(f"❌ Tavily error: {response.status}")
                        return []
        except Exception as e:
            print(f"❌ Tavily exception: {e}")
            return []
    
    async def _search_serpapi(self, query: str, max_results: int) -> List[Dict]:
        """SerpAPI search."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "engine": "google",
                    "q": query,
                    "api_key": APIConfig.SERPAPI_API_KEY,
                    "num": max_results,
                }
                
                async with session.get(
                    APIConfig.SERPAPI_ENDPOINT,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.request_count += 1
                        
                        results = []
                        for item in data.get("organic_results", [])[:max_results]:
                            results.append({
                                "title": item.get("title", ""),
                                "url": item.get("link", ""),
                                "snippet": item.get("snippet", ""),
                                "published": item.get("date"),
                                "domain": urlparse(item.get("link", "")).netloc.lower(),
                            })
                        
                        print(f"✅ SerpAPI: {len(results)} results")
                        return results
                    else:
                        print(f"❌ SerpAPI error: {response.status}")
                        return []
        except Exception as e:
            print(f"❌ SerpAPI exception: {e}")
            return []
    
    async def search_batch(
        self,
        queries: List[str],
        max_results: int = 10,
        max_concurrent: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple searches concurrently.
        Returns combined, deduplicated results.
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def bounded_search(query: str):
            async with semaphore:
                return await self.search(query, max_results)
        
        tasks = [bounded_search(q) for q in queries]
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine and deduplicate
        all_results = []
        seen_urls = set()
        
        for results in results_lists:
            if isinstance(results, list):
                for r in results:
                    if r.get('url') and r['url'] not in seen_urls:
                        seen_urls.add(r['url'])
                        all_results.append(r)
        
        return all_results


# =============================================================================
# HAVEIBEENPWNED API
# =============================================================================

class HaveIBeenPwnedAPI:
    """
    HaveIBeenPwned API for email breach detection.
    Note: Rate limited, no API key required for basic check.
    """
    
    @staticmethod
    async def check_breaches(email: str) -> Dict[str, Any]:
        """
        Check if email appears in known data breaches.
        
        Returns:
            {
                "breached": bool,
                "breach_count": int,
                "breaches": list of breach names,
                "breach_details": list of {name, year, data_classes},
                "oldest_breach_year": int or None
            }
        """
        try:
            # Create SSL context that doesn't verify (for compatibility)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                headers = {
                    'User-Agent': 'UnifiedIdentityVerification/1.0',
                    'Accept': 'application/json',
                }
                
                url = f"{APIConfig.HIBP_ENDPOINT}/{email}"
                
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        breaches = await response.json()
                        breach_names = [b.get('Name', 'Unknown') for b in breaches]
                        
                        # Extract detailed breach info with REAL dates
                        breach_details = []
                        oldest = None
                        
                        for breach in breaches:
                            date = breach.get('BreachDate', '')
                            year = None
                            if date:
                                try:
                                    year = int(date[:4])
                                    if oldest is None or year < oldest:
                                        oldest = year
                                except:
                                    pass
                            
                            breach_details.append({
                                'name': breach.get('Name', 'Unknown'),
                                'year': year,
                                'data_classes': breach.get('DataClasses', [])[:5],
                                'is_verified': breach.get('IsVerified', False),
                            })
                        
                        # Sort by year (oldest first)
                        breach_details.sort(key=lambda x: x['year'] or 9999)
                        
                        print(f"✅ HIBP: {len(breaches)} breaches for {email} (oldest: {oldest})")
                        
                        return {
                            "breached": True,
                            "breach_count": len(breaches),
                            "breaches": breach_names[:10],
                            "breach_details": breach_details[:10],
                            "oldest_breach_year": oldest,
                        }
                    
                    elif response.status == 404:
                        print(f"✅ HIBP: No breaches for {email}")
                        return {
                            "breached": False,
                            "breach_count": 0,
                            "breaches": [],
                            "breach_details": [],
                            "oldest_breach_year": None,
                        }
                    
                    else:
                        print(f"⚠️ HIBP: Status {response.status}")
                        return {
                            "breached": None,
                            "breach_count": 0,
                            "breaches": [],
                            "breach_details": [],
                            "oldest_breach_year": None,
                        }
                        
        except Exception as e:
            print(f"⚠️ HIBP exception: {e}")
            return {
                "breached": None,
                "breach_count": 0,
                "breaches": [],
                "breach_details": [],
                "oldest_breach_year": None,
            }


# =============================================================================
# NUMVERIFY API
# =============================================================================

class NumverifyAPI:
    """
    Numverify API for phone number validation.
    Provides carrier detection and location.
    """
    
    @staticmethod
    async def validate_phone(
        phone: str,
        country_code: str = "IN"
    ) -> Dict[str, Any]:
        """
        Validate phone number and get carrier info.
        
        Returns:
            {
                "valid": bool,
                "carrier": str,
                "line_type": str,
                "location": str,
                "country": str
            }
        """
        if not APIConfig.NUMVERIFY_API_KEY:
            # Fallback: Pattern-based validation for Indian numbers
            return NumverifyAPI._fallback_validation(phone)
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'access_key': APIConfig.NUMVERIFY_API_KEY,
                    'number': phone,
                    'country_code': country_code,
                }
                
                async with session.get(
                    APIConfig.NUMVERIFY_ENDPOINT,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('valid'):
                            carrier = data.get('carrier', 'Unknown')
                            
                            # Estimate registration age based on carrier
                            age_years = 5.0  # Default
                            carrier_lower = carrier.lower()
                            for key, info in INDIAN_CARRIERS.items():
                                if key in carrier_lower:
                                    launch_year = info['launch']
                                    age_years = datetime.now().year - launch_year
                                    break
                            
                            print(f"✅ Numverify: Valid - {carrier}")
                            
                            return {
                                "valid": True,
                                "carrier": carrier,
                                "line_type": data.get('line_type', 'mobile'),
                                "location": data.get('location', ''),
                                "country": data.get('country_name', 'India'),
                                "registration_age_years": min(age_years, 15),
                            }
                        else:
                            print(f"⚠️ Numverify: Invalid number")
                            return {
                                "valid": False,
                                "carrier": "Invalid",
                                "line_type": "unknown",
                                "location": None,
                                "country": None,
                                "registration_age_years": 0,
                            }
                    else:
                        return NumverifyAPI._fallback_validation(phone)
                        
        except Exception as e:
            print(f"⚠️ Numverify exception: {e}")
            return NumverifyAPI._fallback_validation(phone)
    
    @staticmethod
    def _fallback_validation(phone: str) -> Dict[str, Any]:
        """Fallback pattern-based validation for Indian numbers."""
        clean = re.sub(r'\D', '', phone)
        
        # Indian mobile: 10 digits starting with 6-9
        if len(clean) == 10 and clean[0] in '6789':
            # Guess carrier from prefix (simplified)
            prefix = clean[:4]
            carrier = "Unknown Carrier"
            
            if prefix.startswith(('70', '71', '72', '73', '74', '75', '76')):
                carrier = "Possible Jio/BSNL"
            elif prefix.startswith(('98', '99', '97', '96')):
                carrier = "Possible Airtel"
            elif prefix.startswith(('91', '92', '93', '94', '95')):
                carrier = "Possible Vodafone/Idea"
            
            return {
                "valid": True,
                "carrier": carrier,
                "line_type": "mobile",
                "location": "India",
                "country": "India",
                "registration_age_years": 5.0,
            }
        
        return {
            "valid": False,
            "carrier": "Invalid",
            "line_type": "unknown",
            "location": None,
            "country": None,
            "registration_age_years": 0,
        }


# =============================================================================
# INDIA POST API
# =============================================================================

class IndiaPostAPI:
    """
    India Post API for PIN code validation.
    Free public API, no key required.
    """
    
    @staticmethod
    async def validate_pincode(pincode: str) -> Dict[str, Any]:
        """
        Validate Indian PIN code and get location details.
        
        Returns:
            {
                "valid": bool,
                "city": str,
                "state": str,
                "district": str,
                "post_offices": list
            }
        """
        if not pincode or not re.match(r'^\d{6}$', pincode):
            return {
                "valid": False,
                "city": None,
                "state": None,
                "district": None,
                "post_offices": [],
            }
        
        try:
            # SSL context for compatibility
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                url = f"{APIConfig.INDIAPOST_ENDPOINT}/{pincode}"
                
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data and data[0].get('Status') == 'Success':
                            post_offices = data[0].get('PostOffice', [])
                            
                            if post_offices:
                                po = post_offices[0]
                                
                                print(f"✅ India Post: {po['District']}, {po['State']}")
                                
                                return {
                                    "valid": True,
                                    "city": po.get('Block') or po.get('Name'),
                                    "state": po.get('State'),
                                    "district": po.get('District'),
                                    "post_offices": [p.get('Name') for p in post_offices[:5]],
                                }
                        
                        print(f"⚠️ India Post: Invalid PIN {pincode}")
                        return {
                            "valid": False,
                            "city": None,
                            "state": None,
                            "district": None,
                            "post_offices": [],
                        }
                    else:
                        return {
                            "valid": None,
                            "city": None,
                            "state": None,
                            "district": None,
                            "post_offices": [],
                        }
                        
        except Exception as e:
            print(f"⚠️ India Post exception: {e}")
            return {
                "valid": None,
                "city": None,
                "state": None,
                "district": None,
                "post_offices": [],
            }


# =============================================================================
# EMAIL ANALYSIS UTILITIES
# =============================================================================

class EmailAnalyzer:
    """
    Analyze email address patterns and domain reputation.
    """
    
    @staticmethod
    def analyze(email: str) -> Dict[str, Any]:
        """
        Analyze email pattern without external API.
        
        Returns:
            {
                "is_valid": bool,
                "is_disposable": bool,
                "is_educational": bool,
                "is_corporate": bool,
                "domain": str,
                "local_part": str,
                "pattern": str,  # name_based, random, student_id, etc.
            }
        """
        if not email or '@' not in email:
            return {
                "is_valid": False,
                "is_disposable": False,
                "is_educational": False,
                "is_corporate": False,
                "domain": "",
                "local_part": "",
                "pattern": "invalid",
            }
        
        local_part, domain = email.lower().split('@', 1)
        
        # Check disposable
        is_disposable = domain in DISPOSABLE_EMAIL_DOMAINS
        
        # Check educational
        is_educational = any(edu in domain for edu in EDUCATIONAL_DOMAINS)
        
        # Check corporate (not free provider and not educational)
        free_providers = {'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
                        'aol.com', 'icloud.com', 'protonmail.com', 'mail.com'}
        is_corporate = domain not in free_providers and not is_educational
        
        # Detect pattern
        pattern = "unknown"
        if re.match(r'^\d{6,12}$', local_part):
            pattern = "student_id"
        elif re.match(r'^[a-z]+[\._][a-z]+$', local_part):
            pattern = "name_based"
        elif re.match(r'^[a-z0-9]{10,}$', local_part) and not re.search(r'[aeiou]{2,}', local_part):
            pattern = "random"
        elif re.match(r'^[a-z]+\d*$', local_part):
            pattern = "simple"
        else:
            pattern = "mixed"
        
        return {
            "is_valid": True,
            "is_disposable": is_disposable,
            "is_educational": is_educational,
            "is_corporate": is_corporate,
            "domain": domain,
            "local_part": local_part,
            "pattern": pattern,
        }


# =============================================================================
# DOMAIN TRUST ANALYZER
# =============================================================================

class DomainTrustAnalyzer:
    """
    Analyze domain trustworthiness.
    """
    
    @staticmethod
    def get_trust_level(domain: str) -> str:
        """
        Get trust level for a domain.
        
        Returns: "critical", "high", "medium", "low", "suspicious"
        """
        domain_lower = domain.lower()
        
        # Government/Educational - Critical trust
        if any(domain_lower.endswith(g) for g in ['.gov', '.gov.in', '.gov.uk', '.mil', '.edu']):
            return "critical"
        
        # High trust established platforms
        if any(ht in domain_lower for ht in HIGH_TRUST_DOMAINS):
            return "high"
        
        # News domains
        if any(nd in domain_lower for nd in NEWS_DOMAINS):
            return "high"
        
        # Educational
        if any(edu in domain_lower for edu in EDUCATIONAL_DOMAINS):
            return "high"
        
        return "medium"
    
    @staticmethod
    def classify_domains(domains: List[str]) -> Dict[str, List[str]]:
        """
        Classify a list of domains by trust level.
        """
        classified = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "suspicious": [],
        }
        
        for domain in domains:
            level = DomainTrustAnalyzer.get_trust_level(domain)
            classified[level].append(domain)
        
        return classified

