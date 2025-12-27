"""
Intelligent Behavioral Authentication System
============================================
Continuous learning alert system for behavioral anomaly detection
"""

from .continuous_trainer import ContinuousTrainer
from .baseline_model import BaselineModel
from .adaptive_model import AdaptiveModel
from .anomaly_detector import AnomalyDetector
from .alert_manager import AlertManager

__version__ = "1.0.0"
__all__ = [
    'ContinuousTrainer',
    'BaselineModel',
    'AdaptiveModel',
    'AnomalyDetector',
    'AlertManager'
]

