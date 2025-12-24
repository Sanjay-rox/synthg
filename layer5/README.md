# Sample Hardhat Project

This project demonstrates a basic Hardhat use case. It comes with a sample contract, a test for that contract, and a Hardhat Ignition module that deploys that contract.

Try running some of the following tasks:

```shell
npx hardhat help
npx hardhat test
REPORT_GAS=true npx hardhat test
npx hardhat node
npx hardhat ignition deploy ./ignition/modules/Lock.js
```

# SynthGuard Layer 5 - Blockchain Verification System

## 🎯 Overview

Layer 5 is the **Blockchain Verification** component of the SynthGuard synthetic identity fraud detection system. It provides a decentralized, immutable consortium ledger for cross-platform fraud prevention.

**Key Innovation:** While AI can create perfect fake documents in minutes, it cannot create years of real digital history stored on an immutable blockchain.

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 5 ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐                                           │
│  │   User Data  │                                           │
│  │  (SSN, Name, │                                           │
│  │     DOB)     │                                           │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────────┐                                    │
│  │ blockchain_service  │  ← Python Backend                  │
│  │       .py           │     - Hashes identity (SHA-256)    │
│  │                     │     - Connects to blockchain       │
│  │  - check_identity() │     - Manages transactions         │
│  │  - store_identity() │                                    │
│  │  - flag_identity()  │                                    │
│  └─────────┬───────────┘                                    │
│            │                                                 │
│            ▼                                                 │
│  ┌─────────────────────┐                                    │
│  │   Web3 Provider     │  ← Alchemy RPC                     │
│  │   (Polygon Amoy)    │                                    │
│  └─────────┬───────────┘                                    │
│            │                                                 │
│            ▼                                                 │
│  ┌─────────────────────────────────────────┐               │
│  │     POLYGON BLOCKCHAIN (Testnet)        │               │
│  │  ┌───────────────────────────────────┐  │               │
│  │  │  SynthGuardConsortium.sol         │  │               │
│  │  │  (Smart Contract)                 │  │               │
│  │  │                                   │  │               │
│  │  │  - identityHash → bytes32         │  │               │
│  │  │  - trustScore → uint8 (0-100)     │  │               │
│  │  │  - isFlagged → bool               │  │               │
│  │  │  - flagReason → string            │  │               │
│  │  │  - verificationCount → uint256    │  │               │
│  │  │  - timestamp → uint256            │  │               │
│  │  └───────────────────────────────────┘  │               │
│  │                                          │               │
│  │  Immutable Storage | Cross-Platform     │               │
│  └─────────────────────────────────────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure & Explanations

### **Root Directory Files**

#### **`hardhat.config.js`** ⚙️

**Purpose:** Configuration file for Hardhat (Ethereum development framework)

**What it does:**

- Defines Solidity compiler version (0.8.20)
- Configures network connections (Polygon Amoy testnet)
- Sets up optimizer for gas efficiency
- Specifies RPC endpoints and chain IDs

**Key configurations:**

```javascript
solidity: "0.8.20"           // Smart contract language version
networks: {
  polygon_amoy: {
    url: process.env.POLYGON_RPC_URL,    // Alchemy endpoint
    chainId: 80002                        // Polygon Amoy testnet
  }
}
```

**When it's used:**

- Compiling contracts: `npx hardhat compile`
- Deploying contracts: `npx hardhat run scripts/deploy.js`

---

#### **`package.json`** 📦

**Purpose:** Node.js project configuration and dependency manifest

**What it does:**

- Lists all JavaScript/Node.js dependencies
- Defines project metadata (name, version)
- Specifies module type (ESM vs CommonJS)

**Key dependencies:**

```json
{
  "hardhat": "^3.1.0", // Blockchain dev framework
  "@nomicfoundation/hardhat-toolbox": "^6.1.0", // Hardhat plugins
  "@openzeppelin/contracts": "^5.2.0", // Secure contract templates
  "dotenv": "^16.4.7" // Environment variables
}
```

**When it's used:**

