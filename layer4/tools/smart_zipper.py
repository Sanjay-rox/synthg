#!/usr/bin/env python3
"""
Smart Project Zipper - Cross-Platform Archive Creator
======================================================
Creates professional ZIP archives with optional integrity checksums.
Automatically excludes common unwanted files and provides unzip instructions.

Usage:
    python3 smart_zipper.py [path] [options]
    
Examples:
    python3 smart_zipper.py                    # Zip current directory
    python3 smart_zipper.py /path/to/project   # Zip specific project
    python3 smart_zipper.py --with-checksum    # Include SHA256 checksum
    python3 smart_zipper.py --name myproject   # Custom output name
"""

import os
import sys
import platform
import hashlib
import zipfile
from pathlib import Path
from datetime import datetime
import argparse


class SmartZipper:
    """Intelligent cross-platform project archiver"""
    
    def __init__(self):
        self.os_type = platform.system()
        self.version = "1.0.0"
        
        # Common files/folders to exclude
        self.default_excludes = {
            # Version control
            '.git', '.svn', '.hg', '.gitignore', '.gitattributes',
            
            # Python
            '__pycache__', '*.pyc', '*.pyo', '*.pyd', '.Python',
            'venv', 'env', '.venv', 'ENV', 'virtualenv',
            '*.egg-info', 'dist', 'build', '.eggs',
            '.pytest_cache', '.coverage', 'htmlcov',
            
            # IDE
            '.vscode', '.idea', '*.swp', '*.swo', '*~',
            '.DS_Store', 'Thumbs.db', 'desktop.ini',
            
            # Node
            'node_modules', 'package-lock.json',
            
            # Build artifacts
            '*.o', '*.so', '*.dylib', '*.dll', '*.exe',
            
            # Data files (usually shouldn't be in project distribution)
            '*.db', '*.sqlite', '*.sqlite3',
            '*.log', '*.pid',
            
            # Archives
            '*.zip', '*.tar', '*.tar.gz', '*.tgz', '*.rar',
            
            # OS specific
            '.Spotlight-V100', '.Trashes', '.fseventsd',
            '$RECYCLE.BIN', 'System Volume Information'
        }
    
    def print_header(self):
        """Print program header"""
        print("=" * 70)
        print(f"  SMART PROJECT ZIPPER v{self.version}")
        print(f"  Cross-Platform Archive Creator")
        print("=" * 70)
        print()
    
    def should_exclude(self, path, excludes):
        """Check if path should be excluded"""
        name = os.path.basename(path)
        
        # Check exact matches
        if name in excludes:
            return True
        
        # Check wildcards
        for pattern in excludes:
            if '*' in pattern:
                # Simple wildcard matching
                if pattern.startswith('*'):
                    if name.endswith(pattern[1:]):
                        return True
                elif pattern.endswith('*'):
                    if name.startswith(pattern[:-1]):
                        return True
        
        # Check if any parent directory is excluded
        parts = Path(path).parts
        for part in parts:
            if part in excludes:
                return True
        
        return False
    
    def get_files_to_zip(self, source_dir, excludes):
        """Get list of files to include in ZIP"""
        files_to_zip = []
        
        source_path = Path(source_dir).resolve()
        
        for root, dirs, files in os.walk(source_path):
            # Remove excluded directories from traversal
            dirs[:] = [d for d in dirs if not self.should_exclude(
                os.path.join(root, d), excludes
            )]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                if not self.should_exclude(file_path, excludes):
                    # Get relative path from source directory
                    rel_path = os.path.relpath(file_path, source_path)
                    files_to_zip.append((file_path, rel_path))
        
        return files_to_zip
    
    def create_zip(self, source_dir, output_name, excludes, compression_level=9):
        """Create ZIP archive"""
        print(f"📦 Creating ZIP archive...")
        print(f"   Source: {source_dir}")
        print(f"   Output: {output_name}")
        print()
        
        # Get files to zip
        files_to_zip = self.get_files_to_zip(source_dir, excludes)
        
        if not files_to_zip:
            print("❌ No files found to zip!")
            return None
        
        print(f"   Found {len(files_to_zip)} files to archive")
        print()
        
        # Create ZIP with compression
        compression = zipfile.ZIP_DEFLATED if compression_level > 0 else zipfile.ZIP_STORED
        
        try:
            with zipfile.ZipFile(output_name, 'w', compression, compresslevel=compression_level) as zipf:
                for file_path, arc_name in files_to_zip:
                    try:
                        zipf.write(file_path, arc_name)
                        print(f"   ✓ {arc_name}")
                    except Exception as e:
                        print(f"   ⚠ Skipped {arc_name}: {e}")
            
            # Get file size
            size_bytes = os.path.getsize(output_name)
            size_mb = size_bytes / (1024 * 1024)
            
            print()
            print(f"✅ ZIP created successfully!")
            print(f"   File: {output_name}")
            print(f"   Size: {size_mb:.2f} MB ({size_bytes:,} bytes)")
            print()
            
            return output_name
        
        except Exception as e:
            print(f"❌ Error creating ZIP: {e}")
            return None
    
    def generate_checksum(self, file_path):
        """Generate SHA256 checksum for file"""
        print(f"🔒 Generating SHA256 checksum...")
        
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                # Read in chunks for memory efficiency
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            checksum = sha256_hash.hexdigest()
            
            # Save to file
            checksum_file = f"{file_path}.sha256"
            with open(checksum_file, 'w') as f:
                f.write(f"# SHA256 Checksum\n")
                f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# File: {os.path.basename(file_path)}\n")
                f.write(f"\n")
                f.write(f"{checksum}  {os.path.basename(file_path)}\n")
            
            print(f"   Checksum: {checksum}")
            print(f"   Saved to: {checksum_file}")
            print()
            
            return checksum, checksum_file
        
        except Exception as e:
            print(f"❌ Error generating checksum: {e}")
            return None, None
    
    def print_unzip_instructions(self, zip_file, checksum_file=None):
        """Print platform-specific unzip instructions"""
        print("=" * 70)
        print("  HOW TO UNZIP")
        print("=" * 70)
        print()
        
        zip_name = os.path.basename(zip_file)
        
        # Verification instructions (if checksum exists)
        if checksum_file:
            print("📋 STEP 1: VERIFY INTEGRITY (Recommended)")
            print("-" * 70)
            print()
            
            if self.os_type in ["Darwin", "Linux"]:
                print("On macOS/Linux:")
                print(f"  sha256sum -c {os.path.basename(checksum_file)}")
                print()
                print("Alternative (macOS):")
                print(f"  shasum -a 256 -c {os.path.basename(checksum_file)}")
            
            elif self.os_type == "Windows":
                print("On Windows (PowerShell):")
                print(f"  Get-FileHash {zip_name} -Algorithm SHA256")
                print(f"  # Compare output with content of {os.path.basename(checksum_file)}")
                print()
                print("Or using certutil:")
                print(f"  certutil -hashfile {zip_name} SHA256")
            
            else:
                print(f"Check the content of {os.path.basename(checksum_file)} and compare")
            
            print()
            print("✅ If checksums match, proceed to extraction.")
            print("❌ If checksums DON'T match, DO NOT EXTRACT (file may be corrupted).")
            print()
        
        # Extraction instructions
        step_num = 2 if checksum_file else 1
        print(f"📦 STEP {step_num}: EXTRACT FILES")
        print("-" * 70)
        print()
        
        if self.os_type in ["Darwin", "Linux"]:
            print("On macOS/Linux:")
            print(f"  unzip {zip_name}")
            print()
            print("Extract to specific directory:")
            print(f"  unzip {zip_name} -d /path/to/directory")
            print()
            print("List contents without extracting:")
            print(f"  unzip -l {zip_name}")
        
        elif self.os_type == "Windows":
            print("On Windows:")
            print()
            print("Method 1 - File Explorer:")
            print(f"  1. Right-click on {zip_name}")
            print("  2. Select 'Extract All...'")
            print("  3. Choose destination folder")
            print("  4. Click 'Extract'")
            print()
            print("Method 2 - PowerShell:")
            print(f"  Expand-Archive -Path {zip_name} -DestinationPath .\\extracted")
            print()
            print("Method 3 - Command Prompt (with 7-Zip installed):")
            print(f"  7z x {zip_name}")
        
        else:
            print("Using command line:")
            print(f"  unzip {zip_name}")
            print()
            print("Or use your system's archive manager (GUI)")
        
        print()
        print("=" * 70)
        print()
        
        # Cross-platform tips
        print("💡 TIPS:")
        print("-" * 70)
        print("• Always verify checksum before extracting (if provided)")
        print("• Extract to a new directory to avoid file conflicts")
        print("• On Unix systems, file permissions are preserved")
        print("• Large files may take time to extract")
        print("• If extraction fails, try re-downloading the ZIP file")
        print()
        print("=" * 70)
    
    def run(self, args):
        """Main execution"""
        self.print_header()
        
        # Determine source directory
        if args.path:
            source_dir = Path(args.path).resolve()
        else:
            source_dir = Path.cwd()
        
        if not source_dir.exists():
            print(f"❌ Error: Path does not exist: {source_dir}")
            return 1
        
        if not source_dir.is_dir():
            print(f"❌ Error: Path is not a directory: {source_dir}")
            return 1
        
        # Determine output name
        if args.name:
            output_name = args.name
            if not output_name.endswith('.zip'):
                output_name += '.zip'
        else:
            # Use directory name + timestamp
            dir_name = source_dir.name
            timestamp = datetime.now().strftime('%Y%m%d')
            output_name = f"{dir_name}-{timestamp}.zip"
        
        # Handle output path
        if args.output:
            output_path = Path(args.output) / output_name
        else:
            output_path = Path.cwd() / output_name
        
        output_path = output_path.resolve()
        
        # Prepare excludes
        excludes = self.default_excludes.copy()
        
        if args.include_all:
            # Minimal excludes
            excludes = {'.git', '__pycache__', '*.pyc'}
        
        if args.exclude:
            excludes.update(args.exclude)
        
        if args.no_exclude_defaults:
            excludes = set(args.exclude) if args.exclude else set()
        
        # Show configuration
        print(f"⚙️  Configuration:")
        print(f"   Source Directory: {source_dir}")
        print(f"   Output File: {output_path}")
        print(f"   Compression Level: {args.compression}")
        print(f"   Generate Checksum: {'Yes' if args.with_checksum else 'No'}")
        print(f"   Excluded Patterns: {len(excludes)} patterns")
        print()
        
        if args.verbose:
            print(f"   Exclude patterns:")
            for pattern in sorted(excludes):
                print(f"     - {pattern}")
            print()
        
        # Confirm if not auto-confirm
        if not args.yes:
            response = input("Proceed with ZIP creation? (y/n): ")
            if response.lower() not in ['y', 'yes']:
                print("Cancelled.")
                return 0
            print()
        
        # Create ZIP
        zip_file = self.create_zip(
            source_dir, 
            output_path, 
            excludes,
            args.compression
        )
        
        if not zip_file:
            return 1
        
        # Generate checksum if requested
        checksum_file = None
        if args.with_checksum:
            _, checksum_file = self.generate_checksum(zip_file)
        
        # Print instructions
        self.print_unzip_instructions(zip_file, checksum_file)
        
        print(f"✅ All done! Your archive is ready.")
        print()
        
        return 0


