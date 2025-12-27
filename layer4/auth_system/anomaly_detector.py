"""
Anomaly Detector - Intelligent Behavior Scoring
===============================================
Combines baseline + adaptive models + statistics + rules
Makes final decision on behavior legitimacy
"""

import numpy as np
import pandas as pd
from datetime import datetime
import sqlite3


class AnomalyDetector:
    """Multi-model anomaly detection with intelligent fusion"""
    
    def __init__(self, baseline_model, adaptive_model):
        self.baseline_model = baseline_model
        self.adaptive_model = adaptive_model
        
        # Thresholds (from config)
        self.thresholds = {
            'critical': 0.2,   # <20% confidence
            'high': 0.3,       # <30% confidence
            'medium': 0.5,     # <50% confidence
            'low': 0.7         # <70% confidence
        }
        
        self.detection_history = []
    
    def detect(self, db_path="behavioral_data.db"):
        """
        Detect anomalies in current behavior
        
        Returns:
            dict with detection results
        """
        
        # Get latest behavior from database
        latest_features = self._get_latest_features(db_path)
        
        if latest_features is None:
            return {
                'status': 'no_data',
                'confidence': 0.5,
                'is_anomaly': False,
                'severity': 'none'
            }
        
        # Step 1: Baseline model score (long-term profile)
        baseline_score = self.baseline_model.score(latest_features)
        
        # Step 2: Adaptive model score (recent pattern)
        adaptive_score = self.adaptive_model.score(latest_features)
        
        # Step 3: Statistical checks
        stat_score = self._statistical_check(latest_features)
        
        # Step 4: Rule-based checks
        rule_violations = self._rule_check(latest_features)
        rule_score = 1.0 if len(rule_violations) == 0 else 0.3
        
        # Step 5: Fusion (weighted combination)
        final_confidence = self._fuse_scores(
            baseline_score, 
            adaptive_score,
            stat_score,
            rule_score
        )
        
        # Step 6: Determine severity
        severity = self._determine_severity(final_confidence)
        is_anomaly = severity != 'none'
        
        # Step 7: Generate explanation
        explanation = self._explain_detection(
            latest_features,
            baseline_score,
            adaptive_score,
            stat_score,
            rule_violations
        )
        
        # Record detection
        detection = {
            'timestamp': datetime.now(),
            'confidence': final_confidence,
            'baseline_score': baseline_score,
            'adaptive_score': adaptive_score,
            'stat_score': stat_score,
            'rule_score': rule_score,
            'is_anomaly': is_anomaly,
            'severity': severity,
            'explanation': explanation,
            'rule_violations': rule_violations
        }
        
        self.detection_history.append(detection)
        
        # Keep last 100 detections
        if len(self.detection_history) > 100:
            self.detection_history = self.detection_history[-100:]
        
        return detection
    
    def _get_latest_features(self, db_path):
        """Get most recent behavioral features"""
        
        conn = sqlite3.connect(db_path)
        
        query = """
            SELECT * FROM master_features 
            ORDER BY timestamp DESC 
            LIMIT 10
        """
        
        try:
            df = pd.read_sql_query(query, conn)
        except:
            conn.close()
            return None
        
        conn.close()
        
        if len(df) == 0:
            return None
        
        # Average last 10 samples (last ~2 minutes)
        feature_cols = [col for col in df.columns 
                       if col not in ['id', 'user_id', 'session_id', 'timestamp']]
        
        features = {}
        for col in feature_cols:
            features[col] = df[col].mean()
        
        return features
    
    def _statistical_check(self, features):
        """Statistical validation of features"""
        
        # Check if features are within reasonable ranges
        violations = 0
        total_checks = 0
        
        # Example checks (can be extended)
        checks = {
            'ks_typing_speed': (0, 15),      # 0-15 keys/sec is reasonable
            'ms_avg_speed': (0, 3000),       # 0-3000 px/sec
            'ks_error_rate': (0, 0.5),       # 0-50% error rate
            'sys_cpu_usage': (0, 1.0),       # 0-100%
            'sys_memory_usage': (0, 1.0)     # 0-100%
        }
        
        for feature, (min_val, max_val) in checks.items():
            if feature in features:
                value = features[feature]
                total_checks += 1
                
                if not (min_val <= value <= max_val):
                    violations += 1
        
        # Score based on violation rate
        if total_checks == 0:
            return 1.0
        
        violation_rate = violations / total_checks
        stat_score = 1.0 - violation_rate
        
        return max(stat_score, 0.0)
    
    def _rule_check(self, features):
        """Rule-based anomaly detection"""
        
        violations = []
        
        # Rule 1: Superhuman typing speed
        if features.get('ks_typing_speed', 0) > 12:
            violations.append("Typing speed unusually high (>12 keys/sec)")
        
        # Rule 2: Impossible mouse speed
        if features.get('ms_avg_speed', 0) > 2500:
            violations.append("Mouse speed unrealistic (>2500 px/sec)")
        
        # Rule 3: Zero activity (possible system freeze or takeover)
        if (features.get('ks_typing_speed', 0) == 0 and 
            features.get('ms_avg_speed', 0) == 0):
            violations.append("No user activity detected")
        
        # Rule 4: Unusual time-of-day activity (can be customized)
        hour = datetime.now().hour
        if hour >= 2 and hour <= 5:  # 2 AM - 5 AM
            if features.get('ss_activity_intensity', 0) > 0.5:
                violations.append("High activity during unusual hours (2-5 AM)")
        
        return violations
    
    def _fuse_scores(self, baseline, adaptive, stat, rule):
        """
        Intelligently combine all scores
        Weighted fusion with context awareness
        """
        
        # Base weights
        weights = {
            'baseline': 0.5,   # Most important (your core profile)
            'adaptive': 0.25,  # Recent adjustments
            'stat': 0.15,      # Statistical validation
            'rule': 0.10       # Rule compliance
        }
        
        # Adjust weights based on context
        
        # If adaptive model detects drift, trust baseline more
        drift = self.adaptive_model.get_drift_score()
        if drift > 0.3:
            weights['baseline'] += 0.1
            weights['adaptive'] -= 0.1
        
        # If adaptive model is contaminated, ignore it
        if self.adaptive_model.is_contaminated():
            weights['baseline'] = 0.7
            weights['adaptive'] = 0.0
            weights['stat'] = 0.2
            weights['rule'] = 0.1
        
        # Calculate weighted average
        final_score = (
            baseline * weights['baseline'] +
            adaptive * weights['adaptive'] +
            stat * weights['stat'] +
            rule * weights['rule']
        )
        
        return np.clip(final_score, 0, 1)
    
    def _determine_severity(self, confidence):
        """Determine alert severity based on confidence"""
        
        if confidence >= self.thresholds['low']:
            return 'none'  # Normal behavior
        elif confidence >= self.thresholds['medium']:
            return 'low'
        elif confidence >= self.thresholds['high']:
            return 'medium'
        elif confidence >= self.thresholds['critical']:
            return 'high'
        else:
            return 'critical'
    
    def _explain_detection(self, features, baseline, adaptive, stat, violations):
        """Generate human-readable explanation"""
        
        explanations = []
        
        # Baseline model explanation
        if baseline < 0.5:
            explanations.append(
                f"Behavior differs from your baseline profile (confidence: {baseline:.0%})"
            )
        
        # Adaptive model explanation
        if adaptive < 0.5:
            explanations.append(
                f"Recent behavior pattern changed (confidence: {adaptive:.0%})"
            )
        
        # Statistical anomalies
        if stat < 0.8:
            explanations.append(
                "Some behavioral metrics outside normal range"
            )
        
        # Rule violations
        if violations:
            for violation in violations:
                explanations.append(violation)
        
        # Feature-specific explanations (top anomalies)
        feature_anomalies = self._identify_anomalous_features(features)
        explanations.extend(feature_anomalies[:3])  # Top 3
        
        return explanations
    
    def _identify_anomalous_features(self, features):
        """Identify which features are most anomalous"""
        
        anomalies = []
        
        # Compare against adaptive model's recent averages
        for feature_name in self.adaptive_model.feature_names:
            if feature_name not in features:
                continue
            
            value = features[feature_name]
            mean = self.adaptive_model.feature_means.get(feature_name, 0)
            std = self.adaptive_model.feature_stds.get(feature_name, 1)
            
            if std == 0:
                continue
            
            z_score = abs((value - mean) / std)
            
            if z_score > 2.0:  # Outside 95% confidence interval
                percent_diff = ((value - mean) / mean * 100) if mean != 0 else 0
                feature_readable = feature_name.replace('_', ' ').title()
                
                if percent_diff > 0:
                    anomalies.append(
                        f"{feature_readable}: {abs(percent_diff):.0f}% higher than recent average"
                    )
                else:
                    anomalies.append(
                        f"{feature_readable}: {abs(percent_diff):.0f}% lower than recent average"
                    )
        
        return sorted(anomalies)[:5]  # Return top 5
    
    def get_statistics(self):
        """Get detection statistics"""
        
        if not self.detection_history:
            return {
                'total_detections': 0,
                'anomalies_detected': 0,
                'avg_confidence': 0
            }
        
        total = len(self.detection_history)
        anomalies = sum(1 for d in self.detection_history if d['is_anomaly'])
        avg_conf = np.mean([d['confidence'] for d in self.detection_history])
        
        # Severity breakdown
        severity_counts = {}
        for d in self.detection_history:
            sev = d['severity']
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        return {
            'total_detections': total,
            'anomalies_detected': anomalies,
            'avg_confidence': float(avg_conf),
            'anomaly_rate': float(anomalies / total),
            'severity_breakdown': severity_counts,
            'last_detection': self.detection_history[-1]['timestamp'].isoformat()
        }