- Installing dependencies: `npm install`
- Auto-generated when running: `npm init`

---

#### **`package-lock.json`** 🔒

**Purpose:** Locks exact versions of all dependencies (including transitive dependencies)

**What it does:**

- Ensures reproducible builds
- Locks down 300+ sub-dependencies
- Speeds up `npm install`

**Auto-generated:** Do not manually edit this file

---

#### **`.env`** 🔐

**Purpose:** Stores sensitive configuration and secrets

**What it contains:**

```bash
POLYGON_RPC_URL=https://polygon-amoy.g.alchemy.com/v2/YOUR_API_KEY
PRIVATE_KEY=0xYourMetaMaskPrivateKey
```

**Security:**

- ⚠️ **NEVER commit to Git**
- ⚠️ **Contains your wallet private key**
- ✅ Listed in `.gitignore`

**When it's used:** Loaded by both Hardhat and Python scripts to access blockchain

---

#### **`.gitignore`** 🚫

**Purpose:** Tells Git which files/folders to ignore

**What it ignores:**

```
node_modules/        # 300MB+ of dependencies
.env                 # Secrets
cache/               # Temporary Hardhat files
artifacts/           # Compiled contracts (can be regenerated)
*.log                # Log files
```

**Why:** Keeps repository clean and prevents committing secrets

---

#### **`deployment-info.json`** 📝

**Purpose:** Stores deployment details after contract is deployed

**What it contains:**

```json
{
  "network": "Polygon Amoy Testnet",
  "contractAddress": "0x742d35Cc6634C0532925a3b844Bc9e7595f5E4c",
  "deployer": "0xYourWalletAddress",
  "timestamp": "2024-12-17T10:30:00.000Z",
  "blockExplorer": "https://amoy.polygonscan.com/address/0x742d..."
}
```

**When it's created:** Auto-generated by `scripts/deploy.js` after successful deployment

**Why it's important:** Contains the contract address needed for backend configuration

---

### **`contracts/` Directory** 📜

#### **`contracts/SynthGuardConsortium.sol`**

**Purpose:** Smart contract - the "database" on the blockchain

**What it does:**

- Stores identity verification records permanently
- Enforces business logic (who can write, what data is valid)
- Emits events for transparency
- Manages consortium membership

**Key functions:**

```solidity
storeIdentity()      // Store verified identity (costs gas)
flagIdentity()       // Flag as fraudulent (costs gas)
checkIdentity()      // Read identity data (FREE)
getStats()           // Get global statistics (FREE)
```

**Data structure:**

```solidity
struct IdentityRecord {
    bytes32 identityHash;       // SHA-256 hash (privacy)
    uint8 trustScore;           // 0-100 score
    uint256 timestamp;          // When verified
    address verifier;           // Who verified
    bool isFlagged;             // Fraud flag
    string flagReason;          // Why flagged
    uint256 verificationCount;  // Times verified
}
```

**Written in:** Solidity (Ethereum smart contract language)

**Deployed to:** Polygon blockchain at address in `deployment-info.json`

---

### **`scripts/` Directory** 🚀

#### **`scripts/deploy.js`**

**Purpose:** Deployment script that publishes the smart contract to blockchain

**What it does:**

1. Connects to Polygon Amoy testnet
2. Compiles the smart contract
3. Deploys it (sends transaction)
4. Waits for confirmation (2-3 seconds)
5. Saves contract address to `deployment-info.json`
6. Outputs Polygonscan link for verification

**How to run:**

```bash
npx hardhat run scripts/deploy.js --network polygon_amoy
```

**Output example:**

```
🚀 Deploying SynthGuard Consortium to Polygon Amoy...
📝 Deploying with account: 0x742d...5E4c
💰 Account balance: 0.5 MATIC
⏳ Deploying contract...
✅ SynthGuardConsortium deployed to: 0xABC123...
🔍 View on Polygonscan: https://amoy.polygonscan.com/address/0xABC123...
```

**Cost:** ~0.01 MATIC (test MATIC, so free)

