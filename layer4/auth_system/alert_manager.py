"""
Alert Manager - Smart Notification System
=========================================
Sends desktop notifications when anomalies detected.
Implements rate limiting and severity-based responses.
"""

import platform
import time
from datetime import datetime, timedelta
from pathlib import Path


class AlertManager:
    """Cross-platform alert notification system"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.alert_log = self.log_dir / "alerts.log"
        
        # Rate limiting (don't spam user)
        self.last_alert_time = {}  # severity -> last alert time
        self.rate_limit_seconds = {
            'low': 600,       # Every 10 minutes
            'medium': 300,    # Every 5 minutes
            'high': 120,      # Every 2 minutes
            'critical': 60    # Every minute
        }
        
        # Alert history
        self.alert_history = []
        
        # Initialize notification system
        self.notifier = self._init_notifier()
    
    def _init_notifier(self):
        """Initialize cross-platform notification system"""
        
        try:
            from plyer import notification
            return notification
        except ImportError:
            print("[Alert] Warning: plyer not installed. Notifications disabled.")
            print("[Alert] Install with: pip install plyer")
            return None
    
    def alert(self, detection):
        """
        Send alert based on detection result
        
        Args:
            detection: Detection dict from AnomalyDetector
        """
        
        if not detection['is_anomaly']:
            return  # No alert needed
        
        severity = detection['severity']
        confidence = detection['confidence']
        explanation = detection['explanation']
        
        # Check rate limiting
        if not self._should_alert(severity):
            return  # Too soon since last alert
        
        # Log alert
        self._log_alert(detection)
        
        # Send notification
        self._send_notification(severity, confidence, explanation)
        
        # Record alert
        self.alert_history.append({
            'timestamp': datetime.now(),
            'severity': severity,
            'confidence': confidence,
            'explanation': explanation
        })
        
        # Update rate limit
        self.last_alert_time[severity] = datetime.now()
        
        print(f"[Alert] {severity.upper()} severity alert sent (confidence: {confidence:.0%})")
    
    def _should_alert(self, severity):
        """Check if enough time has passed since last alert of this severity"""
        
        if severity not in self.last_alert_time:
            return True  # First alert
        
        last_time = self.last_alert_time[severity]
        elapsed = (datetime.now() - last_time).total_seconds()
        rate_limit = self.rate_limit_seconds.get(severity, 300)
        
        return elapsed >= rate_limit
    
    def _send_notification(self, severity, confidence, explanation):
        """Send desktop notification"""
        
        if self.notifier is None:
            # Fallback: console output
            print(f"\n{'='*60}")
            print(f"⚠️  ALERT: {severity.upper()} Severity")
            print(f"Confidence: {confidence:.0%}")
            print(f"Explanation:")
            for exp in explanation[:3]:  # Show top 3 reasons
                print(f"  • {exp}")
            print(f"{'='*60}\n")
            return
        
        # Prepare notification message
        title = self._get_title(severity)
        message = self._get_message(confidence, explanation)
        
        try:
            self.notifier.notify(
                title=title,
                message=message,
                app_name='Behavioral Auth',
                timeout=10  # Show for 10 seconds
            )
        except Exception as e:
            print(f"[Alert] Failed to send notification: {e}")
            # Fallback to console
            print(f"\n⚠️  {title}")
            print(f"{message}\n")
    
    def _get_title(self, severity):
        """Get notification title based on severity"""
        
        titles = {
            'low': '⚠️  Unusual Behavior Detected',
            'medium': '🔶 Suspicious Activity',
            'high': '🔴 High Risk Activity',
            'critical': '🚨 CRITICAL: Possible Impostor'
        }
        
        return titles.get(severity, '⚠️  Alert')
    
    def _get_message(self, confidence, explanation):
        """Format notification message"""
        
        # Show top 2 explanations
        reasons = explanation[:2] if explanation else ['Behavior pattern changed']
        
        message = f"Confidence: {confidence:.0%}\n\n"
        message += "Reasons:\n"
        for reason in reasons:
            message += f"• {reason}\n"
        
        return message
    
    def _log_alert(self, detection):
        """Log alert to file"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        severity = detection['severity']
        confidence = detection['confidence']
        
        log_entry = f"[{timestamp}] {severity.upper()} | Confidence: {confidence:.2f}\n"
        
        for exp in detection['explanation']:
            log_entry += f"    - {exp}\n"
        
        log_entry += "\n"
        
        with open(self.alert_log, 'a') as f:
            f.write(log_entry)
    
    def send_test_notification(self):
        """Send test notification to verify system works"""
        
        print("[Alert] Sending test notification...")
        
        if self.notifier is None:
            print("[Alert] Notification system not available")
            return False
        
        try:
            self.notifier.notify(
                title='🧪 Test Notification',
                message='Behavioral Auth system is working!\n\nIf you see this, alerts will work correctly.',
                app_name='Behavioral Auth',
                timeout=5
            )
            print("[Alert] ✓ Test notification sent successfully")
            return True
        except Exception as e:
            print(f"[Alert] ✗ Test notification failed: {e}")
            return False
    
    def get_alert_stats(self):
        """Get alert statistics"""
        
        if not self.alert_history:
            return {
                'total_alerts': 0,
                'by_severity': {},
                'last_alert': None
            }
        
        # Count by severity
        severity_counts = {}
        for alert in self.alert_history:
            sev = alert['severity']
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        return {
            'total_alerts': len(self.alert_history),
            'by_severity': severity_counts,
            'last_alert': self.alert_history[-1]['timestamp'].isoformat(),
            'avg_confidence': sum(a['confidence'] for a in self.alert_history) / len(self.alert_history)
        }
    
    def clear_old_alerts(self, days=7):
        """Clear alerts older than N days from history"""
        
        cutoff = datetime.now() - timedelta(days=days)
        
        self.alert_history = [
            a for a in self.alert_history 
            if a['timestamp'] > cutoff
        ]
        
        print(f"[Alert] Cleared alerts older than {days} days")

