"""
Unified Identity Verification System - Scoring Engine (FULLY FIXED)
====================================================================

FIXED:
1. More lenient thresholds for legitimate identities
2. Better handling of minimal data scenarios
3. Adjusted bucket boundaries for realistic scoring
4. Proper graph handling with fallback scores
5. OSINT integration maintained
"""

from typing import Any, Dict, List, Optional, Tuple
import networkx as nx

from models import (
    ScoreBreakdown, VerificationBucket, TrustIndicator, TrustStrength,
    RedFlag, ClaudeVerdict,
)


# =============================================================================
# SCORING WEIGHTS (BALANCED & LENIENT)
# =============================================================================

class ScoringWeights:
    """Scoring weight configuration - balanced and lenient."""
    
    # OSINT Signals (60% total)
    FORMAT_LEGITIMACY = 0.12      # 12%
    TEMPORAL_ANALYSIS = 0.12      # 12%
    CROSS_REFERENCE = 0.08        # 8%
    PLATFORM_PRESENCE = 0.08      # 8%
    DOMAIN_TRUST = 0.06           # 6%
    BEHAVIORAL = 0.06             # 6%
    BREACH_HISTORY = 0.04         # 4%
    GEOGRAPHIC = 0.04             # 4%
    
    # Graph Signals (20% total)
    CONNECTION_COUNT = 0.08       # 8%
    TEMPORAL_DEPTH = 0.08         # 8%
    DIVERSITY = 0.04              # 4%
    
    # AI Verdict (20%)
    VERDICT_ADJUSTMENT = 0.20     # 20%


# =============================================================================
# UNIFIED SCORING ENGINE (FULLY FIXED)
# =============================================================================

