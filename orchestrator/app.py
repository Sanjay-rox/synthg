"""
SynthGuard Orchestrator - Main Application
==========================================
FastAPI server that orchestrates all 5 layers of identity verification
"""

import os
import asyncio
import time
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from models import (
    VerificationRequest, VerificationResponse, HealthResponse, ErrorResponse,
    VerdictEnum, LayerStatusEnum
)
from layer_clients import OrchestratorClient
from scoring_engine import ScoringEngine
from utils import setup_logger, generate_verification_id, get_timestamp, format_error_response


# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger(__name__, log_file=os.getenv("LOG_FILE", "orchestrator.log"))

# Global orchestrator client
orchestrator_client: Optional[OrchestratorClient] = None
scoring_engine: Optional[ScoringEngine] = None


# =============================================================================
# LIFESPAN MANAGEMENT
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown
    """
    # Startup
    logger.info("=" * 80)
    logger.info("SYNTHGUARD ORCHESTRATOR STARTING UP")
    logger.info("=" * 80)
    
    global orchestrator_client, scoring_engine
    
    # Initialize orchestrator client
    orchestrator_client = OrchestratorClient(
        layer1_url=os.getenv("LAYER1_URL", "http://localhost:5000"),
        layer1_endpoint=os.getenv("LAYER1_ENDPOINT", "/api/analyze"),
        layer23_url=os.getenv("LAYER2_3_URL", "http://localhost:8000"),
        layer23_endpoint=os.getenv("LAYER2_3_ENDPOINT", "/api/analyze"),
        layer4_url=os.getenv("LAYER4_URL", "http://localhost:6000"),
        layer4_endpoint=os.getenv("LAYER4_ENDPOINT", "/api/analyze-behavior"),
        timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
        layer1_enabled=os.getenv("LAYER1_ENABLED", "true").lower() == "true",
        layer23_enabled=os.getenv("LAYER2_3_ENABLED", "true").lower() == "true",
        layer4_enabled=os.getenv("LAYER4_ENABLED", "false").lower() == "true",
        layer5_enabled=os.getenv("LAYER5_ENABLED", "true").lower() == "true"
    )
    
    # Initialize scoring engine
    scoring_engine = ScoringEngine(
        weight_layer1=float(os.getenv("WEIGHT_LAYER1", "0.25")),
        weight_layer23=float(os.getenv("WEIGHT_LAYER2_3", "0.50")),
        weight_layer4=float(os.getenv("WEIGHT_LAYER4", "0.15")),
        weight_layer5=float(os.getenv("WEIGHT_LAYER5", "0.10")),
        threshold_verified=int(os.getenv("THRESHOLD_VERIFIED", "90")),
        threshold_suspicious=int(os.getenv("THRESHOLD_SUSPICIOUS", "50"))
    )
    
    logger.info("Orchestrator client initialized")
    logger.info("Scoring engine initialized")
    
    # Check layer health
    logger.info("Checking layer health...")
    health_status = await orchestrator_client.check_health()
    for layer_id, is_healthy in health_status.items():
        status_emoji = "✅" if is_healthy else "❌"
        logger.info(f"{status_emoji} {layer_id}: {'Healthy' if is_healthy else 'Unavailable'}")
    
    logger.info("=" * 80)
    logger.info(f"Server running on http://{os.getenv('ORCHESTRATOR_HOST', '0.0.0.0')}:{os.getenv('ORCHESTRATOR_PORT', '9000')}")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("=" * 80)
    logger.info(" SYNTHGUARD ORCHESTRATOR SHUTTING DOWN")
    logger.info("=" * 80)
    
    if orchestrator_client:
        await orchestrator_client.close()
        logger.info(" Orchestrator client closed")


# =============================================================================
# FASTAPI APP INITIALIZATION
# =============================================================================

app = FastAPI(
    title="SynthGuard Orchestrator",
    description="AI-Powered Synthetic Identity Fraud Detection System - Integration Layer",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "service": "SynthGuard Orchestrator",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "verification": "/api/verify-identity",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns status of orchestrator and all layers
    """
    try:
        if not orchestrator_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Orchestrator not initialized"
            )
        
        layers_status = await orchestrator_client.check_health()
        
        return HealthResponse(
            status="healthy",
            orchestrator_version="1.0.0",
            layers_status=layers_status
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )


