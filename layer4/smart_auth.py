#!/usr/bin/env python3
"""
Smart Behavioral Authentication System
======================================
Main entry point for the continuous learning alert system

Usage:
    python3 smart_auth.py start    - Start continuous monitoring
    python3 smart_auth.py test     - Run single detection test
    python3 smart_auth.py train    - Train baseline model only
    python3 smart_auth.py status   - Show system status
"""

import sys
import argparse
from pathlib import Path

# Add auth_system to path
sys.path.insert(0, str(Path(__file__).parent))

from auth_system import ContinuousTrainer


def print_header():
    """Print system header"""
    print()
    print("="*70)
    print("  SMART BEHAVIORAL AUTHENTICATION SYSTEM")
    print("  Continuous Learning Alert System v1.0")
    print("="*70)
    print()


def cmd_start(args):
    """Start continuous monitoring"""
    
    trainer = ContinuousTrainer(db_path=args.db)
    trainer.start()


def cmd_test(args):
    """Run single detection test"""
    
    trainer = ContinuousTrainer(db_path=args.db)
    trainer.run_once()


def cmd_train(args):
    """Train baseline model"""
    
    from auth_system.baseline_model import BaselineModel
    
    print("[Train] Training baseline model...")
    model = BaselineModel()
    
    try:
        model.train(db_path=args.db, min_samples=args.min_samples)
        print("[Train] ✓ Model trained and saved successfully")
        
        # Show model info
        info = model.get_info()
        print(f"\nModel Info:")
        print(f"  Samples: {info['n_samples_trained']}")
        print(f"  Features: {info['n_features']}")
        print(f"  Date: {info['training_date']}")
        
    except Exception as e:
        print(f"[Train] ✗ Training failed: {e}")
        sys.exit(1)


def cmd_status(args):
    """Show system status"""
    
    from auth_system.baseline_model import BaselineModel
    import sqlite3
    
    print("System Status:")
    print("-" * 70)
    
    # Check database
    db_path = Path(args.db)
    if not db_path.exists():
        print(f"❌ Database not found: {args.db}")
        print(f"   Run data collection first: python3 run.py")
        return
    
    # Check data availability
    try:
        conn = sqlite3.connect(args.db)
        cursor = conn.cursor()
        
        # Count samples
        cursor.execute("SELECT COUNT(*) FROM master_features")
        n_samples = cursor.fetchone()[0]
        
        # Get time range
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM master_features")
        min_time, max_time = cursor.fetchone()
        
        if min_time and max_time:
            duration_hours = (max_time - min_time) / 3600
            print(f"✓ Database: {args.db}")
            print(f"  Samples: {n_samples}")
            print(f"  Duration: {duration_hours:.1f} hours")
        
        conn.close()
        
    except Exception as e:
        print(f"⚠ Database check failed: {e}")
    
    # Check baseline model
    model = BaselineModel()
    if model.exists():
        model.load()
        info = model.get_info()
        
        print(f"\n✓ Baseline Model: Trained")
        print(f"  Date: {info['training_date']}")
        print(f"  Samples: {info['n_samples_trained']}")
        print(f"  Age: {info['days_since_training']} days")
        
        if info['needs_retraining']:
            print(f"  ⚠ Needs retraining (>7 days old)")
    else:
        print(f"\n❌ Baseline Model: Not trained")
        print(f"   Run: python3 smart_auth.py train")
    
    print("-" * 70)


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description='Smart Behavioral Authentication System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 smart_auth.py start              # Start continuous monitoring
  python3 smart_auth.py test               # Run single detection test
  python3 smart_auth.py train              # Train baseline model
  python3 smart_auth.py status             # Check system status
        """
    )
    
    parser.add_argument(
        'command',
        choices=['start', 'test', 'train', 'status'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--db',
        default='behavioral_data.db',
        help='Path to database (default: behavioral_data.db)'
    )
    
    parser.add_argument(
        '--min-samples',
        type=int,
        default=100,
        help='Minimum samples for training (default: 100)'
    )
    
    args = parser.parse_args()
    
    # Print header
    print_header()
    
    # Execute command
    commands = {
        'start': cmd_start,
        'test': cmd_test,
        'train': cmd_train,
        'status': cmd_status
    }
    
    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

