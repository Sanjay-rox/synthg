"""
Unified Identity Verification System - Scoring Engine
======================================================

Multi-signal scoring algorithm combining:
- OSINT analysis (8 signals)
- Graph analysis (3 signals)
- Claude AI verdict
- Red flag penalties

Total: 12+ signals for comprehensive identity scoring.
"""

from typing import Any, Dict, List, Optional, Tuple
import networkx as nx

from models import (
    ScoreBreakdown, VerificationBucket, TrustIndicator, TrustStrength,
    RedFlag, ClaudeVerdict,
)


# =============================================================================
# SCORING WEIGHTS
# =============================================================================

class ScoringWeights:
    """Scoring weight configuration."""
    
    # OSINT Signals (65% total)
    FORMAT_LEGITIMACY = 0.10      # 10%
    TEMPORAL_ANALYSIS = 0.15     # 15%
    CROSS_REFERENCE = 0.10       # 10%
    PLATFORM_PRESENCE = 0.10     # 10%
    DOMAIN_TRUST = 0.08          # 8%
    BEHAVIORAL = 0.07            # 7%
    BREACH_HISTORY = 0.03        # 3%
    GEOGRAPHIC = 0.02            # 2%
    
    # Graph Signals (20% total)
    CONNECTION_COUNT = 0.08      # 8%
    TEMPORAL_DEPTH = 0.08        # 8%
    DIVERSITY = 0.04             # 4%
    
    # AI Verdict (15%)
    VERDICT_ADJUSTMENT = 0.15    # 15%


# =============================================================================
# UNIFIED SCORING ENGINE
# =============================================================================