class UnifiedScoringEngine:
    """
    Comprehensive scoring engine with LENIENT thresholds.
    Properly handles graph, OSINT, and all data sources.
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
        
        print(f"🔍 Scoring identity (student={is_student})...")
        
        # --- OSINT SIGNALS ---
        
        # 1. Format Legitimacy (12%)
        format_score, format_trust = self._score_format_legitimacy(
            identity, enrichment
        )
        breakdown.format_legitimacy = format_score
        trust_indicators.extend(format_trust)
        print(f"   Format: {format_score:.1f}")
        
        # 2. Temporal Analysis (12%)
        temporal_score, temporal_trust = self._score_temporal_analysis(
            enrichment, osint_data, is_student
        )
        breakdown.temporal_analysis = temporal_score
        trust_indicators.extend(temporal_trust)
        print(f"   Temporal: {temporal_score:.1f}")
        
        # 3. Cross-Reference (8%)
        cross_ref_score = self._score_cross_reference(identity, osint_data, is_student)
        breakdown.cross_reference = cross_ref_score
        print(f"   Cross-ref: {cross_ref_score:.1f}")
        
        # 4. Platform Presence (8%)
        platform_score, platform_trust = self._score_platform_presence(
            osint_data, claude_verdict, is_student
        )
        breakdown.platform_presence = platform_score
        trust_indicators.extend(platform_trust)
        print(f"   Platform: {platform_score:.1f}")
        
        # 5. Domain Trust (6%)
        domain_score = self._score_domain_trust(osint_data, is_student)
        breakdown.domain_trust = domain_score
        print(f"   Domain: {domain_score:.1f}")
        
        # 6. Behavioral (6%)
        behavioral_score = self._score_behavioral(osint_data, claude_verdict)
        breakdown.behavioral = behavioral_score
        print(f"   Behavioral: {behavioral_score:.1f}")
        
        # 7. Breach History (4%)
        breach_score, breach_trust = self._score_breach_history(enrichment)
        breakdown.breach_history = breach_score
        trust_indicators.extend(breach_trust)
        print(f"   Breach: {breach_score:.1f}")
        
        # 8. Geographic (4%)
        geo_score = self._score_geographic(enrichment)
        breakdown.geographic = geo_score
        print(f"   Geographic: {geo_score:.1f}")
        
        # --- GRAPH SIGNALS ---
        
        if graph and graph.number_of_nodes() > 0:
            print(f"   📊 Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
            
            # 9. Connection Count (8%)
            conn_score = self._score_connection_count(graph, is_student)
            breakdown.connection_count = conn_score
            print(f"   Graph connections: {conn_score:.1f}")
            
            # 10. Temporal Depth (8%)
            depth_score = self._score_temporal_depth(graph, is_student)
            breakdown.temporal_depth = depth_score
            print(f"   Graph depth: {depth_score:.1f}")
            
            # 11. Diversity (4%)
            diversity_score = self._score_diversity(graph)
            breakdown.diversity = diversity_score
            print(f"   Graph diversity: {diversity_score:.1f}")
        else:
            # No graph data - give neutral scores
            print(f"   ⚠️ No graph data - using neutral scores")
            breakdown.connection_count = 55
            breakdown.temporal_depth = 55
            breakdown.diversity = 55
        
        # --- AI VERDICT (20%) ---
        verdict_adjustment = self._score_claude_verdict(claude_verdict)
        breakdown.verdict_adjustment = verdict_adjustment
        print(f"   AI Verdict: {verdict_adjustment:.1f}")
        
        # --- RED FLAG PENALTIES ---
        total_penalty = sum(rf.penalty for rf in red_flags)
        breakdown.red_flag_penalty = total_penalty
        print(f"   Red flags penalty: -{total_penalty:.1f}")
        
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
        
        print(f"   📊 Weighted score: {weighted_score:.1f}")
        print(f"   🎯 Final score: {final_score:.1f}")
        
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
        
        # Check enrichment
        if enrichment.get('email', {}).get('is_educational'):
            return True
        
        return False
    
    def _score_format_legitimacy(
        self,
        identity: Dict,
        enrichment: Dict,
    ) -> Tuple[float, List[TrustIndicator]]:
        """Score format legitimacy - GENEROUS."""
        score = 50.0  # Start at neutral
        trust = []
        
        # Email format
        email_data = enrichment.get('email', {})
        if email_data:
            if not email_data.get('is_disposable', False):
                score += 25
                
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
                else:
                    score += 5
        
        # Phone format
        phone_data = enrichment.get('phone', {})
        if phone_data:
            if phone_data.get('valid') is True:
                score += 15
                trust.append(TrustIndicator(
                    signal=f"Valid phone ({phone_data.get('carrier', 'Unknown')})",
                    strength=TrustStrength.MEDIUM,
                    source="Numverify"
                ))
            elif phone_data.get('valid') is None:
                score += 10
        
        # Name format
        if identity.get('name'):
            parts = identity['name'].strip().split()
            if len(parts) >= 2:
                score += 5
        
        # Indian documents
        if enrichment.get('aadhaar', {}).get('years_active', 0) > 0:
            score += 10
            trust.append(TrustIndicator(
                signal="Aadhaar enrollment verified",
                strength=TrustStrength.STRONG
            ))
        
        if enrichment.get('pan', {}).get('years_active', 0) > 0:
            score += 5
            trust.append(TrustIndicator(
                signal="PAN card verified",
                strength=TrustStrength.MEDIUM
            ))
        
        return min(100, score), trust
    
    def _score_temporal_analysis(
        self,
        enrichment: Dict,
        osint_data: Optional[Dict],
        is_student: bool,
    ) -> Tuple[float, List[TrustIndicator]]:
        """Score temporal footprint - LENIENT."""
        score = 50.0
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
                score += 40
                trust.append(TrustIndicator(
                    signal=f"{int(max_age)}+ year identity footprint",
                    strength=TrustStrength.STRONG
                ))
            elif max_age >= 7:
                score += 35
            elif max_age >= 5:
                score += 30
                trust.append(TrustIndicator(
                    signal=f"{int(max_age)} year identity footprint",
                    strength=TrustStrength.MEDIUM
                ))
            elif max_age >= 3:
                score += 25
            elif max_age >= 2:
                score += 20
            elif max_age >= 1:
                score += 15
            else:
                score += 10 if is_student else 5
        
        # OSINT temporal spread
        if osint_data:
            temporal = osint_data.get('temporal_data', {})
            year_span = temporal.get('year_span', 0)
            
            if year_span >= 5:
                score += 15
                trust.append(TrustIndicator(
                    signal=f"Mentions span {year_span} years",
                    strength=TrustStrength.STRONG
                ))
            elif year_span >= 3:
                score += 10
            elif year_span >= 1:
                score += 5
        
        return min(100, score), trust
    
    def _score_cross_reference(
        self,
        identity: Dict,
        osint_data: Optional[Dict],
        is_student: bool,
    ) -> float:
        """Score cross-reference - LENIENT."""
        score = 60.0
        
        if not osint_data:
            return 55.0 if is_student else 45.0
        
        total_hits = osint_data.get('total_hits', 0)
        
        if total_hits > 0:
            score += 15
        if total_hits >= 3:
            score += 10
        if total_hits >= 5:
            score += 10
        if total_hits >= 10:
            score += 5
        
        high_trust = osint_data.get('high_trust_count', 0)
        if high_trust >= 3:
            score += 10
        elif high_trust >= 1:
            score += 5
        
        return min(100, score)
    
    def _score_platform_presence(
        self,
        osint_data: Optional[Dict],
        claude_verdict: Optional[ClaudeVerdict],
        is_student: bool,
    ) -> Tuple[float, List[TrustIndicator]]:
        """Score platform presence - LENIENT."""
        score = 50.0
        trust = []
        
        if not osint_data:
            return 60.0 if is_student else 40.0, trust
        
        profiles = osint_data.get('social_profiles', [])
        
        has_linkedin = any('linkedin' in p.get('platform', '').lower() for p in profiles)
        has_github = any('github' in p.get('platform', '').lower() for p in profiles)
        
        if has_linkedin:
            score += 20
            trust.append(TrustIndicator(
                signal="LinkedIn profile found",
                strength=TrustStrength.STRONG,
                source="linkedin.com"
            ))
        
        if has_github:
            score += 15
            trust.append(TrustIndicator(
                signal="GitHub profile found",
                strength=TrustStrength.STRONG,
                source="github.com"
            ))
        
        if len(profiles) > 0:
            score += min(15, len(profiles) * 5)
        
        news = osint_data.get('news_mentions', 0)
        if news > 0:
            score += 15
            trust.append(TrustIndicator(
                signal=f"Mentioned in {news} news source(s)",
                strength=TrustStrength.STRONG
            ))
        
        return min(100, score), trust
    
    def _score_domain_trust(
        self,
        osint_data: Optional[Dict],
        is_student: bool,
    ) -> float:
        """Score domain trust."""
        if not osint_data:
            return 60.0 if is_student else 50.0
        
        score = 50.0
        
        high_trust = osint_data.get('high_trust_count', 0)
        total = osint_data.get('total_hits', 0)
        unique_domains = len(osint_data.get('unique_domains', []))
        
        if total > 0 and high_trust > 0:
            trust_ratio = high_trust / total
            score += trust_ratio * 30
        
        if unique_domains > 0:
            score += min(15, unique_domains * 3)
        
        domains = osint_data.get('unique_domains', [])
        for domain in domains:
            if any(d in domain for d in ['.gov', '.edu', '.ac.']):
                score += 5
                break
        
        return min(100, score)
    
    def _score_behavioral(
        self,
        osint_data: Optional[Dict],
        claude_verdict: Optional[ClaudeVerdict],
    ) -> float:
        """Score behavioral patterns."""
        score = 55.0
        
        if osint_data:
            profiles = osint_data.get('social_profiles', [])
            if profiles:
                score += 15
            
            total_hits = osint_data.get('total_hits', 0)
            if total_hits >= 10:
                score += 15
            elif total_hits >= 5:
                score += 10
            elif total_hits > 0:
                score += 5
        
        if claude_verdict:
            trust_ind = claude_verdict.trust_indicators
            if trust_ind:
                score += min(15, len(trust_ind) * 5)
        
        return min(100, score)
    
    def _score_breach_history(
        self,
        enrichment: Dict,
    ) -> Tuple[float, List[TrustIndicator]]:
        """Score breach history - POSITIVE indicator."""
        score = 50.0
        trust = []
        
        email_data = enrichment.get('email', {})
        breach_count = email_data.get('breach_count', 0)
        
        if breach_count >= 1 and breach_count <= 10:
            score += 30
            trust.append(TrustIndicator(
                signal=f"Appears in {breach_count} data breach(es) - indicates real history",
                strength=TrustStrength.STRONG,
                source="HaveIBeenPwned"
            ))
        elif breach_count > 10:
            score += 20
            trust.append(TrustIndicator(
                signal="Extensive breach history indicates real account",
                strength=TrustStrength.MEDIUM,
                source="HaveIBeenPwned"
            ))
        
        return min(100, score), trust
    
    def _score_geographic(self, enrichment: Dict) -> float:
        """Score geographic consistency."""
        score = 60.0
        
        address_data = enrichment.get('address', {})
        
        if address_data:
            if address_data.get('valid') is True:
                score += 25
            elif address_data.get('valid') is None:
                score += 10
            
            if address_data.get('city') and address_data.get('state'):
                score += 15
        
        return min(100, score)
    
    def _score_connection_count(
        self,
        graph: nx.Graph,
        is_student: bool,
    ) -> float:
        """Score graph connections - LENIENT."""
        edges = graph.number_of_edges()
        
        if edges >= 12:
            return 100
        elif edges >= 8:
            return 85
        elif edges >= 5:
            return 70
        elif edges >= 3:
            return 60 if is_student else 50
        elif edges >= 1:
            return 50 if is_student else 40
        return 40 if is_student else 30
    
    def _score_temporal_depth(
        self,
        graph: nx.Graph,
        is_student: bool,
    ) -> float:
        """Score graph temporal depth - LENIENT."""
        oldest = 0.0
        
        for _, _, data in graph.edges(data=True):
            age = data.get('age_years', 0) or 0
            oldest = max(oldest, age)
        
        if oldest >= 10:
            return 100
        elif oldest >= 7:
            return 85
        elif oldest >= 5:
            return 70
        elif oldest >= 3:
            return 65 if is_student else 55
        elif oldest >= 1:
            return 55 if is_student else 45
        elif oldest >= 0.5:
            return 50 if is_student else 35
        return 45 if is_student else 30
    
    def _score_diversity(self, graph: nx.Graph) -> float:
        """Score node type diversity."""
        types = set()
        for _, data in graph.nodes(data=True):
            types.add(data.get('type', 'Unknown'))
        
        diversity_ratio = len(types) / 6
        return min(100, diversity_ratio * 80 + 30)
    
    def _score_claude_verdict(
        self,
        claude_verdict: Optional[ClaudeVerdict],
    ) -> float:
        """Convert Claude verdict to score."""
        if not claude_verdict:
            return 60.0
        
        verdict = claude_verdict.verdict.upper()
        confidence = claude_verdict.confidence / 100
        
        verdict_scores = {
            "REAL": 100,
            "LIKELY_REAL": 80,
            "INCONCLUSIVE": 60,
            "SUSPICIOUS": 30,
            "SYNTHETIC": 0,
        }
        
        base = verdict_scores.get(verdict, 60)
        return base * confidence + 60 * (1 - confidence)
    
    def _determine_bucket(
        self,
        score: float,
        claude_verdict: Optional[ClaudeVerdict],
        red_flags: List[RedFlag],
        is_student: bool,
    ) -> VerificationBucket:
        """Determine verification bucket - LENIENT."""
        
        # Critical red flags
        critical_flags = [rf for rf in red_flags if rf.severity.value == "critical"]
        if critical_flags:
            if any("DISPOSABLE" in rf.code for rf in critical_flags):
                return VerificationBucket.SYNTHETIC
            if any("IMPOSSIBLE" in rf.code for rf in critical_flags):
                return VerificationBucket.SYNTHETIC
        
        # High confidence Claude verdict
        if claude_verdict and claude_verdict.confidence >= 70:
            verdict = claude_verdict.verdict.upper()
            if verdict == "REAL":
                return VerificationBucket.REAL
            elif verdict == "SYNTHETIC" and score < 40:
                return VerificationBucket.SYNTHETIC
            elif verdict == "SUSPICIOUS" and score < 50:
                return VerificationBucket.SUSPICIOUS
        
        # Score-based with LENIENT thresholds
        if is_student:
            if score >= 50:
                return VerificationBucket.REAL
            elif score >= 35:
                return VerificationBucket.LIKELY_REAL
            elif score >= 25:
                return VerificationBucket.SUSPICIOUS
        else:
            if score >= 60:
                return VerificationBucket.REAL
            elif score >= 45:
                return VerificationBucket.LIKELY_REAL
            elif score >= 30:
                return VerificationBucket.SUSPICIOUS
        
        return VerificationBucket.SYNTHETIC
    
    def _get_interpretation(
        self,
        bucket: VerificationBucket,
        score: float,
    ) -> str:
        """Get human-readable interpretation."""
        interpretations = {
            VerificationBucket.REAL: f"AUTHENTIC - Strong identity verification (Score: {score:.0f}/100)",
            VerificationBucket.LIKELY_REAL: f"LIKELY AUTHENTIC - Good verification, minor gaps (Score: {score:.0f}/100)",
            VerificationBucket.SUSPICIOUS: f"SUSPICIOUS - Needs manual review (Score: {score:.0f}/100)",
            VerificationBucket.SYNTHETIC: f"SYNTHETIC - High fraud risk (Score: {score:.0f}/100)",
        }
        return interpretations.get(bucket, f"Unknown (Score: {score:.0f}/100)")