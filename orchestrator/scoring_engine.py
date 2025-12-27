"""
Scoring Engine for SynthGuard Orchestrator
==========================================
Weighted scoring algorithm and business rules for final verdict
"""

from typing import Dict, Any, List, Tuple
from models import (
    VerdictEnum, SeverityEnum, LayerStatusEnum,
    LayerContribution, RedFlag, ScoreBreakdown,
    Layer1Result, Layer23Result, Layer4Result, Layer5Result
)
from utils import (
    calculate_weighted_score, determine_confidence, 
    get_verdict_recommendation, setup_logger, LAYER_NAMES
)


# Setup logger
logger = setup_logger(__name__)


# =============================================================================
# SCORING ENGINE CLASS
# =============================================================================

class ScoringEngine:
    """
    Main scoring engine that calculates final verdict from all layers
    """
    
    def __init__(
        self,
        weight_layer1: float = 0.25,
        weight_layer23: float = 0.50,
        weight_layer4: float = 0.15,
        weight_layer5: float = 0.10,
        threshold_verified: int = 90,
        threshold_suspicious: int = 50
    ):
        """
        Initialize scoring engine
        
        Args:
            weight_layer1: Weight for Layer 1 (Document Forensics)
            weight_layer23: Weight for Layer 2&3 (OSINT + Graph)
            weight_layer4: Weight for Layer 4 (Behavioral)
            weight_layer5: Weight for Layer 5 (Blockchain)
            threshold_verified: Minimum score for VERIFIED verdict
            threshold_suspicious: Minimum score for SUSPICIOUS verdict
        """
        self.weights = {
            "layer_1": weight_layer1,
            "layer_2_3": weight_layer23,
            "layer_4": weight_layer4,
            "layer_5": weight_layer5
        }
        
        self.threshold_verified = threshold_verified
        self.threshold_suspicious = threshold_suspicious
        
        # Validate weights sum to 1.0
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"⚠️  Weights sum to {total_weight}, not 1.0. Normalizing...")
            self.weights = {k: v/total_weight for k, v in self.weights.items()}
        
        logger.info(f" Scoring Engine initialized - Weights: {self.weights}")
    
    def calculate_final_score(
        self,
        layer_results: Dict[str, Any]
    ) -> Tuple[float, VerdictEnum, str, List[LayerContribution], List[RedFlag], List[str]]:
        """
        Calculate final score and verdict from all layer results
        
        Args:
            layer_results: Dict of layer_id -> LayerResult
        
        Returns:
            Tuple of (final_score, verdict, confidence, contributions, red_flags, trust_indicators)
        """
        logger.info(" Starting final score calculation...")
        
        # Step 1: Check critical business rules (auto-reject conditions)
        auto_reject, reject_reason = self._check_auto_reject_rules(layer_results)
        if auto_reject:
            logger.warning(f" Auto-reject triggered: {reject_reason}")
            return self._create_reject_response(reject_reason, layer_results)
        
        # Step 2: Extract scores from successful layers
        scores = self._extract_scores(layer_results)
        
        # Step 3: Calculate weighted average
        final_score = calculate_weighted_score(scores, self.weights)
        logger.info(f" Weighted score calculated: {final_score}/100")
        
        # Step 4: Calculate layer contributions
        contributions = self._calculate_contributions(layer_results, scores)
        
        # Step 5: Collect red flags
        red_flags = self._collect_red_flags(layer_results)
        
        # Step 6: Collect trust indicators
        trust_indicators = self._collect_trust_indicators(layer_results)
        
        # Step 7: Determine verdict based on score
        verdict = self._determine_verdict(final_score)
        
        # Step 8: Determine confidence level
        confidence = determine_confidence(final_score, layer_results)
        
        logger.info(f"Final Verdict: {verdict} (Score: {final_score}, Confidence: {confidence})")
        
        return final_score, verdict, confidence, contributions, red_flags, trust_indicators
    
    def create_score_breakdown(
        self,
        final_score: float,
        verdict: VerdictEnum,
        confidence: str,
        contributions: List[LayerContribution],
        red_flags: List[RedFlag],
        trust_indicators: List[str]
    ) -> ScoreBreakdown:
        """
        Create detailed score breakdown
        
        Args:
            final_score: Final weighted score
            verdict: Final verdict
            confidence: Confidence level
            contributions: Layer contributions
            red_flags: Red flags
            trust_indicators: Trust indicators
        
        Returns:
            ScoreBreakdown object
        """
        recommendation = get_verdict_recommendation(verdict.value, confidence)
        
        return ScoreBreakdown(
            final_score=final_score,
            verdict=verdict,
            confidence=confidence,
            recommendation=recommendation,
            layer_contributions=contributions,
            red_flags=red_flags,
            trust_indicators=trust_indicators
        )
    
    # =========================================================================
    # PRIVATE METHODS - BUSINESS RULES
    # =========================================================================
    
    def _check_auto_reject_rules(
        self,
        layer_results: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Check if any auto-reject rules are triggered
        
        Args:
            layer_results: Dict of layer results
        
        Returns:
            Tuple of (should_reject, reason)
        """
        # Rule 1: Layer 5 blockchain flag (previously flagged as fraud)
        if "layer_5" in layer_results:
            layer5 = layer_results["layer_5"]
            if (layer5.status == LayerStatusEnum.SUCCESS and 
                layer5.is_flagged):
                return True, f"Previously flagged on blockchain: {layer5.flag_reason or 'Fraudulent identity'}"
        
        # Rule 2: Layer 1 - Not an Indian document
        if "layer_1" in layer_results:
            layer1 = layer_results["layer_1"]
            if (layer1.status == LayerStatusEnum.SUCCESS and 
                layer1.is_indian_document == False):
                return True, "Not an Indian identity document"
        
        # Rule 3: Layer 1 - Document score critically low
        if "layer_1" in layer_results:
            layer1 = layer_results["layer_1"]
            if (layer1.status == LayerStatusEnum.SUCCESS and 
                layer1.score < 20):
                return True, f"Document authenticity critically low (score: {layer1.score}/100)"
        
        # Rule 4: Multiple critical failures
        critical_failures = sum(
            1 for result in layer_results.values()
            if result.status == LayerStatusEnum.SUCCESS and result.score < 30
        )
        if critical_failures >= 2:
            return True, f"Multiple layers detected critical issues ({critical_failures} layers)"
        
        # No auto-reject triggered
        return False, ""
    
    def _create_reject_response(
        self,
        reason: str,
        layer_results: Dict[str, Any]
    ) -> Tuple[float, VerdictEnum, str, List[LayerContribution], List[RedFlag], List[str]]:
        """
        Create reject response when auto-reject is triggered
        
        Args:
            reason: Rejection reason
            layer_results: Layer results
        
        Returns:
            Complete scoring tuple with REJECT verdict
        """
        # Calculate contributions (for transparency)
        scores = self._extract_scores(layer_results)
        contributions = self._calculate_contributions(layer_results, scores)
        
        # Create critical red flag
        red_flags = [
            RedFlag(
                layer="orchestrator",
                severity=SeverityEnum.CRITICAL,
                message=reason,
                details="Auto-reject rule triggered"
            )
        ]
        
        # Add layer-specific red flags
        red_flags.extend(self._collect_red_flags(layer_results))
        
        return 0.0, VerdictEnum.REJECT, "HIGH", contributions, red_flags, []
    
    # =========================================================================
    # PRIVATE METHODS - SCORE EXTRACTION
    # =========================================================================
    
    def _extract_scores(self, layer_results: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract scores from layer results
        
        Args:
            layer_results: Dict of layer results
        
        Returns:
            Dict of layer_id -> score
        """
        scores = {}
        
        for layer_id, result in layer_results.items():
            if result.status == LayerStatusEnum.SUCCESS:
                scores[layer_id] = result.score
            elif result.status == LayerStatusEnum.TIMEOUT or result.status == LayerStatusEnum.ERROR:
                # Use neutral score (50) for failed layers to not penalize too heavily
                scores[layer_id] = 50.0
                logger.warning(f"⚠️  {layer_id} {result.status.value} - using neutral score (50)")
            elif result.status == LayerStatusEnum.DISABLED:
                # Don't include disabled layers in calculation
                logger.info(f" {layer_id} disabled - excluded from scoring")
                pass
        
        return scores
    
    def _calculate_contributions(
        self,
        layer_results: Dict[str, Any],
        scores: Dict[str, float]
    ) -> List[LayerContribution]:
        """
        Calculate each layer's contribution to final score
        
        Args:
            layer_results: Dict of layer results
            scores: Dict of layer scores
        
        Returns:
            List of LayerContribution objects
        """
        contributions = []
        
        for layer_id in ["layer_1", "layer_2_3", "layer_4", "layer_5"]:
            if layer_id in layer_results:
                result = layer_results[layer_id]
                score = scores.get(layer_id, 0)
                weight = self.weights.get(layer_id, 0)
                contribution = round(score * weight, 2)
                
                contributions.append(LayerContribution(
                    layer_id=layer_id,
                    layer_name=LAYER_NAMES.get(layer_id, layer_id),
                    score=score,
                    weight=weight,
                    contribution=contribution,
                    status=result.status.value,
                    key_findings=result.key_findings if hasattr(result, 'key_findings') else []
                ))
        
        return contributions
    
    # =========================================================================
    # PRIVATE METHODS - RED FLAGS & TRUST INDICATORS
    # =========================================================================
    
    def _collect_red_flags(self, layer_results: Dict[str, Any]) -> List[RedFlag]:
        """
        Collect all red flags from layer results
        
        Args:
            layer_results: Dict of layer results
        
        Returns:
            List of RedFlag objects
        """
        red_flags = []
        
        # Layer 1: Document issues
        if "layer_1" in layer_results:
            layer1 = layer_results["layer_1"]
            if layer1.status == LayerStatusEnum.SUCCESS:
                if layer1.risk_level == "High" or layer1.risk_level == "Critical":
                    red_flags.append(RedFlag(
                        layer="layer_1",
                        severity=SeverityEnum.HIGH if layer1.risk_level == "High" else SeverityEnum.CRITICAL,
                        message=f"Document risk level: {layer1.risk_level}",
                        details=layer1.verdict
                    ))
                elif layer1.score < 60:
                    red_flags.append(RedFlag(
                        layer="layer_1",
                        severity=SeverityEnum.MEDIUM,
                        message=f"Document authenticity score low: {layer1.score}/100",
                        details=layer1.verdict
                    ))
        
        # Layer 2&3: OSINT and graph issues
        if "layer_2_3" in layer_results:
            layer23 = layer_results["layer_2_3"]
            if layer23.status == LayerStatusEnum.SUCCESS:
                # Extract red flags from Layer 2&3 response
                if layer23.red_flags:
                    for flag in layer23.red_flags:
                        severity_map = {
                            "critical": SeverityEnum.CRITICAL,
                            "high": SeverityEnum.HIGH,
                            "medium": SeverityEnum.MEDIUM,
                            "low": SeverityEnum.LOW
                        }
                        red_flags.append(RedFlag(
                            layer="layer_2_3",
                            severity=severity_map.get(flag.get('severity', 'medium').lower(), SeverityEnum.MEDIUM),
                            message=flag.get('message', 'OSINT/Graph anomaly detected'),
                            details=flag.get('details')
                        ))
                
                # Check Claude verdict
                if layer23.claude_verdict == "LIKELY_SYNTHETIC":
                    red_flags.append(RedFlag(
                        layer="layer_2_3",
                        severity=SeverityEnum.HIGH,
                        message="AI analysis suggests likely synthetic identity",
                        details=f"Claude confidence: {layer23.claude_confidence}%"
                    ))
        
        # Layer 4: Behavioral anomalies
        if "layer_4" in layer_results:
            layer4 = layer_results["layer_4"]
            if layer4.status == LayerStatusEnum.SUCCESS:
                if layer4.anomaly_detected:
                    red_flags.append(RedFlag(
                        layer="layer_4",
                        severity=SeverityEnum.HIGH,
                        message="Behavioral anomaly detected",
                        details=f"Bot probability: {layer4.bot_probability:.2%}" if layer4.bot_probability else None
                    ))
                
                # Check for suspicious indicators
                if layer4.suspicious_indicators:
                    for indicator in layer4.suspicious_indicators[:3]:  # Top 3
                        red_flags.append(RedFlag(
                            layer="layer_4",
                            severity=SeverityEnum.MEDIUM,
                            message=indicator
                        ))
        
        # Layer 5: Blockchain issues
        if "layer_5" in layer_results:
            layer5 = layer_results["layer_5"]
            if layer5.status == LayerStatusEnum.SUCCESS:
                if layer5.is_flagged:
                    red_flags.append(RedFlag(
                        layer="layer_5",
                        severity=SeverityEnum.CRITICAL,
                        message="Previously flagged on blockchain consortium",
                        details=layer5.flag_reason
                    ))
                elif not layer5.exists and layer5.score < 50:
                    red_flags.append(RedFlag(
                        layer="layer_5",
                        severity=SeverityEnum.LOW,
                        message="No blockchain verification history",
                        details="First-time verification"
                    ))
        
        # Sort by severity
        severity_order = {
            SeverityEnum.CRITICAL: 0,
            SeverityEnum.HIGH: 1,
            SeverityEnum.MEDIUM: 2,
            SeverityEnum.LOW: 3
        }
        red_flags.sort(key=lambda x: severity_order[x.severity])
        
        return red_flags
    
    def _collect_trust_indicators(self, layer_results: Dict[str, Any]) -> List[str]:
        """
        Collect positive trust indicators from layer results
        
        Args:
            layer_results: Dict of layer results
        
        Returns:
            List of trust indicator strings
        """
        trust_indicators = []
        
        # Layer 1: Document authenticity
        if "layer_1" in layer_results:
            layer1 = layer_results["layer_1"]
            if layer1.status == LayerStatusEnum.SUCCESS and layer1.score >= 80:
                trust_indicators.append(f"Document appears authentic (score: {layer1.score}/100)")
            if layer1.is_indian_document:
                trust_indicators.append("Valid Indian identity document detected")
        
        # Layer 2&3: OSINT and graph
        if "layer_2_3" in layer_results:
            layer23 = layer_results["layer_2_3"]
            if layer23.status == LayerStatusEnum.SUCCESS:
                if layer23.trust_indicators:
                    trust_indicators.extend(layer23.trust_indicators[:5])  # Top 5
                if layer23.claude_verdict == "LIKELY_REAL":
                    trust_indicators.append(f"AI analysis confirms likely authentic (confidence: {layer23.claude_confidence}%)")
        
        # Layer 4: Behavioral
        if "layer_4" in layer_results:
            layer4 = layer_results["layer_4"]
            if layer4.status == LayerStatusEnum.SUCCESS:
                if layer4.human_indicators:
                    trust_indicators.extend(layer4.human_indicators[:3])  # Top 3
        
        # Layer 5: Blockchain
        if "layer_5" in layer_results:
            layer5 = layer_results["layer_5"]
            if layer5.status == LayerStatusEnum.SUCCESS:
                if layer5.exists and not layer5.is_flagged:
                    trust_indicators.append(
                        f"Previously verified {layer5.verification_count} time(s) on blockchain"
                    )
                if layer5.trust_score and layer5.trust_score >= 80:
                    trust_indicators.append(f"High blockchain trust score: {layer5.trust_score}/100")
        
        return trust_indicators
    
    # =========================================================================
    # PRIVATE METHODS - VERDICT DETERMINATION
    # =========================================================================
    
    def _determine_verdict(self, final_score: float) -> VerdictEnum:
        """
        Determine verdict based on final score
        
        Args:
            final_score: Final weighted score
        
        Returns:
            VerdictEnum (VERIFIED, SUSPICIOUS, or REJECT)
        """
        if final_score >= self.threshold_verified:
            return VerdictEnum.VERIFIED
        elif final_score >= self.threshold_suspicious:
            return VerdictEnum.SUSPICIOUS
        else:
            return VerdictEnum.REJECT