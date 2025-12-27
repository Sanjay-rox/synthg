"""
Baseline Model - Long-term Behavioral Profile
==============================================
Represents the user's core behavioral signature.
Updated weekly with confirmed legitimate data.
"""

import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import sqlite3


class BaselineModel:
    """Long-term behavioral baseline model"""
    
    def __init__(self, model_dir="models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.training_date = None
        self.n_samples_trained = 0
        
        self.model_path = self.model_dir / "baseline_model.pkl"
        self.scaler_path = self.model_dir / "baseline_scaler.pkl"
        self.metadata_path = self.model_dir / "baseline_metadata.pkl"
    
    def train(self, db_path="behavioral_data.db", min_samples=100):
        """Train baseline model on historical legitimate data"""
        
        print("[Baseline] Training long-term behavioral profile...")
        
        # Load data from database
        data = self._load_training_data(db_path)
        
        if len(data) < min_samples:
            print(f"[Baseline] Warning: Only {len(data)} samples available (minimum: {min_samples})")
            print(f"[Baseline] Collecting more data recommended for better accuracy")
        
        # Extract features (drop metadata columns)
        feature_cols = [col for col in data.columns 
                       if col not in ['id', 'user_id', 'session_id', 'timestamp']]
        
        X = data[feature_cols].values
        self.feature_names = feature_cols
        
        # Remove any contamination (outliers in training data)
        X_clean = self._remove_outliers(X)
        
        print(f"[Baseline] Training on {len(X_clean)} samples ({len(feature_cols)} features)")
        print(f"[Baseline] Removed {len(X) - len(X_clean)} outliers from training data")
        
        # Normalize features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_clean)
        
        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=0.1,  # Expect 10% anomalies
            random_state=42,
            n_estimators=100,
            max_samples='auto',
            verbose=0
        )
        
        self.model.fit(X_scaled)
        
        self.training_date = datetime.now()
        self.n_samples_trained = len(X_clean)
        
        # Save model
        self.save()
        
        print(f"[Baseline] ✓ Model trained successfully")
        print(f"[Baseline] Training date: {self.training_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return self
    
    def _load_training_data(self, db_path):
        """Load behavioral data from database"""
        
        conn = sqlite3.connect(db_path)
        
        # Load all master_features data
        query = "SELECT * FROM master_features ORDER BY timestamp DESC"
        
        try:
            df = pd.read_sql_query(query, conn)
        except Exception as e:
            print(f"[Baseline] Error loading data: {e}")
            conn.close()
            return pd.DataFrame()
        
        conn.close()
        
        # Handle missing values
        df = df.fillna(0)
        
        return df
    
    def _remove_outliers(self, X, contamination=0.05):
        """Remove outliers from training data to prevent contamination"""
        
        if len(X) < 50:
            return X  # Not enough data to detect outliers reliably
        
        # Use a temporary Isolation Forest to detect outliers
        temp_model = IsolationForest(contamination=contamination, random_state=42)
        predictions = temp_model.fit_predict(X)
        
        # Keep only inliers (predictions == 1)
        mask = predictions == 1
        return X[mask]
    
    def score(self, features):
        """
        Score a behavior sample
        Returns confidence score (0-1, higher = more normal)
        """
        
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Ensure features are in correct order
        if isinstance(features, dict):
            features = np.array([features[col] for col in self.feature_names])
        
        features = np.array(features).reshape(1, -1)
        
        # Normalize
        features_scaled = self.scaler.transform(features)
        
        # Get anomaly score (lower = more anomalous)
        anomaly_score = self.model.decision_function(features_scaled)[0]
        
        # Convert to confidence (0-1 scale, higher = more confident)
        # Anomaly scores typically range from -0.5 to 0.5
        confidence = (anomaly_score + 0.5) / 1.0
        confidence = np.clip(confidence, 0, 1)
        
        return confidence
    
    def predict(self, features):
        """
        Predict if behavior is normal or anomalous
        Returns: 'normal' or 'anomaly'
        """
        
        confidence = self.score(features)
        
        if confidence >= 0.5:
            return 'normal'
        else:
            return 'anomaly'
    
    def should_retrain(self, days_threshold=7):
        """Check if model should be retrained (weekly)"""
        
        if self.training_date is None:
            return True
        
        days_since_training = (datetime.now() - self.training_date).days
        return days_since_training >= days_threshold
    
    def save(self):
        """Save model to disk"""
        
        if self.model is None:
            raise ValueError("No model to save")
        
        # Save model
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        # Save scaler
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # Save metadata
        metadata = {
            'feature_names': self.feature_names,
            'training_date': self.training_date,
            'n_samples_trained': self.n_samples_trained
        }
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"[Baseline] Model saved to {self.model_dir}")
    
    def load(self):
        """Load model from disk"""
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        
        # Load model
        with open(self.model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        # Load scaler
        with open(self.scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
        
        # Load metadata
        with open(self.metadata_path, 'rb') as f:
            metadata = pickle.load(f)
            self.feature_names = metadata['feature_names']
            self.training_date = metadata['training_date']
            self.n_samples_trained = metadata['n_samples_trained']
        
        print(f"[Baseline] Model loaded (trained {self.training_date.strftime('%Y-%m-%d')})")
        print(f"[Baseline] Trained on {self.n_samples_trained} samples")
        
        return self
    
    def exists(self):
        """Check if trained model exists"""
        return self.model_path.exists()
    
    def get_info(self):
        """Get model information"""
        
        if self.model is None:
            return {"status": "not_trained"}
        
        days_since_training = (datetime.now() - self.training_date).days
        
        return {
            'status': 'trained',
            'training_date': self.training_date.isoformat(),
            'days_since_training': days_since_training,
            'n_samples_trained': self.n_samples_trained,
            'n_features': len(self.feature_names),
            'needs_retraining': self.should_retrain()
        }