@app.post("/api/verify-identity", response_model=VerificationResponse, tags=["Verification"])
async def verify_identity(request: VerificationRequest):
    """
    Main verification endpoint
    
    Orchestrates all 5 layers to verify identity authenticity
    
    **Process:**
    1. Layer 1: Document Forensics (analyze uploaded documents)
    2. Layer 2&3: OSINT + Graph Analysis (digital footprint)
    3. Layer 4: Behavioral Patterns (human vs bot detection)
    4. Layer 5: Blockchain Verification (consortium check)
    5. Calculate weighted score and final verdict
    
    **Returns:**
    - Final score (0-100)
    - Verdict (VERIFIED, SUSPICIOUS, REJECT)
    - Detailed breakdown from all layers
    - Red flags and trust indicators
    - Visualization data
    """
    verification_id = generate_verification_id()
    start_time = time.time()
    
    logger.info("=" * 80)
    logger.info(f" NEW VERIFICATION REQUEST: {verification_id}")
    logger.info(f" Identity: {request.identity_data.name} ({request.identity_data.email})")
    logger.info("=" * 80)
    
    try:
        if not orchestrator_client or not scoring_engine:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Orchestrator services not initialized"
            )
        
        # =====================================================================
        # STEP 1: DISPATCH TO ALL LAYERS (PARALLEL EXECUTION)
        # =====================================================================
        
        logger.info(" Dispatching to all layers in parallel...")
        
        tasks = []
        layer_results = {}
        
        # Layer 1: Document Forensics
        if orchestrator_client.layer1 and request.documents:
            for doc in request.documents:
                tasks.append(("layer_1", orchestrator_client.layer1.analyze_document(doc)))
        
        # Layer 2&3: OSINT + Graph
        if orchestrator_client.layer23:
            tasks.append(("layer_2_3", orchestrator_client.layer23.analyze_identity(request.identity_data)))
        
        # Layer 4: Behavioral
        if orchestrator_client.layer4 and request.behavioral_data:
            tasks.append(("layer_4", orchestrator_client.layer4.analyze_behavior(request.behavioral_data)))
        
        # Layer 5: Blockchain
        if orchestrator_client.layer5:
            tasks.append(("layer_5", orchestrator_client.layer5.verify_identity(request.identity_data)))
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
        
        # Map results back to layer IDs
        for i, (layer_id, _) in enumerate(tasks):
            if isinstance(results[i], Exception):
                logger.error(f" {layer_id} raised exception: {str(results[i])}")
                # Create error result
                layer_results[layer_id] = type('ErrorResult', (), {
                    'layer_id': layer_id,
                    'status': LayerStatusEnum.ERROR,
                    'score': 0,
                    'error_message': str(results[i]),
                    'key_findings': [f"Error: {str(results[i])}"]
                })()
            else:
                layer_results[layer_id] = results[i]
        
        logger.info(f" All layers completed - {len(layer_results)} results received")
        
        # =====================================================================
        # STEP 2: CALCULATE FINAL SCORE AND VERDICT
        # =====================================================================
        
        logger.info(" Calculating final score...")
        
        final_score, verdict, confidence, contributions, red_flags, trust_indicators = \
            scoring_engine.calculate_final_score(layer_results)
        
        score_breakdown = scoring_engine.create_score_breakdown(
            final_score, verdict, confidence, contributions, red_flags, trust_indicators
        )
        
        # =====================================================================
        # STEP 3: PREPARE VISUALIZATION DATA
        # =====================================================================
        
        visualization_data = {}
        
        # Graph data from Layer 2&3
        if "layer_2_3" in layer_results and layer_results["layer_2_3"].status == LayerStatusEnum.SUCCESS:
            layer23 = layer_results["layer_2_3"]
            visualization_data["graph_nodes"] = layer23.graph_nodes
            visualization_data["graph_edges"] = layer23.graph_edges
        
        # Score breakdown chart
        visualization_data["score_chart"] = {
            "labels": [c.layer_name for c in contributions],
            "scores": [c.score for c in contributions],
            "weights": [c.weight for c in contributions],
            "contributions": [c.contribution for c in contributions]
        }
        
        # =====================================================================
        # STEP 4: CALCULATE PERFORMANCE METRICS
        # =====================================================================
        
        total_time_ms = int((time.time() - start_time) * 1000)
        layers_executed = len([r for r in layer_results.values() if r.status != LayerStatusEnum.DISABLED])
        layers_failed = len([r for r in layer_results.values() if r.status in [LayerStatusEnum.ERROR, LayerStatusEnum.TIMEOUT]])
        
        logger.info("=" * 80)
        logger.info(f" VERIFICATION COMPLETE: {verification_id}")
        logger.info(f"Final Score: {final_score}/100")
        logger.info(f"  Verdict: {verdict.value}")
        logger.info(f" Confidence: {confidence}")
        logger.info(f"  Total Time: {total_time_ms}ms")
        logger.info(f" Red Flags: {len(red_flags)}")
        logger.info(f" Trust Indicators: {len(trust_indicators)}")
        logger.info("=" * 80)
        
        # =====================================================================
        # STEP 5: RETURN RESPONSE
        # =====================================================================
        
        return VerificationResponse(
            verification_id=verification_id,
            final_score=final_score,
            verdict=verdict,
            confidence=confidence,
            recommendation=score_breakdown.recommendation,
            score_breakdown=score_breakdown,
            layer_results={k: v for k, v in layer_results.items()},
            visualization_data=visualization_data,
            total_processing_time_ms=total_time_ms,
            layers_executed=layers_executed,
            layers_failed=layers_failed
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f" Verification failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=format_error_response(e)
        )


