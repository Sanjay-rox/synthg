"""
Continuous Trainer - Orchestrates the Intelligent System
========================================================
Runs every minute, coordinates all components:
- Updates adaptive model with filtered data
- Detects anomalies in real-time
- Sends alerts when suspicious behavior found
- Retrains baseline model weekly
"""

import time
import threading
from datetime import datetime
from pathlib import Path

from .baseline_model import BaselineModel
from .adaptive_model import AdaptiveModel
from .anomaly_detector import AnomalyDetector
from .alert_manager import AlertManager


class ContinuousTrainer:
    """Main orchestrator for continuous learning system"""
    
    def __init__(self, db_path="behavioral_data.db"):
        self.db_path = db_path
        self.is_running = False
        self.training_thread = None
        
        # Initialize components
        print("[System] Initializing Behavioral Auth System...")
        
        self.baseline = BaselineModel()
        self.adaptive = AdaptiveModel(window_minutes=30)
        self.alert_manager = AlertManager()
        
        # Anomaly detector (needs both models)
        self.detector = None
        
        # Statistics
        self.iterations = 0
        self.start_time = None
        
        print("[System] ✓ System initialized")
    
    def start(self):
        """Start continuous monitoring and training"""
        
        print("\n" + "="*70)
        print("STARTING BEHAVIORAL AUTHENTICATION SYSTEM")
        print("="*70)
        
        # Step 1: Check or train baseline model
        if not self.baseline.exists():
            print("\n[System] No baseline model found. Training initial model...")
            try:
                self.baseline.train(self.db_path)
            except Exception as e:
                print(f"[System] ✗ Failed to train baseline: {e}")
                print(f"[System] Make sure you have collected data first (run.py)")
                return False
        else:
            print("\n[System] Loading existing baseline model...")
            try:
                self.baseline.load()
            except Exception as e:
                print(f"[System] ✗ Failed to load baseline: {e}")
                return False
        
        # Step 2: Initialize detector
        self.detector = AnomalyDetector(self.baseline, self.adaptive)
        
        # Step 3: Test notification system
        print("\n[System] Testing notification system...")
        self.alert_manager.send_test_notification()
        
        # Step 4: Start monitoring loop
        print("\n[System] Starting continuous monitoring...")
        print("[System] Updates every 60 seconds")
        print("[System] Press Ctrl+C to stop")
        print("="*70 + "\n")
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Run in background thread
        self.training_thread = threading.Thread(target=self._training_loop, daemon=True)
        self.training_thread.start()
        
        # Keep main thread alive
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[System] Stopping...")
            self.stop()
        
        return True
    
    def stop(self):
        """Stop continuous monitoring"""
        
        self.is_running = False
        
        if self.training_thread:
            self.training_thread.join(timeout=5)
        
        # Print final statistics
        self._print_statistics()
        
        print("\n[System] ✓ System stopped")
    
    def _training_loop(self):
        """Main loop - runs every minute"""
        
        while self.is_running:
            try:
                # Run one iteration
                self._run_iteration()
                
                # Wait 60 seconds
                for _ in range(60):
                    if not self.is_running:
                        break
                    time.sleep(1)
                
            except Exception as e:
                print(f"[System] Error in training loop: {e}")
                time.sleep(60)  # Wait before retrying
    
    def _run_iteration(self):
        """Run one minute of monitoring and training"""
        
        self.iterations += 1
        current_time = datetime.now()
        
        # Step 1: Detect anomalies in current behavior
        detection = self.detector.detect(self.db_path)
        
        # Check if there's data to analyze (check for 'status' key)
        if 'status' in detection and detection['status'] == 'no_data':
            print(f"[{current_time.strftime('%H:%M:%S')}] No new data to analyze")
            return
        
        confidence = detection['confidence']
        is_anomaly = detection['is_anomaly']
        severity = detection['severity']
        
        # Step 2: Update adaptive model (with filtered data)
        baseline_score = detection['baseline_score']
        
        # Only update if not contaminated
        if not self.adaptive.is_contaminated():
            self.adaptive.update(
                features=None,  # Will fetch from DB
                baseline_score=baseline_score,
                db_path=self.db_path
            )
        else:
            print(f"[{current_time.strftime('%H:%M:%S')}] ⚠️  Skipping update - contamination detected")
            # Clear contaminated data
            self.adaptive.clear()
        
        # Step 3: Send alerts if anomaly detected
        if is_anomaly:
            self.alert_manager.alert(detection)
            print(f"[{current_time.strftime('%H:%M:%S')}] 🚨 {severity.upper()} Alert | Confidence: {confidence:.0%}")
        else:
            print(f"[{current_time.strftime('%H:%M:%S')}] ✓ Normal | Confidence: {confidence:.0%}")
        
        # Step 4: Check if baseline needs retraining (weekly)
        if self.baseline.should_retrain():
            print(f"\n[{current_time.strftime('%H:%M:%S')}] Baseline model needs retraining...")
            self._retrain_baseline()
        
        # Step 5: Periodic statistics (every 10 minutes)
        if self.iterations % 10 == 0:
            self._print_status()
    
    def _retrain_baseline(self):
        """Retrain baseline model with accumulated data"""
        
        print("[Baseline] Retraining with new data...")
        
        try:
            # Get only high-confidence samples for training
            filtered_samples = self.adaptive.get_filtered_samples(confidence_threshold=0.6)
            
            if len(filtered_samples) < 50:
                print("[Baseline] Not enough high-confidence samples for retraining")
                return
            
            # Retrain baseline
            self.baseline.train(self.db_path)
            
            print("[Baseline] ✓ Model retrained successfully")
            
        except Exception as e:
            print(f"[Baseline] ✗ Retraining failed: {e}")
    
    def _print_status(self):
        """Print current system status"""
        
        uptime = datetime.now() - self.start_time
        hours = int(uptime.total_seconds() / 3600)
        minutes = int((uptime.total_seconds() % 3600) / 60)
        
        print("\n" + "-"*70)
        print(f"STATUS UPDATE (Uptime: {hours}h {minutes}m)")
        print("-"*70)
        
        # Baseline info
        baseline_info = self.baseline.get_info()
        print(f"Baseline Model: Trained {baseline_info.get('days_since_training', 0)} days ago")
        print(f"                {baseline_info.get('n_samples_trained', 0)} samples")
        
        # Adaptive info
        adaptive_info = self.adaptive.get_info()
        print(f"Adaptive Model: {adaptive_info['n_samples']} recent samples")
        print(f"                Avg confidence: {adaptive_info['avg_confidence']:.0%}")
        print(f"                Drift: {adaptive_info['drift_score']:.2f}")
        
        # Detection stats
        det_stats = self.detector.get_statistics()
        print(f"Detections:     {det_stats['total_detections']} total")
        print(f"                {det_stats['anomalies_detected']} anomalies")
        
        # Alert stats
        alert_stats = self.alert_manager.get_alert_stats()
        print(f"Alerts:         {alert_stats['total_alerts']} sent")
        
        print("-"*70 + "\n")
    
    def _print_statistics(self):
        """Print final statistics"""
        
        uptime = datetime.now() - self.start_time
        
        print("\n" + "="*70)
        print("FINAL STATISTICS")
        print("="*70)
        
        print(f"Total Runtime:   {uptime}")
        print(f"Total Iterations: {self.iterations}")
        
        # Detection statistics
        det_stats = self.detector.get_statistics()
        print(f"\nDetections:      {det_stats['total_detections']}")
        print(f"Anomalies Found: {det_stats['anomalies_detected']}")
        print(f"Anomaly Rate:    {det_stats.get('anomaly_rate', 0):.1%}")
        
        # Alert statistics
        alert_stats = self.alert_manager.get_alert_stats()
        print(f"\nAlerts Sent:     {alert_stats['total_alerts']}")
        
        if alert_stats['by_severity']:
            print("By Severity:")
            for sev, count in alert_stats['by_severity'].items():
                print(f"  {sev.capitalize()}: {count}")
        
        print("="*70)
    
    def run_once(self):
        """Run a single iteration (for testing)"""
        
        if not self.baseline.exists():
            print("[System] Training baseline model...")
            self.baseline.train(self.db_path)
        else:
            self.baseline.load()
        
        if self.detector is None:
            self.detector = AnomalyDetector(self.baseline, self.adaptive)
        
        print("\n[System] Running single detection...")
        self._run_iteration()
        print("[System] ✓ Done")

