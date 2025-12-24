// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title SynthGuardConsortium
 * @dev Decentralized fraud prevention consortium for synthetic identity detection
 */
contract SynthGuardConsortium is Ownable {
    
    // Identity record structure
    struct IdentityRecord {
        bytes32 identityHash;      // SHA-256 hash of PII
        uint8 trustScore;          // 0-100 score
        uint256 timestamp;         // When verified
        address verifier;          // Who verified
        bool isFlagged;            // Fraud flag
        string flagReason;         // Why flagged
        uint256 verificationCount; // How many times verified
    }
    
    // Storage
    mapping(bytes32 => IdentityRecord) public identities;
    mapping(address => bool) public authorizedVerifiers;
    
    // Statistics
    uint256 public totalVerifications;
    uint256 public totalFlaggedIdentities;
    
    // Events
    event IdentityVerified(
        bytes32 indexed identityHash, 
        uint8 trustScore, 
        address verifier
    );
    
    event IdentityFlagged(
        bytes32 indexed identityHash, 
        string reason, 
        address flagger
    );
    
    event VerifierAuthorized(address indexed verifier);
    event VerifierRevoked(address indexed verifier);
    
    // Modifiers
    modifier onlyAuthorized() {
        require(
            authorizedVerifiers[msg.sender] || msg.sender == owner(), 
            "Not authorized"
        );
        _;
    }
    
    constructor() Ownable(msg.sender) {
        // Owner is automatically authorized
        authorizedVerifiers[msg.sender] = true;
    }
    
    /**
     * @dev Store or update verified identity
     */
    function storeIdentity(
        bytes32 _identityHash,
        uint8 _trustScore
    ) public onlyAuthorized {
        require(_trustScore <= 100, "Trust score must be 0-100");
        
        IdentityRecord storage record = identities[_identityHash];
        
        if (record.timestamp == 0) {
            // New identity
            identities[_identityHash] = IdentityRecord({
                identityHash: _identityHash,
                trustScore: _trustScore,
                timestamp: block.timestamp,
                verifier: msg.sender,
                isFlagged: false,
                flagReason: "",
                verificationCount: 1
            });
            totalVerifications++;
        } else {
            // Update existing
            record.trustScore = _trustScore;
            record.timestamp = block.timestamp;
            record.verifier = msg.sender;
            record.verificationCount++;
        }
        
        emit IdentityVerified(_identityHash, _trustScore, msg.sender);
    }
    
    /**
     * @dev Flag identity as fraudulent
     */
    function flagIdentity(
        bytes32 _identityHash,
        string memory _reason
    ) public onlyAuthorized {
        require(
            identities[_identityHash].timestamp > 0, 
            "Identity not found"
        );
        
        IdentityRecord storage record = identities[_identityHash];
        
        if (!record.isFlagged) {
            totalFlaggedIdentities++;
        }
        
        record.isFlagged = true;
        record.flagReason = _reason;
        record.trustScore = 0;
        
        emit IdentityFlagged(_identityHash, _reason, msg.sender);
    }
    
    /**
     * @dev Check identity status (public - free to call)
     */
    function checkIdentity(bytes32 _identityHash) 
        public 
        view 
        returns (
            uint8 trustScore, 
            bool isFlagged, 
            string memory flagReason,
            uint256 verificationCount,
            uint256 lastVerified
        ) 
    {
        IdentityRecord memory record = identities[_identityHash];
        return (
            record.trustScore, 
            record.isFlagged, 
            record.flagReason,
            record.verificationCount,
            record.timestamp
        );
    }
    
    /**
     * @dev Check if identity exists in consortium
     */
    function identityExists(bytes32 _identityHash) 
        public 
        view 
        returns (bool) 
    {
        return identities[_identityHash].timestamp > 0;
    }
    
    /**
     * @dev Authorize new verifier (admin only)
     */
    function authorizeVerifier(address _verifier) public onlyOwner {
        authorizedVerifiers[_verifier] = true;
        emit VerifierAuthorized(_verifier);
    }
    
    /**
     * @dev Revoke verifier authorization (admin only)
     */
    function revokeVerifier(address _verifier) public onlyOwner {
        authorizedVerifiers[_verifier] = false;
        emit VerifierRevoked(_verifier);
    }
    
    /**
     * @dev Get consortium statistics
     */
    function getStats() 
        public 
        view 
        returns (uint256 verified, uint256 flagged) 
    {
        return (totalVerifications, totalFlaggedIdentities);
    }
}