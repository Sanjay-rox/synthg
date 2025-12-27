import os
from dotenv import load_dotenv

load_dotenv()

# Blockchain configuration
POLYGON_RPC_URL = os.getenv('POLYGON_RPC_URL')
CONTRACT_ADDRESS = "0xC8b2c748CdDF1980f2c75C39860d98a5691bdb81"  # ✅ STRING
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
WALLET_ADDRESS = "0x91F8c6a57e9363E125f3cbB947095a0F5602235C"    # ✅ STRING

# Contract ABI (copy from artifacts after compilation)
CONTRACT_ABI = [
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "owner",
          "type": "address"
        }
      ],
      "name": "OwnableInvalidOwner",
      "type": "error"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "account",
          "type": "address"
        }
      ],
      "name": "OwnableUnauthorizedAccount",
      "type": "error"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "bytes32",
          "name": "identityHash",
          "type": "bytes32"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "reason",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "address",
          "name": "flagger",
          "type": "address"
        }
      ],
      "name": "IdentityFlagged",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "bytes32",
          "name": "identityHash",
          "type": "bytes32"
        },
        {
          "indexed": False,
          "internalType": "uint8",
          "name": "trustScore",
          "type": "uint8"
        },
        {
          "indexed": False,
          "internalType": "address",
          "name": "verifier",
          "type": "address"
        }
      ],
      "name": "IdentityVerified",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "address",
          "name": "previousOwner",
          "type": "address"
        },
        {
          "indexed": True,
          "internalType": "address",
          "name": "newOwner",
          "type": "address"
        }
      ],
      "name": "OwnershipTransferred",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "address",
          "name": "verifier",
          "type": "address"
        }
      ],
      "name": "VerifierAuthorized",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "address",
          "name": "verifier",
          "type": "address"
        }
      ],
      "name": "VerifierRevoked",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_verifier",
          "type": "address"
        }
      ],
      "name": "authorizeVerifier",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "authorizedVerifiers",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "_identityHash",
          "type": "bytes32"
        }
      ],
      "name": "checkIdentity",
      "outputs": [
        {
          "internalType": "uint8",
          "name": "trustScore",
          "type": "uint8"
        },
        {
          "internalType": "bool",
          "name": "isFlagged",
          "type": "bool"
        },
        {
          "internalType": "string",
          "name": "flagReason",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "verificationCount",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "lastVerified",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "_identityHash",
          "type": "bytes32"
        },
        {
          "internalType": "string",
          "name": "_reason",
          "type": "string"
        }
      ],
      "name": "flagIdentity",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getStats",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "verified",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "flagged",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "",
          "type": "bytes32"
        }
      ],
      "name": "identities",
      "outputs": [
        {
          "internalType": "bytes32",
          "name": "identityHash",
          "type": "bytes32"
        },
        {
          "internalType": "uint8",
          "name": "trustScore",
          "type": "uint8"
        },
        {
          "internalType": "uint256",
          "name": "timestamp",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "verifier",
          "type": "address"
        },
        {
          "internalType": "bool",
          "name": "isFlagged",
          "type": "bool"
        },
        {
          "internalType": "string",
          "name": "flagReason",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "verificationCount",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "_identityHash",
          "type": "bytes32"
        }
      ],
      "name": "identityExists",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "owner",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "renounceOwnership",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_verifier",
          "type": "address"
        }
      ],
      "name": "revokeVerifier",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "_identityHash",
          "type": "bytes32"
        },
        {
          "internalType": "uint8",
          "name": "_trustScore",
          "type": "uint8"
        }
      ],
      "name": "storeIdentity",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "totalFlaggedIdentities",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "totalVerifications",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "newOwner",
          "type": "address"
        }
      ],
      "name": "transferOwnership",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
]