---

### **`backend/` Directory** 🐍

#### **`backend/config.py`**

**Purpose:** Configuration file for Python backend

**What it contains:**

```python
# Connection settings
POLYGON_RPC_URL = os.getenv('POLYGON_RPC_URL')   # From .env
CONTRACT_ADDRESS = '0xDeployedContractAddress'    # From deployment
PRIVATE_KEY = os.getenv('PRIVATE_KEY')           # From .env
WALLET_ADDRESS = '0xYourWalletAddress'           # Your MetaMask

# Contract ABI (Application Binary Interface)
CONTRACT_ABI = [...]  # 500+ lines - describes contract functions
```

**The ABI:**

- Tells Python how to interact with smart contract
- Describes function names, parameters, return types
- Copied from `artifacts/contracts/.../SynthGuardConsortium.json`

**Updates needed after deployment:**

1. ✅ Paste contract address from `deployment-info.json`
2. ✅ Paste wallet address from MetaMask
3. ✅ Paste full ABI from compiled artifacts

---

#### **`backend/blockchain_service.py`** 🔧

**Purpose:** Main Python class for blockchain operations

**What it does:**

- Connects Python to blockchain via Web3
- Provides high-level functions for identity operations
- Handles transaction signing and submission
- Manages errors and confirmations

**Key classes/functions:**

**`BlockchainService` class:**

```python
__init__()                    # Initialize Web3 connection
hash_identity()               # Create SHA-256 hash of identity
check_identity()              # Read from blockchain (FREE)
store_verified_identity()     # Write verified user (costs gas)
flag_fraudulent_identity()    # Flag fraud (costs gas)
get_consortium_stats()        # Get global stats (FREE)
```

**How it works:**

1. **Initialize connection:**

```python
bc = BlockchainService()
# Output: ✅ Connected to Polygon - Block: 30724381
```

2. **Check identity (READ - no cost):**

```python
result = bc.check_identity('123-45-6789', 'John Doe', '1990-01-01')
# Returns: {'exists': True, 'trust_score': 95, 'is_flagged': False, ...}
```

3. **Store identity (WRITE - costs gas):**

```python
tx = bc.store_verified_identity('123-45-6789', 'John Doe', '1990-01-01', 95)
# Output: ✅ Identity stored! TX: 0xabc123...
# Returns: {'success': True, 'tx_hash': '0xabc...', 'explorer_url': '...'}
```

4. **Flag fraud (WRITE - costs gas):**

```python
tx = bc.flag_fraudulent_identity('999-88-7777', 'Fake Person', '2024-01-01',
                                  'Synthetic identity detected')
# Output: 🚨 Identity flagged! TX: 0xdef456...
```

**Dependencies:**

- `web3` - Connect to blockchain
- `hashlib` - SHA-256 hashing
- `re` - Regex for SSN normalization

**Transaction flow:**

```
Python → Build transaction → Sign with private key →
Send to blockchain → Wait for confirmation → Return receipt
```

---

#### **`backend/__init__.py`** 📦

**Purpose:** Makes `backend` a proper Python package

**What it contains:** Empty file (or import statements)

**Why it exists:** Allows `from backend.blockchain_service import BlockchainService`

**Without it:** Would get `ModuleNotFoundError: No module named 'backend'`

---

### **`test/` Directory** 🧪

#### **`test_layer5_complete.py`** (in root, should be here)

**Purpose:** Comprehensive test suite for Layer 5

**What it tests:**

**Test Case 1: New Legitimate User**

- Checks blockchain (should not exist)
- Stores with high trust score (95/100)
- Verifies storage successful
- Confirms blockchain transaction

**Test Case 2: Fraudulent User**

- Stores with low score (20/100)
- Flags as fraudulent
- Verifies flagged status
- Checks trust score drops to 0

**Test Case 3: Cross-Platform Detection**

- Simulates fraudster on "different platform"
- Checks blockchain before verification
- Confirms instant blocking

**Test Case 4: Returning User**

