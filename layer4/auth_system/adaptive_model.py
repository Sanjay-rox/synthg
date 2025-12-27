"""
Adaptive Model - Short-term Behavioral Adjustments
==================================================
Updates every minute based on recent behavior.
Handles variations (tired, different setup, time of day).
"""

import numpy as np
import pandas as pd
from collections import deque
from datetime import datetime
import sqlite3


class AdaptiveModel:
    """Short-term adaptive model with incremental learning"""
    
    def __init__(self, window_minutes=30):
        self.window_minutes = window_minutes
        self.recent_samples = deque(maxlen=window_minutes)  # Last 30 minutes
        self.recent_scores = deque(maxlen=window_minutes)   # Baseline scores
        
        # Statistical baseline (mean and std for each feature)
        self.feature_means = {}
        self.feature_stds = {}
        self.feature_names = []
        
        self.last_update = None
        self.n_updates = 0
    
    def update(self, features, baseline_score, db_path="behavioral_data.db"):
        """
        Update adaptive model with new minute of data
        
        Args:
            features: Current behavior features (dict or array)
            baseline_score: Score from baseline model
            db_path: Path to database
        """
        
        # Get last minute of data from database
        recent_data = self._get_recent_data(db_path, minutes=1)
        
        if len(recent_data) == 0:
            return  # No new data
        
        # Calculate average features for this minute
        minute_features = self._aggregate_minute_features(recent_data)
        
        # Store sample with its baseline score
        self.recent_samples.append({
            'features': minute_features,
            'baseline_score': baseline_score,
            'timestamp': datetime.now()
        })
        
        self.recent_scores.append(baseline_score)
        
        # Update statistical baseline
        self._update_statistics()
        
        self.last_update = datetime.now()
        self.n_updates += 1
        
        if self.n_updates % 10 == 0:  # Log every 10 minutes
            print(f"[Adaptive] Updated (total: {self.n_updates} updates)")
    
    def _get_recent_data(self, db_path, minutes=1):
        """Get last N minutes of data from database"""
        
        import time
        cutoff_time = time.time() - (minutes * 60)
        
        conn = sqlite3.connect(db_path)
        
        query = """
            SELECT * FROM master_features 
            WHERE timestamp > ? 
            ORDER BY timestamp DESC
        """
        
        try:
            df = pd.read_sql_query(query, conn, params=(cutoff_time,))
        except:
            df = pd.DataFrame()
        
        conn.close()
        return df
    
    def _aggregate_minute_features(self, data):
        """Calculate average features for the minute"""
        
        if len(data) == 0:
            return {}
        
        # Extract feature columns
        feature_cols = [col for col in data.columns 
                       if col not in ['id', 'user_id', 'session_id', 'timestamp']]
        
        # Calculate mean of each feature
        features = {}
        for col in feature_cols:
            features[col] = data[col].mean()
        
        return features
    
    def _update_statistics(self):
        """Update running statistics of recent behavior"""
        
        if len(self.recent_samples) < 5:
            return  # Need minimum samples
        
        # Extract all features
        all_features = {}
        for sample in self.recent_samples:
            for key, value in sample['features'].items():
                if key not in all_features:
                    all_features[key] = []
                all_features[key].append(value)
        
        # Calculate mean and std for each feature
        for feature, values in all_features.items():
            self.feature_means[feature] = np.mean(values)
            self.feature_stds[feature] = np.std(values)
        
        self.feature_names = list(all_features.keys())
    
    def score(self, features):
        """
        Score current behavior against recent pattern
        Returns confidence (0-1, higher = more similar to recent behavior)
        """
        
        if len(self.recent_samples) < 5:
            return 0.5  # Not enough data, neutral score
        
        # Calculate Z-scores for each feature
        z_scores = []
        
        for feature_name in self.feature_names:
            if feature_name not in features:
                continue
            
            value = features[feature_name]
            mean = self.feature_means.get(feature_name, 0)
            std = self.feature_stds.get(feature_name, 1)
            
            if std == 0:
                z_score = 0
            else:
                z_score = abs((value - mean) / std)
            
            z_scores.append(z_score)
        
        # Average Z-score
        avg_z = np.mean(z_scores) if z_scores else 0
        
        # Convert to confidence (higher Z-score = lower confidence)
        # Z-score of 2 or more is unusual (outside 95% confidence interval)
        confidence = 1.0 / (1.0 + avg_z / 2.0)
        
        return np.clip(confidence, 0, 1)
    
    def get_drift_score(self):
        """
        Calculate how much recent behavior has drifted from baseline
        Returns: drift score (0-1, higher = more drift)
        """
        
        if len(self.recent_scores) < 5:
            return 0.0
        
        # Calculate how baseline scores have changed
        recent_avg = np.mean(list(self.recent_scores)[-10:])  # Last 10 minutes
        older_avg = np.mean(list(self.recent_scores)[:10])    # First 10 minutes
        
        drift = abs(recent_avg - older_avg)
        return np.clip(drift, 0, 1)
    
    def is_contaminated(self, threshold=0.3):
        """
        Check if recent data might be contaminated (impostor)
        Returns True if >30% of recent samples are suspicious
        """
        
        if len(self.recent_scores) < 10:
            return False  # Not enough data
        
        # Count low-confidence samples
        suspicious_count = sum(1 for score in self.recent_scores if score < 0.5)
        suspicious_ratio = suspicious_count / len(self.recent_scores)
        
        is_contam = suspicious_ratio > threshold
        
        if is_contam:
            print(f"[Adaptive] ⚠️ Contamination detected! {suspicious_ratio:.1%} suspicious samples")
        
        return is_contam
    
    def get_filtered_samples(self, confidence_threshold=0.6):
        """
        Get only high-confidence samples for safe training
        Filters out potential impostor data
        """
        
        filtered = []
        
        for sample in self.recent_samples:
            if sample['baseline_score'] >= confidence_threshold:
                filtered.append(sample['features'])
        
        return filtered
    
    def get_info(self):
        """Get adaptive model information"""
        
        drift = self.get_drift_score()
        contaminated = self.is_contaminated()
        
        avg_confidence = np.mean(self.recent_scores) if self.recent_scores else 0
        
        return {
            'n_samples': len(self.recent_samples),
            'window_minutes': self.window_minutes,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'n_updates': self.n_updates,
            'avg_confidence': float(avg_confidence),
            'drift_score': float(drift),
            'is_contaminated': contaminated,
            'n_features_tracked': len(self.feature_names)
        }
    
    def clear(self):
        """Clear recent samples (e.g., when contamination detected)"""
        
        print("[Adaptive] Clearing contaminated data...")
        self.recent_samples.clear()
        self.recent_scores.clear()
        self.feature_means.clear()
        self.feature_stds.clear()