class UnifiedScoringEngine:
    """
    Comprehensive scoring engine combining OSINT + Graph + AI signals.
    """
    
    def __init__(self):
        self.weights = ScoringWeights()
    
    def calculate_score(
        self,
        identity: Dict[str, Any],
        enrichment: Dict[str, Any],
        graph: Optional[nx.Graph],
        osint_data: Optional[Dict[str, Any]],
        claude_verdict: Optional[ClaudeVerdict],
        red_flags: List[RedFlag],
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive identity verification score.
        
        Returns:
            {
                "total_score": float,
                "bucket": str,
                "interpretation": str,
                "score_breakdown": ScoreBreakdown,
                "trust_indicators": List[TrustIndicator],
            }
        """
        breakdown = ScoreBreakdown()
        trust_indicators: List[TrustIndicator] = []
        
        # Determine context
        is_student = self._is_student_context(identity, enrichment)
        
        # --- OSINT SIGNALS ---
        
        # 1. Format Legitimacy (10%)
        format_score, format_trust = self._score_format_legitimacy(
            identity, enrichment
        )
        breakdown.format_legitimacy = format_score
        trust_indicators.extend(format_trust)
        
        # 2. Temporal Analysis (15%)
        temporal_score, temporal_trust = self._score_temporal_analysis(
            enrichment, osint_data
        )
        breakdown.temporal_analysis = temporal_score
        trust_indicators.extend(temporal_trust)
        
        # 3. Cross-Reference (10%)
        cross_ref_score = self._score_cross_reference(identity, osint_data)
        breakdown.cross_reference = cross_ref_score
        
        # 4. Platform Presence (10%)
        platform_score, platform_trust = self._score_platform_presence(
            osint_data, claude_verdict
        )
        breakdown.platform_presence = platform_score
        trust_indicators.extend(platform_trust)
        
        # 5. Domain Trust (8%)
        domain_score = self._score_domain_trust(osint_data)
        breakdown.domain_trust = domain_score
        
        # 6. Behavioral (7%)
        behavioral_score = self._score_behavioral(osint_data, claude_verdict)
        breakdown.behavioral = behavioral_score
        
        # 7. Breach History (3%)
        breach_score, breach_trust = self._score_breach_history(enrichment)
        breakdown.breach_history = breach_score
        trust_indicators.extend(breach_trust)
        
        # 8. Geographic (2%)
        geo_score = self._score_geographic(enrichment)
        breakdown.geographic = geo_score
        
        # --- GRAPH SIGNALS ---
        
        if graph:
            # 9. Connection Count (8%)
            conn_score = self._score_connection_count(graph)
            breakdown.connection_count = conn_score
            
            # 10. Temporal Depth (8%)
            depth_score = self._score_temporal_depth(graph)
            breakdown.temporal_depth = depth_score
            
            # 11. Diversity (4%)
            diversity_score = self._score_diversity(graph)
            breakdown.diversity = diversity_score
        
        # --- AI VERDICT (15%) ---
        verdict_adjustment = self._score_claude_verdict(claude_verdict)
        breakdown.verdict_adjustment = verdict_adjustment
        
        # --- RED FLAG PENALTIES ---
        total_penalty = sum(rf.penalty for rf in red_flags)
        breakdown.red_flag_penalty = total_penalty
        
        # --- CALCULATE FINAL SCORE ---
        
        # Weighted sum of all components
        weighted_score = (
            breakdown.format_legitimacy * self.weights.FORMAT_LEGITIMACY +
            breakdown.temporal_analysis * self.weights.TEMPORAL_ANALYSIS +
            breakdown.cross_reference * self.weights.CROSS_REFERENCE +
            breakdown.platform_presence * self.weights.PLATFORM_PRESENCE +
            breakdown.domain_trust * self.weights.DOMAIN_TRUST +
            breakdown.behavioral * self.weights.BEHAVIORAL +
            breakdown.breach_history * self.weights.BREACH_HISTORY +
            breakdown.geographic * self.weights.GEOGRAPHIC +
            breakdown.connection_count * self.weights.CONNECTION_COUNT +
            breakdown.temporal_depth * self.weights.TEMPORAL_DEPTH +
            breakdown.diversity * self.weights.DIVERSITY +
            breakdown.verdict_adjustment * self.weights.VERDICT_ADJUSTMENT
        )
        
        # Apply penalties
        final_score = max(0, min(100, weighted_score - total_penalty))
        
        # Determine bucket
        bucket = self._determine_bucket(
            final_score, claude_verdict, red_flags, is_student
        )
        
        # Get interpretation
        interpretation = self._get_interpretation(bucket, final_score)
        
        return {
            "total_score": round(final_score, 2),
            "bucket": bucket,
            "interpretation": interpretation,
            "score_breakdown": breakdown,
            "trust_indicators": trust_indicators,
        }
    
    def _is_student_context(
        self,
        identity: Dict,
        enrichment: Dict,
    ) -> bool:
        """Determine if student context applies."""
        if identity.get('context') == 'student':
            return True
        
        email = identity.get('email', '')
        if email and '@' in email:
            domain = email.split('@')[1].lower()
            educational = ['.edu', '.ac.', 'college', 'university', 'school']
            if any(edu in domain for edu in educational):
                return True
        
        return False
    
    def _score_format_legitimacy(
        self,
        identity: Dict,
        enrichment: Dict,
    ) -> Tuple[float, List[TrustIndicator]]:
        """Score format legitimacy of identifiers."""
        score = 0.0
        trust = []
        
        # Email format
        email_data = enrichment.get('email', {})
        if not email_data.get('is_disposable', False):
            score += 30
            if email_data.get('is_educational'):
                score += 15
                trust.append(TrustIndicator(
                    signal="Educational email domain",
                    strength=TrustStrength.STRONG
                ))
            elif email_data.get('is_corporate'):
                score += 10
                trust.append(TrustIndicator(
                    signal="Corporate email domain",
                    strength=TrustStrength.MEDIUM
                ))
        
        # Phone format
        phone_data = enrichment.get('phone', {})
        if phone_data.get('valid') is True:
            score += 25
            trust.append(TrustIndicator(
                signal=f"Valid phone ({phone_data.get('carrier', 'Unknown')})",
                strength=TrustStrength.MEDIUM,
                source="Numverify"
            ))
        elif phone_data.get('valid') is None:
            score += 15  # Neutral
        
        # Name format (if provided)
        if identity.get('name'):
            parts = identity['name'].split()
            if len(parts) >= 2:
                score += 15
            else:
                score += 5
        
        # Indian documents
        if enrichment.get('aadhaar', {}).get('years_active', 0) > 0:
            score += 15
            trust.append(TrustIndicator(
                signal="Aadhaar enrollment verified",
                strength=TrustStrength.STRONG
            ))
        
        return min(100, score), trust
    
    def _score_temporal_analysis(
        self,
        enrichment: Dict,
        osint_data: Optional[Dict],
    ) -> Tuple[float, List[TrustIndicator]]:
        """Score temporal footprint."""
        score = 0.0
        trust = []
        
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
        
        if ages:
            max_age = max(ages)
            
            if max_age >= 10:
                score += 60
                trust.append(TrustIndicator(
                    signal=f"{int(max_age)}+ year identity footprint",
                    strength=TrustStrength.STRONG
                ))
            elif max_age >= 7:
                score += 50
            elif max_age >= 5:
                score += 40
                trust.append(TrustIndicator(
                    signal=f"{int(max_age)} year identity footprint",
                    strength=TrustStrength.MEDIUM
                ))
            elif max_age >= 3:
                score += 30
            elif max_age >= 2:
                score += 20
            elif max_age >= 1:
                score += 10
        
        # OSINT temporal spread
        if osint_data:
            temporal = osint_data.get('temporal_data', {})
            year_span = temporal.get('year_span', 0)
            
            if year_span >= 5:
                score += 30
                trust.append(TrustIndicator(
                    signal=f"Mentions span {year_span} years",
                    strength=TrustStrength.STRONG
                ))
            elif year_span >= 3:
                score += 20
            elif year_span >= 1:
                score += 10
        
        return min(100, score), trust
    
    def _score_cross_reference(
        self,
        identity: Dict,
        osint_data: Optional[Dict],
    ) -> float:
        """Score cross-reference between identifiers."""
        score = 30.0  # Base neutral score
        
        if not osint_data:
            return score
        
        # Check if name+email found together
        total_hits = osint_data.get('total_hits', 0)
        
        if total_hits > 0:
            score += 20
        if total_hits >= 5:
            score += 20
        if total_hits >= 10:
            score += 15
        
        # High-trust domain presence
        high_trust = osint_data.get('high_trust_count', 0)
        if high_trust >= 3:
            score += 15
        elif high_trust >= 1:
            score += 10
        
        return min(100, score)
    
    def _score_platform_presence(
        self,
        osint_data: Optional[Dict],
        claude_verdict: Optional[ClaudeVerdict],
    ) -> Tuple[float, List[TrustIndicator]]:
        """Score social/professional platform presence."""
        score = 0.0
        trust = []
        
        if osint_data:
            profiles = osint_data.get('social_profiles', [])
            
            # Count by platform type
            has_linkedin = any('linkedin' in p.get('platform', '').lower() for p in profiles)
            has_github = any('github' in p.get('platform', '').lower() for p in profiles)
            
            if has_linkedin:
                score += 35
                trust.append(TrustIndicator(
                    signal="LinkedIn profile found",
                    strength=TrustStrength.STRONG,
                    source="linkedin.com"
                ))
            
            if has_github:
                score += 25
                trust.append(TrustIndicator(
                    signal="GitHub profile found",
                    strength=TrustStrength.STRONG,
                    source="github.com"
                ))
            
            # General profile count
            score += min(20, len(profiles) * 5)
        
        # News mentions
        if osint_data:
            news = osint_data.get('news_mentions', 0)
            if news > 0:
                score += 20
                trust.append(TrustIndicator(
                    signal=f"Mentioned in {news} news source(s)",
                    strength=TrustStrength.STRONG
                ))
        
        return min(100, score), trust
    
    def _score_domain_trust(self, osint_data: Optional[Dict]) -> float:
        """Score based on domain trustworthiness."""
        if not osint_data:
            return 30.0  # Neutral
        
        score = 0.0
        
        high_trust = osint_data.get('high_trust_count', 0)
        total = osint_data.get('total_hits', 0)
        unique_domains = len(osint_data.get('unique_domains', []))
        
        # High trust ratio
        if total > 0:
            trust_ratio = high_trust / total
            score += trust_ratio * 50
        
        # Domain diversity
        score += min(30, unique_domains * 3)
        
        # Bonus for critical domains
        domains = osint_data.get('unique_domains', [])
        for domain in domains:
            if any(d in domain for d in ['.gov', '.edu', '.ac.']):
                score += 10
                break
        
        return min(100, score)
    
    def _score_behavioral(
        self,
        osint_data: Optional[Dict],
        claude_verdict: Optional[ClaudeVerdict],
    ) -> float:
        """Score behavioral patterns."""
        score = 30.0  # Base neutral
        
        # From OSINT
        if osint_data:
            profiles = osint_data.get('social_profiles', [])
            if profiles:
                score += 20
            
            total_hits = osint_data.get('total_hits', 0)
            if total_hits >= 10:
                score += 20
            elif total_hits >= 5:
                score += 10
        
        # From Claude
        if claude_verdict:
            trust_ind = claude_verdict.trust_indicators
            if 'content creation' in ' '.join(trust_ind).lower():
                score += 15
            if 'engagement' in ' '.join(trust_ind).lower():
                score += 10
        
        return min(100, score)
    
    def _score_breach_history(
        self,
        enrichment: Dict,
    ) -> Tuple[float, List[TrustIndicator]]:
        """
        Score breach history.
        Paradoxically, being in breaches indicates REAL history.
        """
        score = 50.0  # Neutral
        trust = []
        
        email_data = enrichment.get('email', {})
        breach_count = email_data.get('breach_count', 0)
        
        if breach_count > 0 and breach_count <= 5:
            score += 30
            trust.append(TrustIndicator(
                signal="Appears in data breach records (indicates real history)",
                strength=TrustStrength.MEDIUM,
                source="HaveIBeenPwned"
            ))
        elif breach_count > 5:
            score += 20  # Many breaches, still indicates real person
        
        return min(100, score), trust
    
    def _score_geographic(self, enrichment: Dict) -> float:
        """Score geographic consistency."""
        score = 50.0  # Neutral
        
        address_data = enrichment.get('address', {})
        
        if address_data.get('valid') is True:
            score += 30
        
        if address_data.get('city') and address_data.get('state'):
            score += 20
        
        return min(100, score)
    
    def _score_connection_count(self, graph: nx.Graph) -> float:
        """Score based on graph connections."""
        edges = graph.number_of_edges()
        
        if edges >= 15:
            return 100
        elif edges >= 10:
            return 80
        elif edges >= 7:
            return 60
        elif edges >= 5:
            return 40
        elif edges >= 3:
            return 20
        return 10
    
    def _score_temporal_depth(self, graph: nx.Graph) -> float:
        """Score based on oldest relationship in graph."""
        oldest = 0.0
        
        for _, _, data in graph.edges(data=True):
            age = data.get('age_years', 0) or 0
            oldest = max(oldest, age)
        
        if oldest >= 10:
            return 100
        elif oldest >= 7:
            return 80
        elif oldest >= 5:
            return 60
        elif oldest >= 3:
            return 40
        elif oldest >= 1:
            return 20
        return 10
    
    def _score_diversity(self, graph: nx.Graph) -> float:
        """Score based on node type diversity."""
        types = set()
        for _, data in graph.nodes(data=True):
            types.add(data.get('type', 'Unknown'))
        
        # Max 6 types: Person, Email, Phone, Aadhaar, PAN, Address
        diversity_ratio = len(types) / 6
        return min(100, diversity_ratio * 100 + 20)  # Bonus for any diversity
    
    def _score_claude_verdict(
        self,
        claude_verdict: Optional[ClaudeVerdict],
    ) -> float:
        """Convert Claude verdict to score."""
        if not claude_verdict:
            return 50.0  # Neutral
        
        verdict = claude_verdict.verdict.upper()
        confidence = claude_verdict.confidence / 100
        
        verdict_scores = {
            "REAL": 100,
            "LIKELY_REAL": 75,
            "INCONCLUSIVE": 50,
            "SUSPICIOUS": 25,
            "SYNTHETIC": 0,
        }
        
        base = verdict_scores.get(verdict, 50)
        
        # Scale by confidence
        return base * confidence + 50 * (1 - confidence)
    
    def _determine_bucket(
        self,
        score: float,
        claude_verdict: Optional[ClaudeVerdict],
        red_flags: List[RedFlag],
        is_student: bool,
    ) -> VerificationBucket:
        """Determine final verification bucket."""
        
        # Critical red flags force synthetic
        critical_flags = [rf for rf in red_flags if rf.severity.value == "critical"]
        if critical_flags:
            # Check for disposable email specifically
            if any("DISPOSABLE" in rf.code for rf in critical_flags):
                return VerificationBucket.SYNTHETIC
        
        # High confidence Claude verdict
        if claude_verdict and claude_verdict.confidence >= 75:
            verdict = claude_verdict.verdict.upper()
            if verdict == "REAL":
                return VerificationBucket.REAL
            elif verdict == "SYNTHETIC":
                return VerificationBucket.SYNTHETIC
            elif verdict == "SUSPICIOUS":
                return VerificationBucket.SUSPICIOUS
        
        # Score-based with context adjustment
        if is_student:
            if score >= 45:
                return VerificationBucket.REAL
            elif score >= 30:
                return VerificationBucket.LIKELY_REAL
            elif score >= 20:
                return VerificationBucket.SUSPICIOUS
        else:
            if score >= 70:
                return VerificationBucket.REAL
            elif score >= 55:
                return VerificationBucket.LIKELY_REAL
            elif score >= 40:
                return VerificationBucket.SUSPICIOUS
        
        return VerificationBucket.SYNTHETIC
    
    def _get_interpretation(
        self,
        bucket: VerificationBucket,
        score: float,
    ) -> str:
        """Get human-readable interpretation."""
        interpretations = {
            VerificationBucket.REAL: f"AUTHENTIC - Strong identity verification (Score: {score:.0f})",
            VerificationBucket.LIKELY_REAL: f"LIKELY AUTHENTIC - Good verification, minor gaps (Score: {score:.0f})",
            VerificationBucket.SUSPICIOUS: f"SUSPICIOUS - Needs manual review (Score: {score:.0f})",
            VerificationBucket.SYNTHETIC: f"SYNTHETIC - High fraud risk (Score: {score:.0f})",
        }
        return interpretations.get(bucket, f"Unknown (Score: {score:.0f})")