- Legitimate user returns
- Blockchain recognizes them
- Shows previous trust score
- Skips expensive verification

**Test Case 5: Multiple Verifications**

- User verified on Platform A
- User re-verified on Platform B
- Verification count increments
- Trust score updates

**Test Case 6: Consortium Statistics**

- Fetches global stats
- Shows total verifications
- Shows total flagged identities
- Calculates fraud rate

**Test Case 7: Hash Consistency**

- Tests SSN format independence ('123-45-6789' vs '123456789')
- Tests name case independence ('John Doe' vs 'JOHN DOE')
- Verifies same person = same hash

**How to run:**

```bash
python test_layer5_complete.py
```

**Expected runtime:** 3-5 minutes (blockchain confirmations take time)

**Success criteria:** 7/7 tests passed

---

### **`artifacts/` Directory** 📦

**Purpose:** Auto-generated compiled contract files

**Created by:** `npx hardhat compile`

**Structure:**

```
artifacts/
└── contracts/
    └── SynthGuardConsortium.sol/
        ├── SynthGuardConsortium.json     # Main artifact
        └── SynthGuardConsortium.dbg.json # Debug info
```

**`SynthGuardConsortium.json` contains:**

- **ABI:** Function signatures (needed by Python)
- **Bytecode:** Compiled contract code (deployed to blockchain)
- **Metadata:** Source code mappings

**Can be deleted?** Yes - regenerate with `npx hardhat compile`

---

### **`cache/` Directory** 💾

**Purpose:** Hardhat compilation cache for faster rebuilds

**Contains:** `solidity-files-cache.json`

**What it does:** Tracks which files changed to avoid recompiling everything

**Can be deleted?** Yes - auto-regenerates

---

### **`node_modules/` Directory** 📚

**Purpose:** All JavaScript/Node.js dependencies

**Size:** 300+ MB, 15,000+ files

**Contains:**

- Hardhat framework
- OpenZeppelin contracts
- Ethers.js (Ethereum library)
- Web3 utilities
- 300+ sub-dependencies

**Can be deleted?** Yes - reinstall with `npm install`

---

## 🔄 Complete Workflow

### **1. Initial Setup**

```bash
npm install                    # Install Node.js dependencies
pip install web3 python-dotenv # Install Python dependencies
```

### **2. Configuration**

```bash
# Edit .env file
POLYGON_RPC_URL=https://polygon-amoy.g.alchemy.com/v2/YOUR_KEY
PRIVATE_KEY=0xYourPrivateKey
```

### **3. Compile Contract**

```bash
npx hardhat compile
# Creates: artifacts/contracts/SynthGuardConsortium.sol/SynthGuardConsortium.json
```

### **4. Deploy Contract**

```bash
npx hardhat run scripts/deploy.js --network polygon_amoy
# Creates: deployment-info.json
# Output: Contract address
```

### **5. Configure Backend**

```python
# Update backend/config.py
CONTRACT_ADDRESS = '0xFromDeploymentInfo'
WALLET_ADDRESS = '0xYourMetaMaskAddress'
CONTRACT_ABI = [...]  # Copy from artifacts
```

### **6. Test**

```bash
python test_layer5_complete.py
# Runs 7 test cases
# Expected: 7/7 passed
```

### **7. Use in Application**

```python
from backend.blockchain_service import BlockchainService

bc = BlockchainService()
result = bc.check_identity('123-45-6789', 'John Doe', '1990-01-01')
```

---

## 🔐 Security Notes

### **Private Key Security**

- ⚠️ **NEVER share your private key**
- ⚠️ **NEVER commit .env to Git**
- ✅ `.env` is in `.gitignore`
- ✅ Use separate wallet for testnet vs mainnet

### **Data Privacy**

- ✅ Only hashed identities stored on blockchain
- ✅ SHA-256 is one-way (cannot reverse)
- ✅ Raw PII never touches blockchain
- ✅ GDPR compliant approach

### **Access Control**

