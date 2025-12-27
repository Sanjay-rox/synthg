from web3 import Web3
import hashlib
import json
import re
from datetime import datetime

# Smart import - works both ways
try:
    from backend.config import (
        POLYGON_RPC_URL, 
        CONTRACT_ADDRESS, 
        CONTRACT_ABI, 
        PRIVATE_KEY, 
        WALLET_ADDRESS
    )
except ImportError:
    from config import (
        POLYGON_RPC_URL, 
        CONTRACT_ADDRESS, 
        CONTRACT_ABI, 
        PRIVATE_KEY, 
        WALLET_ADDRESS
    )

class BlockchainService:
    # ✅ CONFIGURABLE: Baseline score for first-time users
    BASELINE_TRUST_SCORE = 50  # Change to 45 if you prefer
    
    def __init__(self, baseline_score=None):
        """
        Initialize Web3 connection
        
        Args:
            baseline_score: Override baseline score for first-time users (default: 50)
        """
        self.w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))
        
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Polygon network")
        
        print(f"✅ Connected to Polygon - Block: {self.w3.eth.block_number}")
        
        # Load contract
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACT_ADDRESS),
            abi=CONTRACT_ABI
        )
        
        self.wallet_address = Web3.to_checksum_address(WALLET_ADDRESS)
        self.private_key = PRIVATE_KEY
        
        # Set baseline score
        self.baseline_score = baseline_score if baseline_score is not None else self.BASELINE_TRUST_SCORE
        print(f"📊 Baseline score for first-time users: {self.baseline_score}")
    
    def hash_identity(self, ssn, name, dob):
        """
        Create privacy-preserving hash of identity
        Args:
            ssn: Social Security Number or Aadhaar
            name: Full name
            dob: Date of birth (YYYY-MM-DD)
        Returns:
            bytes32 hash (hex string)
        """
        # Normalize inputs
        ssn_clean = re.sub(r'[^0-9]', '', ssn)
        name_clean = name.lower().strip()
        dob_clean = dob.strip()
        
        # Combine and hash
        identity_string = f"{ssn_clean}{name_clean}{dob_clean}"
        hash_bytes = hashlib.sha256(identity_string.encode()).digest()
        return '0x' + hash_bytes.hex()
    
    def check_identity(self, ssn, name, dob):
        """
        Check if identity exists in consortium (FREE - no gas)
        
        Returns: dict with trust_score, is_flagged, flag_reason
        
        Scoring logic:
        - Exists with history: Return actual blockchain score (0-100)
        - First-time user: Return baseline score (default: 50)
        - Blockchain error: Return baseline score (default: 50)
        """
        identity_hash = self.hash_identity(ssn, name, dob)
        
        try:
            # Call contract (read-only, no transaction)
            result = self.contract.functions.checkIdentity(identity_hash).call()
            
            # Check if identity exists
            exists = result[3] > 0  # verificationCount > 0
            
            if exists:
                # Identity has blockchain history - return actual score
                age_days = None
                if result[4] > 0:  # lastVerified timestamp
                    age_days = int((datetime.now().timestamp() - result[4]) / 86400)
                
                return {
                    'exists': True,
                    'trust_score': int(result[0]),  # Actual blockchain score
                    'is_flagged': result[1],
                    'flag_reason': result[2],
                    'verification_count': int(result[3]),
                    'last_verified': datetime.fromtimestamp(result[4]).isoformat() if result[4] > 0 else None,
                    'age_days': age_days,
                    'identity_hash': identity_hash
                }
            else:
                # ✅ First-time user - return baseline score
                return {
                    'exists': False,
                    'trust_score': self.baseline_score,  # Neutral baseline
                    'is_flagged': False,
                    'flag_reason': '',
                    'verification_count': 0,
                    'last_verified': None,
                    'age_days': None,
                    'identity_hash': identity_hash
                }
                
        except Exception as e:
            print(f"❌ Error checking identity: {e}")
            # Return baseline score on error
            return {
                'exists': False,
                'trust_score': self.baseline_score,
                'is_flagged': False,
                'flag_reason': '',
                'verification_count': 0,
                'last_verified': None,
                'age_days': None,
                'identity_hash': identity_hash
            }
    
    def store_verified_identity(self, ssn, name, dob, trust_score):
        """
        Store verified identity on blockchain (COSTS GAS)
        Args:
            ssn, name, dob: Identity data
            trust_score: 0-100 score from Layers 1-4
        Returns: Transaction receipt
        """
        identity_hash = self.hash_identity(ssn, name, dob)
        
        try:
            # Build transaction
            tx = self.contract.functions.storeIdentity(
                identity_hash,
                trust_score
            ).build_transaction({
                'from': self.wallet_address,
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            print(f"⏳ Transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            print(f"✅ Identity stored on blockchain!")
            print(f"🔗 TX: https://amoy.polygonscan.com/tx/{tx_hash.hex()}")
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'gas_used': receipt['gasUsed'],
                'block_number': receipt['blockNumber'],
                'explorer_url': f"https://amoy.polygonscan.com/tx/{tx_hash.hex()}"
            }
            
        except Exception as e:
            print(f"❌ Error storing identity: {e}")
            return {'success': False, 'error': str(e)}
    
    def flag_fraudulent_identity(self, ssn, name, dob, reason):
        """
        Flag identity as fraudulent (COSTS GAS)
        """
        identity_hash = self.hash_identity(ssn, name, dob)
        
        try:
            tx = self.contract.functions.flagIdentity(
                identity_hash,
                reason
            ).build_transaction({
                'from': self.wallet_address,
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            print(f"⏳ Flagging identity...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            print(f"🚨 Identity flagged as fraudulent!")
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'explorer_url': f"https://amoy.polygonscan.com/tx/{tx_hash.hex()}"
            }
            
        except Exception as e:
            print(f"❌ Error flagging identity: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_consortium_stats(self):
        """Get global consortium statistics (FREE)"""
        try:
            stats = self.contract.functions.getStats().call()
            return {
                'total_verifications': stats[0],
                'total_flagged': stats[1]
            }
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return None


# Demo/Testing function
def test_blockchain_layer():
    """Test the blockchain layer"""
    print("=" * 60)
    print("🧪 TESTING SYNTHGUARD BLOCKCHAIN LAYER")
    print("=" * 60)
    
    # You can customize baseline score here
    bc = BlockchainService(baseline_score=50)  # Or use 45
    
    # Test identity
    test_ssn = "123-45-6789"
    test_name = "John Doe"
    test_dob = "1990-01-01"
    
    print("\n1️⃣ Checking if identity exists...")
    result = bc.check_identity(test_ssn, test_name, test_dob)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if not result['exists']:
        print("\n2️⃣ Storing verified identity (trust score: 95)...")
        tx_result = bc.store_verified_identity(test_ssn, test_name, test_dob, 95)
        print(f"Result: {json.dumps(tx_result, indent=2)}")
    
    print("\n3️⃣ Checking identity again...")
    result = bc.check_identity(test_ssn, test_name, test_dob)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    print("\n4️⃣ Testing first-time user (no history)...")
    result_new = bc.check_identity("999888777", "New User", "1995-01-01")
    print(f"First-time user score: {result_new['trust_score']} (baseline)")
    
    print("\n5️⃣ Getting consortium stats...")
    stats = bc.get_consortium_stats()
    print(f"Stats: {json.dumps(stats, indent=2)}")
    
    print("\n✅ TEST COMPLETE")

if __name__ == "__main__":
    test_blockchain_layer()