def main():
    """Entry point"""
    parser = argparse.ArgumentParser(
        description='Smart Project Zipper - Cross-platform archive creator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 smart_zipper.py                        # Zip current directory
  python3 smart_zipper.py /path/to/project       # Zip specific directory
  python3 smart_zipper.py --with-checksum        # Include SHA256 checksum
  python3 smart_zipper.py --name myproject-v1.0  # Custom output name
  python3 smart_zipper.py --exclude "*.db" "*.log"  # Additional exclusions
  python3 smart_zipper.py --include-all          # Minimal exclusions
  python3 smart_zipper.py -y                     # Auto-confirm
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        help='Path to directory to zip (default: current directory)'
    )
    
    parser.add_argument(
        '--name', '-n',
        help='Output ZIP filename (without .zip extension)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output directory for ZIP file (default: current directory)'
    )
    
    parser.add_argument(
        '--with-checksum', '-c',
        action='store_true',
        help='Generate SHA256 checksum file'
    )
    
    parser.add_argument(
        '--compression', '-z',
        type=int,
        default=9,
        choices=range(0, 10),
        help='Compression level 0-9 (default: 9, highest)'
    )
    
    parser.add_argument(
        '--exclude', '-e',
        nargs='+',
        help='Additional patterns to exclude'
    )
    
    parser.add_argument(
        '--include-all', '-a',
        action='store_true',
        help='Minimal exclusions (only .git, __pycache__, .pyc)'
    )
    
    parser.add_argument(
        '--no-exclude-defaults',
        action='store_true',
        help='Don\'t use default exclusion patterns'
    )
    
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Auto-confirm (no prompts)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Smart Zipper 1.0.0'
    )
    
    args = parser.parse_args()
    
    zipper = SmartZipper()
    
    try:
        exit_code = zipper.run(args)
        sys.exit(exit_code)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