@app.post("/api/verify-identity-simple", tags=["Verification"])
async def verify_identity_simple(request: VerificationRequest):
    """
    Simplified verification endpoint
    Returns only essential information (score, verdict, key findings)
    """
    try:
        # Call full verification
        full_response = await verify_identity(request)
        
        # Return simplified response
        return {
            "verification_id": full_response.verification_id,
            "final_score": full_response.final_score,
            "verdict": full_response.verdict,
            "confidence": full_response.confidence,
            "recommendation": full_response.recommendation,
            "red_flags": [
                {"severity": rf.severity, "message": rf.message}
                for rf in full_response.score_breakdown.red_flags[:5]
            ],
            "trust_indicators": full_response.score_breakdown.trust_indicators[:5],
            "processing_time_ms": full_response.total_processing_time_ms
        }
    
    except Exception as e:
        logger.error(f" Simple verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/layer-status", tags=["Monitoring"])
async def get_layer_status():
    """
    Get detailed status of all layers
    """
    try:
        if not orchestrator_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Orchestrator not initialized"
            )
        
        health_status = await orchestrator_client.check_health()
        
        return {
            "timestamp": get_timestamp(),
            "layers": {
                "layer_1": {
                    "name": "Document Forensics",
                    "enabled": orchestrator_client.layer1 is not None,
                    "healthy": health_status.get("layer_1", False),
                    "weight": scoring_engine.weights.get("layer_1", 0) if scoring_engine else 0
                },
                "layer_2_3": {
                    "name": "OSINT + Graph Analysis",
                    "enabled": orchestrator_client.layer23 is not None,
                    "healthy": health_status.get("layer_2_3", False),
                    "weight": scoring_engine.weights.get("layer_2_3", 0) if scoring_engine else 0
                },
                "layer_4": {
                    "name": "Behavioral Patterns",
                    "enabled": orchestrator_client.layer4 is not None,
                    "healthy": health_status.get("layer_4", False),
                    "weight": scoring_engine.weights.get("layer_4", 0) if scoring_engine else 0
                },
                "layer_5": {
                    "name": "Blockchain Verification",
                    "enabled": orchestrator_client.layer5 is not None,
                    "healthy": health_status.get("layer_5", False),
                    "weight": scoring_engine.weights.get("layer_5", 0) if scoring_engine else 0
                }
            }
        }
    
    except Exception as e:
        logger.error(f" Layer status check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "timestamp": get_timestamp()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f" Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=format_error_response(exc)
    )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("ORCHESTRATOR_HOST", "0.0.0.0")
    port = int(os.getenv("ORCHESTRATOR_PORT", "9000"))
    reload = os.getenv("ORCHESTRATOR_RELOAD", "true").lower() == "true"
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )