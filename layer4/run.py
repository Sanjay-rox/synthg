#!/usr/bin/env python3
"""
Intelligent Bootstrap & Run Script for Behavioral Data Collection System
==========================================================================
This script automatically:
- Detects OS and configures accordingly
- Checks Python version and dependencies
- Installs requirements if missing
- Validates permissions (keyboard/mouse access)
- Sets up security configurations
- Performs health checks
- Runs the data collector safely

Compatible with: macOS, Linux, Windows
"""

import sys
import os
import platform
import subprocess
import importlib
from pathlib import Path
import json


class IntelligentBootstrap:
    """Smart system setup and configuration"""
    
    def __init__(self):
        self.os_type = platform.system()
        self.os_version = platform.version()
        self.python_version = sys.version_info
        self.home = Path.home()
        self.script_dir = Path(__file__).parent
        self.config_file = self.home / ".behavioral_auth_config.json"
        
        # Color codes for terminal output
        self.GREEN = '\033[92m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.BLUE = '\033[94m'
        self.RESET = '\033[0m'
        self.BOLD = '\033[1m'
    
    def print_header(self):
        """Print system header"""
        print("=" * 80)
        print(f"{self.BOLD}BEHAVIORAL AUTHENTICATION - INTELLIGENT BOOTSTRAP{self.RESET}")
        print("=" * 80)
        print(f"\n{self.BLUE}System Information:{self.RESET}")
        print(f"  OS: {self.os_type} ({platform.platform()})")
        print(f"  Python: {sys.version.split()[0]}")
        print(f"  Architecture: {platform.machine()}")
        print(f"  User: {os.getlogin() if hasattr(os, 'getlogin') else 'unknown'}")
        print("=" * 80)
    
    def check_python_version(self):
        """Validate Python version"""
        print(f"\n{self.BOLD}[1/8] Checking Python Version...{self.RESET}")
        
        if self.python_version < (3, 7):
            print(f"{self.RED}✗ Python 3.7+ required. Found: {sys.version.split()[0]}{self.RESET}")
            print(f"\n{self.YELLOW}Please upgrade Python:{self.RESET}")
            if self.os_type == "Darwin":
                print("  brew install python3")
            elif self.os_type == "Linux":
                print("  sudo apt-get install python3.9  # Ubuntu/Debian")
                print("  sudo yum install python39       # RedHat/CentOS")
            elif self.os_type == "Windows":
                print("  Download from: https://www.python.org/downloads/")
            return False
        
        print(f"{self.GREEN}✓ Python {sys.version.split()[0]} - OK{self.RESET}")
        return True
    
    def check_pip(self):
        """Check if pip is available"""
        print(f"\n{self.BOLD}[2/8] Checking Package Manager (pip)...{self.RESET}")
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                          capture_output=True, check=True)
            print(f"{self.GREEN}✓ pip is available{self.RESET}")
            return True
        except subprocess.CalledProcessError:
            print(f"{self.RED}✗ pip not found{self.RESET}")
            print(f"\n{self.YELLOW}Installing pip:{self.RESET}")
            
            if self.os_type in ["Darwin", "Linux"]:
                print("  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py")
                print("  python3 get-pip.py")
            elif self.os_type == "Windows":
                print("  python -m ensurepip --upgrade")
            
            return False
    
    def install_dependencies(self):
        """Install required Python packages"""
        print(f"\n{self.BOLD}[3/8] Checking Dependencies...{self.RESET}")
        
        requirements = {
            'numpy': 'numpy>=1.24.0',
            'pandas': 'pandas>=2.0.0',
            'pynput': 'pynput>=1.7.6',
            'psutil': 'psutil>=5.9.0',
            'cryptography': 'cryptography>=41.0.0'
        }
        
        missing = []
        installed = []
        
        for package, requirement in requirements.items():
            try:
                importlib.import_module(package)
                installed.append(package)
                print(f"  {self.GREEN}✓{self.RESET} {package}")
            except ImportError:
                missing.append(requirement)
                print(f"  {self.YELLOW}✗{self.RESET} {package} - missing")
        
        if not missing:
            print(f"\n{self.GREEN}✓ All dependencies installed{self.RESET}")
            return True
        
        print(f"\n{self.YELLOW}Installing {len(missing)} missing package(s)...{self.RESET}")
        
        try:
            for req in missing:
                print(f"  Installing {req}...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", req, "--quiet"],
                    check=True,
                    capture_output=True
                )
                print(f"  {self.GREEN}✓{self.RESET} {req.split('>=')[0]} installed")
            
            print(f"\n{self.GREEN}✓ All dependencies installed successfully{self.RESET}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"{self.RED}✗ Installation failed: {e}{self.RESET}")
            print(f"\n{self.YELLOW}Manual installation:{self.RESET}")
            print(f"  pip3 install {' '.join(missing)}")
            return False
    
    def check_permissions(self):
        """Check OS-specific permissions for keyboard/mouse access"""
        print(f"\n{self.BOLD}[4/8] Checking System Permissions...{self.RESET}")
        
        if self.os_type == "Darwin":  # macOS
            print(f"  {self.BLUE}macOS Detected{self.RESET}")
            print(f"  Checking Accessibility permissions...")
            
            # Test if we can create listeners
            try:
                from pynput import keyboard
                test_listener = keyboard.Listener(on_press=lambda k: None)
                test_listener.start()
                test_listener.stop()
                print(f"  {self.GREEN}✓ Accessibility permissions granted{self.RESET}")
                return True
            except Exception as e:
                print(f"  {self.YELLOW}⚠ Accessibility permissions needed{self.RESET}")
                print(f"\n{self.YELLOW}Grant permissions:{self.RESET}")
                print(f"  1. Open: System Preferences → Security & Privacy → Privacy")
                print(f"  2. Select: Accessibility")
                print(f"  3. Add: Terminal (or your terminal app)")
                print(f"  4. Check the box to enable")
                print(f"\n  Then run this script again.")
                return "warning"
        
        elif self.os_type == "Linux":
            print(f"  {self.BLUE}Linux Detected{self.RESET}")
            
            # Check if running in X11 or Wayland
            display = os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')
            
            if not display:
                print(f"  {self.RED}✗ No display server detected{self.RESET}")
                print(f"  Running in headless mode? This requires a display.")
                return False
            
            # Check if user has input group permissions
            try:
                import grp
                groups = [grp.getgrgid(g).gr_name for g in os.getgroups()]
                
                if 'input' in groups or os.geteuid() == 0:
                    print(f"  {self.GREEN}✓ Input device permissions OK{self.RESET}")
                else:
                    print(f"  {self.YELLOW}⚠ May need 'input' group membership{self.RESET}")
                    print(f"    sudo usermod -a -G input $USER")
                    return "warning"
            except:
                pass
            
            print(f"  {self.GREEN}✓ Linux environment OK{self.RESET}")
            return True
        
        elif self.os_type == "Windows":
            print(f"  {self.BLUE}Windows Detected{self.RESET}")
            
            # Windows usually doesn't require special permissions
            # Check if running with admin rights (not required, just FYI)
            try:
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                
                if is_admin:
                    print(f"  {self.GREEN}✓ Running with Administrator privileges{self.RESET}")
                else:
                    print(f"  {self.BLUE}ℹ Running with standard user privileges (OK){self.RESET}")
            except:
                pass
            
            print(f"  {self.GREEN}✓ Windows environment OK{self.RESET}")
            return True
        
        else:
            print(f"  {self.YELLOW}⚠ Unknown OS: {self.os_type}{self.RESET}")
            print(f"  Proceeding with caution...")
            return "warning"
    
    def configure_security(self):
        """Set up security configurations"""
        print(f"\n{self.BOLD}[5/8] Configuring Security...{self.RESET}")
        
        # Check/create encryption key
        key_file = self.home / ".behavioral_auth_key.bin"
        
        if key_file.exists():
            print(f"  {self.GREEN}✓ Encryption key exists{self.RESET}")
        else:
            print(f"  {self.BLUE}ℹ Creating encryption key...{self.RESET}")
            try:
                from cryptography.fernet import Fernet
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                
                # Set restrictive permissions (Unix-like systems)
                if self.os_type in ["Darwin", "Linux"]:
                    os.chmod(key_file, 0o600)
                    print(f"  {self.GREEN}✓ Encryption key created (chmod 600){self.RESET}")
                else:
                    print(f"  {self.GREEN}✓ Encryption key created{self.RESET}")
            except Exception as e:
                print(f"  {self.YELLOW}⚠ Could not create encryption key: {e}{self.RESET}")
        
        # Check/create user profile
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    user_id = config.get('user_id', 'unknown')
                print(f"  {self.GREEN}✓ User profile exists (ID: {user_id[:8]}...){self.RESET}")
            except:
                print(f"  {self.YELLOW}⚠ User profile corrupted, will recreate{self.RESET}")
        else:
            print(f"  {self.BLUE}ℹ User profile will be created on first run{self.RESET}")
        
        print(f"{self.GREEN}✓ Security configuration complete{self.RESET}")
        return True
    
    def check_disk_space(self):
        """Check available disk space"""
        print(f"\n{self.BOLD}[6/8] Checking Disk Space...{self.RESET}")
        
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.script_dir)
            
            free_gb = free / (1024**3)
            
            print(f"  Available: {free_gb:.2f} GB")
            
            if free_gb < 0.1:  # Less than 100 MB
                print(f"  {self.RED}✗ Insufficient disk space{self.RESET}")
                return False
            elif free_gb < 1.0:  # Less than 1 GB
                print(f"  {self.YELLOW}⚠ Low disk space (< 1 GB){self.RESET}")
                return "warning"
            else:
                print(f"  {self.GREEN}✓ Sufficient disk space{self.RESET}")
                return True
        except Exception as e:
            print(f"  {self.YELLOW}⚠ Could not check disk space: {e}{self.RESET}")
            return "warning"
    
    def check_database(self):
        """Check database file"""
        print(f"\n{self.BOLD}[7/8] Checking Database...{self.RESET}")
        
        db_path = self.script_dir / "behavioral_data.db"
        
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024**2)
            print(f"  {self.GREEN}✓ Database exists ({size_mb:.2f} MB){self.RESET}")
            
            # Try to read it
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                if 'master_features' in tables:
                    cursor.execute("SELECT COUNT(*) FROM master_features")
                    count = cursor.fetchone()[0]
                    print(f"  {self.GREEN}✓ Database valid ({count} samples){self.RESET}")
                else:
                    print(f"  {self.YELLOW}⚠ Database tables missing, will recreate{self.RESET}")
                
                conn.close()
            except Exception as e:
                print(f"  {self.YELLOW}⚠ Database check failed: {e}{self.RESET}")
        else:
            print(f"  {self.BLUE}ℹ Database will be created on first run{self.RESET}")
        
        return True
    
    def perform_health_check(self):
        """Perform quick health check"""
        print(f"\n{self.BOLD}[8/8] Health Check...{self.RESET}")
        
        checks = {
            'Script exists': (self.script_dir / "behavioral_data_collector.py").exists(),
            'Requirements file': (self.script_dir / "requirements.txt").exists(),
            'Home directory writable': os.access(self.home, os.W_OK),
            'Script directory writable': os.access(self.script_dir, os.W_OK),
        }
        
        all_pass = True
        for check, result in checks.items():
            if result:
                print(f"  {self.GREEN}✓{self.RESET} {check}")
            else:
                print(f"  {self.RED}✗{self.RESET} {check}")
                all_pass = False
        
        if all_pass:
            print(f"\n{self.GREEN}✓ All health checks passed{self.RESET}")
        else:
            print(f"\n{self.RED}✗ Some health checks failed{self.RESET}")
        
        return all_pass
    
    def run_data_collector(self):
        """Run the main data collection system"""
        print("\n" + "=" * 80)
        print(f"{self.BOLD}{self.GREEN}✓ BOOTSTRAP COMPLETE - STARTING DATA COLLECTION{self.RESET}")
        print("=" * 80)
        print()
        
        try:
            # Import and run the main collector
            sys.path.insert(0, str(self.script_dir))
            from behavioral_data_collector import main
            main()
        except ImportError as e:
            print(f"{self.RED}✗ Could not import data collector: {e}{self.RESET}")
            return False
        except KeyboardInterrupt:
            print(f"\n{self.YELLOW}Collection interrupted by user{self.RESET}")
            return True
        except Exception as e:
            print(f"{self.RED}✗ Error running data collector: {e}{self.RESET}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_bootstrap(self):
        """Execute full bootstrap process"""
        self.print_header()
        
        # Step 1: Python version
        if not self.check_python_version():
            return False
        
        # Step 2: pip
        if not self.check_pip():
            return False
        
        # Step 3: Dependencies
        if not self.install_dependencies():
            return False
        
        # Step 4: Permissions
        perm_result = self.check_permissions()
        if perm_result == False:
            return False
        elif perm_result == "warning":
            response = input(f"\n{self.YELLOW}Continue anyway? (y/n): {self.RESET}")
            if response.lower() != 'y':
                return False
        
        # Step 5: Security
        if not self.configure_security():
            return False
        
        # Step 6: Disk space
        disk_result = self.check_disk_space()
        if disk_result == False:
            return False
        
        # Step 7: Database
        if not self.check_database():
            return False
        
        # Step 8: Health check
        if not self.perform_health_check():
            response = input(f"\n{self.YELLOW}Some checks failed. Continue? (y/n): {self.RESET}")
            if response.lower() != 'y':
                return False
        
        # Run the collector
        return self.run_data_collector()


def main():
    """Main entry point"""
    bootstrap = IntelligentBootstrap()
    
    try:
        success = bootstrap.run_bootstrap()
        
        if success:
            print(f"\n{bootstrap.GREEN}✓ System shutdown successfully{bootstrap.RESET}")
            sys.exit(0)
        else:
            print(f"\n{bootstrap.RED}✗ Bootstrap failed{bootstrap.RESET}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print(f"\n\n{bootstrap.YELLOW}Bootstrap interrupted by user{bootstrap.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{bootstrap.RED}✗ Critical error: {e}{bootstrap.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

