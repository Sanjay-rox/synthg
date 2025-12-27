# Project Utilities

Utility scripts for project management and distribution.

---

## 📦 Smart Zipper

**Purpose:** Create professional ZIP archives with optional SHA256 checksums.

**Features:**
- ✅ Cross-platform (macOS, Linux, Windows)
- ✅ Automatic exclusion of unwanted files (.git, __pycache__, etc.)
- ✅ Optional SHA256 checksum generation
- ✅ Provides platform-specific unzip instructions
- ✅ Customizable compression levels
- ✅ Intelligent file filtering

### Quick Start

```bash
# Zip current directory
python3 smart_zipper.py

# Zip specific project
python3 smart_zipper.py /path/to/project

# With checksum verification file
python3 smart_zipper.py --with-checksum

# Custom output name
python3 smart_zipper.py --name myproject-v1.0
```

### Usage Examples

```bash
# Zip parent directory (the main project)
cd tools
python3 smart_zipper.py .. --name behavioral-auth-v1.0 --with-checksum -y

# Zip with minimal exclusions
python3 smart_zipper.py --include-all

# Zip with additional exclusions
python3 smart_zipper.py --exclude "*.db" "*.csv" "*.log"

# Maximum compression
python3 smart_zipper.py --compression 9

# No compression (faster, larger file)
python3 smart_zipper.py --compression 0

# Auto-confirm (no prompts)
python3 smart_zipper.py -y
```

### Default Exclusions

The script automatically excludes:
- Version control: `.git`, `.svn`, `.gitignore`
- Python: `__pycache__`, `*.pyc`, `venv`, `*.egg-info`
- IDE: `.vscode`, `.idea`, `.DS_Store`
- Build artifacts: `dist`, `build`, `*.o`, `*.so`
- Data files: `*.db`, `*.sqlite`, `*.log`
- Archives: `*.zip`, `*.tar.gz`

### Command-Line Options

```
positional arguments:
  path                  Path to directory to zip (default: current directory)

optional arguments:
  -h, --help            Show help message
  --name NAME, -n NAME  Custom output filename (without .zip)
  --output DIR, -o DIR  Output directory for ZIP file
  --with-checksum, -c   Generate SHA256 checksum file
  --compression N, -z N Compression level 0-9 (default: 9)
  --exclude PATTERNS    Additional patterns to exclude
  --include-all, -a     Minimal exclusions only
  --no-exclude-defaults Don't use default exclusion patterns
  --yes, -y             Auto-confirm (no prompts)
  --verbose, -v         Verbose output
  --version             Show version
```

### Output

Creates two files when using `--with-checksum`:
- `projectname-YYYYMMDD.zip` - The ZIP archive
- `projectname-YYYYMMDD.zip.sha256` - Checksum file

Provides platform-specific unzip instructions for:
- macOS/Linux terminal
- Windows PowerShell
- Windows File Explorer

---

## 🎯 Use Cases

**For Distribution:**
```bash
# Create release package with verification
cd DataCollection/tools
python3 smart_zipper.py .. --name behavioral-auth-v1.0 --with-checksum -y
```

**For Backup:**
```bash
# Quick backup without checksum
python3 smart_zipper.py /path/to/project --name backup-$(date +%Y%m%d) -y
```

**For Sharing:**
```bash
# Include checksum for integrity verification
python3 smart_zipper.py --with-checksum --yes
```

---

## 🔒 Security Features

- **SHA256 Checksum:** Verify file integrity after transfer
- **Automatic Exclusion:** Sensitive files (*.db, *.log) excluded by default
- **Cross-Platform:** Verification instructions for all platforms
- **Tamper Detection:** Any modification changes the checksum

---

## 💡 Tips

- Always use `--with-checksum` for distribution to others
- Review excluded files with `--verbose` before creating archive
- Use `--compression 9` (default) for maximum compression
- Test extraction after creating to ensure integrity
- Share both .zip and .sha256 files for verification

---

## 📋 Example Workflow

```bash
# 1. Navigate to tools directory
cd DataCollection/tools

# 2. Create distribution package
python3 smart_zipper.py .. \
  --name behavioral-auth-v1.0 \
  --with-checksum \
  --yes

# 3. Files created:
#    - behavioral-auth-v1.0.zip
#    - behavioral-auth-v1.0.zip.sha256

# 4. Unzip instructions are automatically displayed
```

---

**Version:** 1.0.0  
**License:** Same as main project  
**Platform:** Cross-platform (Python 3.7+)