- ✅ Only authorized verifiers can write to blockchain
- ✅ Anyone can read (transparency)
- ✅ Owner can authorize/revoke verifiers

---

## 📊 Gas Costs

| Operation           | Gas Used   | Cost (MATIC) | Cost (USD) |
| ------------------- | ---------- | ------------ | ---------- |
| **Deploy Contract** | ~2,000,000 | 0.01         | ~$0.01     |
| **Store Identity**  | ~150,000   | 0.0007       | ~$0.0007   |
| **Flag Identity**   | ~120,000   | 0.0006       | ~$0.0006   |
| **Check Identity**  | 0          | FREE         | FREE       |
| **Get Stats**       | 0          | FREE         | FREE       |

**Note:** Testnet uses free test MATIC. Mainnet uses real MATIC (~$1/MATIC).

---

## 🌐 Network Information

### **Polygon Amoy Testnet** (Current)

- **Chain ID:** 80002
- **RPC:** https://rpc-amoy.polygon.technology/
- **Explorer:** https://amoy.polygonscan.com/
- **Faucet:** https://faucet.polygon.technology/
- **Currency:** Test MATIC (free)

### **Polygon Mainnet** (Production)

- **Chain ID:** 137
- **RPC:** https://polygon-mainnet.g.alchemy.com/v2/...
- **Explorer:** https://polygonscan.com/
- **Currency:** Real MATIC (~$1 each)

**To switch:** Change 3 lines in `hardhat.config.js` and redeploy

---

## 🐛 Troubleshooting

### **"Failed to connect to Polygon"**

- ✅ Check `POLYGON_RPC_URL` in `.env`
- ✅ Verify Alchemy API key is valid
- ✅ Check internet connection

### **"Insufficient funds"**

- ✅ Get test MATIC from faucet
- ✅ Check wallet has 0.5+ MATIC

### **"Contract address not found"**

- ✅ Update `CONTRACT_ADDRESS` in `config.py`
- ✅ Use address from `deployment-info.json`

### **"Module not found"**

- ✅ Run `npm install` for Node.js
- ✅ Run `pip install web3 python-dotenv` for Python
- ✅ Create `backend/__init__.py` (empty file)

### **"rawTransaction attribute error"**

- ✅ Use `raw_transaction` (underscore) not `rawTransaction`
- ✅ Update to latest Web3.py: `pip install --upgrade web3`

---

## 📈 Performance

- **Blockchain reads:** Instant (< 100ms)
- **Blockchain writes:** 2-5 seconds (wait for block confirmation)
- **Contract deployment:** 10-15 seconds
- **Test suite:** 3-5 minutes (due to multiple transactions)

---

## 🎯 Production Deployment

### **Checklist for Mainnet:**

- [ ] Audit smart contract (use OpenZeppelin Defender)
- [ ] Use separate wallet for production
- [ ] Change `chainId: 137` in `hardhat.config.js`
- [ ] Update RPC to mainnet endpoint
- [ ] Get real MATIC for gas fees
- [ ] Deploy with `--network polygon_mainnet`
- [ ] Update `backend/config.py` with new contract address
- [ ] Test thoroughly on mainnet before production use
- [ ] Implement monitoring and alerts
- [ ] Set up multi-sig wallet for contract ownership

---

## 📚 Additional Resources

- **Hardhat Documentation:** https://hardhat.org/docs
- **OpenZeppelin Contracts:** https://docs.openzeppelin.com/contracts
- **Web3.py Documentation:** https://web3py.readthedocs.io/
- **Polygon Documentation:** https://docs.polygon.technology/
- **Solidity Documentation:** https://docs.soliditylang.org/

---

## 🤝 Support

For issues or questions:

1. Check this README
2. Review error messages carefully
3. Check blockchain explorer (Polygonscan)
4. Verify configuration in `.env` and `config.py`

---

## 📜 License

This is a hackathon project for PEC Hacks 3.0 - FinTech Track.

---

**Last Updated:** December 2024  
**Version:** 1.0.0  
**Network:** Polygon Amoy Testnet
