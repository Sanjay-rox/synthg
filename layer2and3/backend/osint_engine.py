"""
Unified Identity Verification System - OSINT Engine
====================================================

Advanced Google Dorking and OSINT capabilities for comprehensive
digital footprint analysis. Generates 50+ search patterns.
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

from models import DorkCategory, SearchHit


# =============================================================================
# PLATFORM DEFINITIONS
# =============================================================================

SOCIAL_PLATFORMS = {
    "professional": [
        "linkedin.com", "xing.com", "glassdoor.com", "indeed.com",
        "angel.co", "crunchbase.com", "f6s.com", "wellfound.com",
    ],
    "developer": [
        "github.com", "gitlab.com", "bitbucket.org", "stackoverflow.com",
        "dev.to", "hashnode.com", "codepen.io", "replit.com",
        "kaggle.com", "huggingface.co", "leetcode.com", "hackerrank.com",
    ],
    "social": [
        "twitter.com", "x.com", "facebook.com", "instagram.com",
        "threads.net", "mastodon.social", "bsky.app", "tiktok.com",
        "reddit.com", "quora.com",
    ],
    "content": [
        "medium.com", "substack.com", "wordpress.com", "blogger.com",
        "youtube.com", "vimeo.com", "twitch.tv",
    ],
    "academic": [
        "researchgate.net", "academia.edu", "orcid.org", "scholar.google.com",
        "semanticscholar.org", "arxiv.org",
    ],
}

BREACH_INDICATOR_DOMAINS = {
    "pastebin.com", "ghostbin.com", "paste.ee", "dpaste.org",
    "hastebin.com", "justpaste.it",
}


# =============================================================================
# DORK QUERY DATA CLASS
# =============================================================================

@dataclass
class DorkQuery:
    """Represents a Google Dork search query."""
    query: str
    category: DorkCategory
    priority: int  # 1-10
    description: str
    expected_signal: str


# =============================================================================
# GOOGLE DORK GENERATOR
# =============================================================================

class GoogleDorkGenerator:
    """
    Advanced Google Dork query generator.
    Generates 50+ search patterns for comprehensive OSINT.
    """
    
    def __init__(self, aggressive: bool = True):
        """
        Initialize the dork generator.
        
        Args:
            aggressive: Include breach detection queries
        """
        self.aggressive = aggressive
    
    def generate_all_dorks(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        username: Optional[str] = None,
        company: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[DorkQuery]:
        """
        Generate comprehensive dork queries for all identifiers.
        Returns prioritized list of 50+ queries.
        """
        dorks: List[DorkQuery] = []
        
        # Extract components
        email_local = email.split("@")[0] if email and "@" in email else None
        email_domain = email.split("@")[1] if email and "@" in email else None
        phone_clean = re.sub(r"[^\d]", "", phone) if phone else None
        phone_last10 = phone_clean[-10:] if phone_clean and len(phone_clean) >= 10 else phone_clean
        
        # Infer username from email
        inferred_username = username or email_local
        
        # 1. IDENTITY CORE (Highest Priority)
        dorks.extend(self._identity_core_dorks(name, email, phone, phone_last10))
        
        # 2. SOCIAL MEDIA DEEP SCAN
        dorks.extend(self._social_media_dorks(name, email, inferred_username))
        
        # 3. PROFESSIONAL VERIFICATION
        dorks.extend(self._professional_dorks(name, email, company))
        
        # 4. ACADEMIC & RESEARCH
        dorks.extend(self._academic_dorks(name, email))
        
        # 5. DATA LEAK DETECTION (if aggressive)
        if self.aggressive:
            dorks.extend(self._data_leak_dorks(email, phone, inferred_username))
        
        # 6. DOCUMENT DISCOVERY
        dorks.extend(self._document_dorks(name, email))
        
        # 7. HISTORICAL/ARCHIVE
        dorks.extend(self._historical_dorks(name, email))
        
        # 8. BEHAVIORAL PATTERNS
        dorks.extend(self._behavioral_dorks(name, inferred_username))
        
        # 9. GEOLOCATION (if location provided)
        if location:
            dorks.extend(self._geolocation_dorks(name, location))
        
        # 10. CROSS-REFERENCE
        dorks.extend(self._cross_reference_dorks(name, email, phone, inferred_username))
        
        # Sort by priority (highest first)
        dorks.sort(key=lambda d: d.priority, reverse=True)
        
        return dorks
    
    def _identity_core_dorks(
        self,
        name: Optional[str],
        email: Optional[str],
        phone: Optional[str],
        phone_last10: Optional[str],
    ) -> List[DorkQuery]:
        """Core identity verification - highest priority."""
        dorks = []
        
        if email:
            # Exact email match
            dorks.append(DorkQuery(
                query=f'"{email}"',
                category=DorkCategory.IDENTITY_CORE,
                priority=10,
                description="Exact email match across all pages",
                expected_signal="email_presence"
            ))
            
            # Email in URL
            dorks.append(DorkQuery(
                query=f'inurl:"{email}"',
                category=DorkCategory.IDENTITY_CORE,
                priority=8,
                description="Email in URLs (signups, profiles)",
                expected_signal="email_in_urls"
            ))
        
        if phone:
            dorks.append(DorkQuery(
                query=f'"{phone}"',
                category=DorkCategory.IDENTITY_CORE,
                priority=9,
                description="Exact phone number match",
                expected_signal="phone_presence"
            ))
            
            if phone_last10 and phone_last10 != phone:
                dorks.append(DorkQuery(
                    query=f'"{phone_last10}"',
                    category=DorkCategory.IDENTITY_CORE,
                    priority=8,
                    description="Phone without country code",
                    expected_signal="phone_variations"
                ))
        
        if name:
            dorks.append(DorkQuery(
                query=f'"{name}"',
                category=DorkCategory.IDENTITY_CORE,
                priority=6,
                description="Exact name match",
                expected_signal="name_presence"
            ))
            
            dorks.append(DorkQuery(
                query=f'intitle:"{name}"',
                category=DorkCategory.IDENTITY_CORE,
                priority=7,
                description="Name in page titles",
                expected_signal="name_prominence"
            ))
        
        # Cross-correlations (very strong)
        if name and email:
            dorks.append(DorkQuery(
                query=f'"{name}" "{email}"',
                category=DorkCategory.IDENTITY_CORE,
                priority=10,
                description="Name and email together",
                expected_signal="identity_correlation"
            ))
        
        if name and phone:
            dorks.append(DorkQuery(
                query=f'"{name}" "{phone}"',
                category=DorkCategory.IDENTITY_CORE,
                priority=10,
                description="Name and phone together",
                expected_signal="identity_correlation"
            ))
        
        if email and phone:
            dorks.append(DorkQuery(
                query=f'"{email}" "{phone}"',
                category=DorkCategory.IDENTITY_CORE,
                priority=10,
                description="Email and phone together",
                expected_signal="identity_correlation"
            ))
        
        return dorks
    
    def _social_media_dorks(
        self,
        name: Optional[str],
        email: Optional[str],
        username: Optional[str],
    ) -> List[DorkQuery]:
        """Social media platform searches."""
        dorks = []
        
        # Professional platforms
        for platform in SOCIAL_PLATFORMS["professional"]:
            if name:
                dorks.append(DorkQuery(
                    query=f'site:{platform} "{name}"',
                    category=DorkCategory.SOCIAL_MEDIA,
                    priority=9 if "linkedin" in platform else 7,
                    description=f"Profile on {platform}",
                    expected_signal="professional_profile"
                ))
        
        # Developer platforms
        for platform in SOCIAL_PLATFORMS["developer"]:
            if username:
                dorks.append(DorkQuery(
                    query=f'site:{platform} "{username}"',
                    category=DorkCategory.SOCIAL_MEDIA,
                    priority=8 if platform in ["github.com", "stackoverflow.com"] else 6,
                    description=f"Developer profile on {platform}",
                    expected_signal="developer_profile"
                ))
        
        # Social platforms
        for platform in SOCIAL_PLATFORMS["social"]:
            if name:
                dorks.append(DorkQuery(
                    query=f'site:{platform} "{name}"',
                    category=DorkCategory.SOCIAL_MEDIA,
                    priority=6,
                    description=f"Social presence on {platform}",
                    expected_signal="social_profile"
                ))
        
        # Content platforms
        for platform in SOCIAL_PLATFORMS["content"]:
            if name:
                dorks.append(DorkQuery(
                    query=f'site:{platform} "{name}"',
                    category=DorkCategory.SOCIAL_MEDIA,
                    priority=6,
                    description=f"Content on {platform}",
                    expected_signal="content_creation"
                ))
        
        return dorks
    
    def _professional_dorks(
        self,
        name: Optional[str],
        email: Optional[str],
        company: Optional[str],
    ) -> List[DorkQuery]:
        """Professional/business verification."""
        dorks = []
        
        if name:
            # Press releases
            dorks.append(DorkQuery(
                query=f'"{name}" (press release OR announcement OR appointed OR hired)',
                category=DorkCategory.PROFESSIONAL,
                priority=8,
                description="Professional announcements",
                expected_signal="professional_mentions"
            ))
            
            # Conference speakers
            dorks.append(DorkQuery(
                query=f'"{name}" (speaker OR presenter OR keynote OR panelist)',
                category=DorkCategory.PROFESSIONAL,
                priority=7,
                description="Conference engagements",
                expected_signal="professional_reputation"
            ))
            
            # Patents
            dorks.append(DorkQuery(
                query=f'"{name}" (patent OR inventor OR author)',
                category=DorkCategory.PROFESSIONAL,
                priority=7,
                description="Patents and publications",
                expected_signal="intellectual_property"
            ))
        
        if name and company:
            dorks.append(DorkQuery(
                query=f'"{name}" "{company}"',
                category=DorkCategory.PROFESSIONAL,
                priority=9,
                description="Name with company",
                expected_signal="employment_verification"
            ))
        
        return dorks
    
    def _academic_dorks(
        self,
        name: Optional[str],
        email: Optional[str],
    ) -> List[DorkQuery]:
        """Academic and research searches."""
        dorks = []
        
        if name:
            for platform in SOCIAL_PLATFORMS["academic"]:
                dorks.append(DorkQuery(
                    query=f'site:{platform} "{name}"',
                    category=DorkCategory.ACADEMIC,
                    priority=7,
                    description=f"Academic profile on {platform}",
                    expected_signal="academic_presence"
                ))
            
            dorks.append(DorkQuery(
                query=f'"{name}" (published OR journal OR research OR thesis)',
                category=DorkCategory.ACADEMIC,
                priority=7,
                description="Academic publications",
                expected_signal="academic_publications"
            ))
            
            dorks.append(DorkQuery(
                query=f'"{name}" site:*.edu',
                category=DorkCategory.ACADEMIC,
                priority=8,
                description="University site presence",
                expected_signal="educational_affiliation"
            ))
        
        return dorks
    
    def _data_leak_dorks(
        self,
        email: Optional[str],
        phone: Optional[str],
        username: Optional[str],
    ) -> List[DorkQuery]:
        """Data leak and breach detection."""
        dorks = []
        
        paste_sites = " OR ".join([f"site:{s}" for s in list(BREACH_INDICATOR_DOMAINS)[:4]])
        
        if email:
            dorks.append(DorkQuery(
                query=f'"{email}" ({paste_sites})',
                category=DorkCategory.DATA_LEAKS,
                priority=9,
                description="Email in paste/leak sites",
                expected_signal="data_breach_exposure"
            ))
            
            dorks.append(DorkQuery(
                query=f'"{email}" (leak OR breach OR dump OR combo)',
                category=DorkCategory.DATA_LEAKS,
                priority=8,
                description="Email in breach discussions",
                expected_signal="breach_mention"
            ))
        
        if username:
            dorks.append(DorkQuery(
                query=f'"{username}" (leak OR breach OR dump OR hacked)',
                category=DorkCategory.DATA_LEAKS,
                priority=7,
                description="Username in breach contexts",
                expected_signal="breach_mention"
            ))
        
        return dorks
    
    def _document_dorks(
        self,
        name: Optional[str],
        email: Optional[str],
    ) -> List[DorkQuery]:
        """Document discovery."""
        dorks = []
        
        if name:
            dorks.append(DorkQuery(
                query=f'"{name}" filetype:pdf',
                category=DorkCategory.DOCUMENTS,
                priority=7,
                description="Name in PDFs",
                expected_signal="document_presence"
            ))
            
            dorks.append(DorkQuery(
                query=f'"{name}" (filetype:doc OR filetype:docx OR filetype:ppt)',
                category=DorkCategory.DOCUMENTS,
                priority=6,
                description="Name in Office documents",
                expected_signal="document_presence"
            ))
        
        if email:
            dorks.append(DorkQuery(
                query=f'"{email}" filetype:pdf',
                category=DorkCategory.DOCUMENTS,
                priority=7,
                description="Email in PDFs",
                expected_signal="email_in_documents"
            ))
        
        return dorks
    
    def _historical_dorks(
        self,
        name: Optional[str],
        email: Optional[str],
    ) -> List[DorkQuery]:
        """Historical and archive searches."""
        dorks = []
        
        if name:
            dorks.append(DorkQuery(
                query=f'site:web.archive.org "{name}"',
                category=DorkCategory.HISTORICAL,
                priority=8,
                description="Historical archives",
                expected_signal="historical_presence"
            ))
            
            # Date-restricted (5+ years ago)
            dorks.append(DorkQuery(
                query=f'"{name}" before:2020',
                category=DorkCategory.HISTORICAL,
                priority=9,
                description="Mentions 5+ years ago",
                expected_signal="historical_depth"
            ))
            
            # 10+ years ago
            dorks.append(DorkQuery(
                query=f'"{name}" before:2015',
                category=DorkCategory.HISTORICAL,
                priority=9,
                description="Mentions 10+ years ago",
                expected_signal="deep_history"
            ))
        
        if email:
            dorks.append(DorkQuery(
                query=f'"{email}" before:2020',
                category=DorkCategory.HISTORICAL,
                priority=9,
                description="Email mentions 5+ years ago",
                expected_signal="email_history"
            ))
        
        return dorks
    
    def _behavioral_dorks(
        self,
        name: Optional[str],
        username: Optional[str],
    ) -> List[DorkQuery]:
        """Behavioral pattern detection."""
        dorks = []
        
        if username:
            dorks.append(DorkQuery(
                query=f'"{username}" (forum OR discussion OR posted OR replied)',
                category=DorkCategory.BEHAVIORAL,
                priority=6,
                description="Forum participation",
                expected_signal="forum_activity"
            ))
            
            dorks.append(DorkQuery(
                query=f'"{username}" (commit OR pull request OR contributor)',
                category=DorkCategory.BEHAVIORAL,
                priority=7,
                description="Code contributions",
                expected_signal="developer_activity"
            ))
        
        if name:
            dorks.append(DorkQuery(
                query=f'"{name}" (award OR winner OR recognized OR certified)',
                category=DorkCategory.BEHAVIORAL,
                priority=7,
                description="Awards and recognition",
                expected_signal="achievements"
            ))
        
        return dorks
    
    def _geolocation_dorks(
        self,
        name: Optional[str],
        location: str,
    ) -> List[DorkQuery]:
        """Geolocation-based searches."""
        dorks = []
        
        if name and location:
            dorks.append(DorkQuery(
                query=f'"{name}" "{location}"',
                category=DorkCategory.BEHAVIORAL,
                priority=7,
                description="Name with location",
                expected_signal="location_correlation"
            ))
            
            dorks.append(DorkQuery(
                query=f'"{name}" "{location}" (directory OR listing)',
                category=DorkCategory.BEHAVIORAL,
                priority=6,
                description="Local directory presence",
                expected_signal="local_presence"
            ))
        
        return dorks
    
    def _cross_reference_dorks(
        self,
        name: Optional[str],
        email: Optional[str],
        phone: Optional[str],
        username: Optional[str],
    ) -> List[DorkQuery]:
        """Cross-reference between identifiers."""
        dorks = []
        
        # All three together
        if name and email and phone:
            dorks.append(DorkQuery(
                query=f'"{name}" "{email}" "{phone}"',
                category=DorkCategory.IDENTITY_CORE,
                priority=10,
                description="All identifiers together",
                expected_signal="full_identity_match"
            ))
        
        if username and name:
            dorks.append(DorkQuery(
                query=f'"{username}" "{name}"',
                category=DorkCategory.IDENTITY_CORE,
                priority=8,
                description="Username linked to name",
                expected_signal="username_deanonymization"
            ))
        
        return dorks
    
    def get_priority_queries(
        self,
        dorks: List[DorkQuery],
        max_queries: int = 25,
        min_priority: int = 6,
    ) -> List[DorkQuery]:
        """Get highest priority queries up to limit."""
        filtered = [d for d in dorks if d.priority >= min_priority]
        
        # Deduplicate
        seen: Set[str] = set()
        unique: List[DorkQuery] = []
        for dork in filtered:
            key = dork.query.lower().strip()
            if key not in seen:
                seen.add(key)
                unique.append(dork)
        
        return unique[:max_queries]


# =============================================================================
# OSINT RESULT ANALYZER
# =============================================================================

class OSINTResultAnalyzer:
    """
    Analyze OSINT search results for identity signals.
    """
    
    HIGH_TRUST_DOMAINS = {
        "linkedin.com", "github.com", "stackoverflow.com", "medium.com",
        "twitter.com", "x.com", "facebook.com", "instagram.com",
        "researchgate.net", "academia.edu", "crunchbase.com",
    }
    
    NEWS_DOMAINS = {
        "nytimes.com", "bbc.com", "reuters.com", "forbes.com",
        "techcrunch.com", "wired.com", "bloomberg.com",
    }
    
    @classmethod
    def analyze_results(
        cls,
        hits: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze search results for identity signals.
        
        Returns:
            {
                "total_hits": int,
                "unique_domains": list,
                "high_trust_count": int,
                "news_mentions": int,
                "social_profiles": list,
                "temporal_data": dict,
                "domain_distribution": dict,
            }
        """
        domains: Set[str] = set()
        high_trust = []
        news_mentions = []
        social_profiles = []
        years_found = []
        
        for hit in hits:
            domain = hit.get('domain', '')
            if domain:
                domains.add(domain)
                
                # Check trust level
                if any(ht in domain for ht in cls.HIGH_TRUST_DOMAINS):
                    high_trust.append(domain)
                    
                    # Extract as social profile
                    for platform in SOCIAL_PLATFORMS.get("professional", []):
                        if platform in domain:
                            social_profiles.append({
                                "platform": platform.split('.')[0].title(),
                                "url": hit.get('url', ''),
                                "title": hit.get('title', ''),
                            })
                
                if any(nd in domain for nd in cls.NEWS_DOMAINS):
                    news_mentions.append(domain)
            
            # Extract year from published date
            published = hit.get('published', '')
            if published:
                year_match = re.search(r'20\d{2}', str(published))
                if year_match:
                    years_found.append(int(year_match.group()))
        
        # Calculate temporal spread
        temporal_data = {}
        if years_found:
            temporal_data = {
                "oldest_year": min(years_found),
                "newest_year": max(years_found),
                "year_span": max(years_found) - min(years_found),
                "unique_years": sorted(set(years_found)),
            }
        
        return {
            "total_hits": len(hits),
            "unique_domains": sorted(domains),
            "high_trust_count": len(set(high_trust)),
            "news_mentions": len(news_mentions),
            "social_profiles": social_profiles[:10],
            "temporal_data": temporal_data,
            "domain_distribution": {
                "high_trust": list(set(high_trust)),
                "news": list(set(news_mentions)),
            },
        }

