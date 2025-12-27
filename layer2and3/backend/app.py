"""
Unified Identity Verification System - FastAPI Application
===========================================================

Production-ready API combining:
- OSINT Analysis (Google Dorking)
- Graph-based Identity Mapping
- Claude AI Verdicts
- Multi-source API Enrichment

Built for PECHACKS 2025
"""

import asyncio
import os
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()  # Load from .env in current directory
load_dotenv("../../.env")  # Also try parent Layer 2 folder
load_dotenv("../../env.example")  # Fallback to env.example

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import (
    IdentityInput, VerificationResult, GraphNode, GraphEdge,
    ScoreBreakdown, VerificationBucket, RedFlag, TrustIndicator,
    OSINTAnalysis, EnrichmentData, EmailEnrichment, PhoneEnrichment,
    AadhaarEnrichment, PANEnrichment, AddressEnrichment, ClaudeVerdict,
)
from api_integrations import (
    APIConfig, WebSearchAPI, HaveIBeenPwnedAPI, NumverifyAPI,
    IndiaPostAPI, EmailAnalyzer, DomainTrustAnalyzer,
)
from osint_engine import GoogleDorkGenerator, OSINTResultAnalyzer
from graph_engine import IdentityGraphBuilder
from claude_analyzer import ClaudeAnalyzer
from red_flags import detect_red_flags
from scoring_engine import UnifiedScoringEngine


# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(
    title="Unified Identity Verification System",
    description="""
    🔐 **Comprehensive Identity Verification API**
    
    Combines multiple intelligence sources:
    - **OSINT Analysis**: 50+ Google Dorking patterns
    - **Graph Mapping**: NetworkX relationship analysis
    - **AI Verdicts**: Claude-powered authenticity assessment
    - **API Enrichment**: HaveIBeenPwned, Numverify, India Post
    
    Supports global identities + Indian documents (Aadhaar, PAN).
    
    Built for PECHACKS 2025.
    """,
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/api/health")
async def health_check():
    """Health check with API status."""
    return {
        "status": "healthy",
        "service": "Unified Identity Verification System",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "api_status": APIConfig.get_status(),
    }
@app.get("/health")
async def health_check_simple():
    """Simple health check for orchestrator"""
    return {
        "status": "healthy",
        "service": "Layer 2&3 - OSINT + Graph Analysis",
        "version": "3.0.0"
    }

# =============================================================================
# MAIN ANALYSIS ENDPOINT
# =============================================================================

@app.post("/api/analyze", response_model=VerificationResult)
async def analyze_identity(identity: IdentityInput):
    """
    🔍 **Comprehensive Identity Verification**
    
    Performs multi-source analysis:
    1. API Enrichment (email, phone, address validation)
    2. OSINT Web Search (Google Dorking)
    3. Graph Construction (identity relationships)
    4. AI Analysis (Claude verdict)
    5. Red Flag Detection
    6. Unified Scoring (12+ signals)
    
    Returns complete verification result with score, graph, and analysis.
    """
    start_time = time.time()
    
    # Validate input
    if not identity.has_identifiers():
        raise HTTPException(
            status_code=400,
            detail="At least one identifier (name, email, phone, or aadhaar) is required"
        )
    
    try:
        # Convert to dict
        identity_dict = identity.get_identifiers()
        identity_dict['context'] = identity.context.value
        
        print("=" * 60)
        print("🔍 UNIFIED IDENTITY VERIFICATION")
        print(f"   Name: {identity.name}")
        print(f"   Email: {identity.email}")
        print(f"   Phone: {identity.phone}")
        print(f"   Aadhaar: {'***' + identity.aadhaar[-4:] if identity.aadhaar else 'N/A'}")
        print(f"   Context: {identity.context.value}")
        print("=" * 60)
        
        # === PHASE 1: API ENRICHMENT ===
        print("\n📡 Phase 1: API Enrichment")
        enrichment = await enrich_identity(identity_dict)
        
        # === PHASE 2: OSINT ANALYSIS ===
        print("\n🔎 Phase 2: OSINT Analysis")
        osint_data, search_hits = await run_osint_analysis(identity_dict)
        
        # === PHASE 3: CLAUDE AI ANALYSIS ===
        print("\n🧠 Phase 3: Claude AI Analysis")
        claude_verdict = await run_claude_analysis(
            identity_dict, search_hits, enrichment
        )
        
        # === PHASE 4: GRAPH CONSTRUCTION ===
        print("\n📊 Phase 4: Graph Construction")
        graph_builder = IdentityGraphBuilder()
        graph = graph_builder.build_graph(
            identity_dict, 
            enrichment, 
            osint_data,
            search_hits  # Pass raw search hits for cross-reference detection
        )
        nodes, edges = graph_builder.to_vis_format()
        graph_stats = graph_builder.get_statistics()
        
        print(f"   Nodes: {graph_stats['total_nodes']}")
        print(f"   Edges: {graph_stats['total_edges']}")
        print(f"   Cross-refs: {graph_stats.get('cross_references', 0)}")
        print(f"   Oldest rel: {graph_stats.get('oldest_relationship', 0)}y")
        
        # === PHASE 5: RED FLAG DETECTION ===
        print("\n🚩 Phase 5: Red Flag Detection")
        red_flags, total_penalty = detect_red_flags(
            identity_dict, enrichment, osint_data, identity.context.value
        )
        print(f"   Red flags: {len(red_flags)}")
        print(f"   Total penalty: {total_penalty}")
        
        # === PHASE 6: UNIFIED SCORING ===
        print("\n📈 Phase 6: Unified Scoring")
        scorer = UnifiedScoringEngine()
        score_result = scorer.calculate_score(
            identity=identity_dict,
            enrichment=enrichment,
            graph=graph,
            osint_data=osint_data,
            claude_verdict=claude_verdict,
            red_flags=red_flags,
        )
        
        elapsed = int((time.time() - start_time) * 1000)
        
        print("=" * 60)
        print(f"✅ ANALYSIS COMPLETE")
        print(f"   Score: {score_result['total_score']}")
        print(f"   Bucket: {score_result['bucket'].value}")
        print(f"   Duration: {elapsed}ms")
        print("=" * 60)
        
        # Build response
        result = VerificationResult(
            identity=identity_dict,
            context=identity.context.value,
            total_score=score_result['total_score'],
            bucket=score_result['bucket'],
            interpretation=score_result['interpretation'],
            claude_verdict=claude_verdict.verdict if claude_verdict else "INCONCLUSIVE",
            claude_confidence=claude_verdict.confidence if claude_verdict else 0,
            claude_reasoning=claude_verdict.reasoning if claude_verdict else "",
            score_breakdown=score_result['score_breakdown'],
            nodes=nodes,
            edges=edges,
            total_connections=graph_stats['total_edges'],
            # New graph metrics for synthetic detection
            graph_density=graph_stats.get('density_score', 0.0),
            oldest_relationship_years=graph_stats.get('oldest_relationship', 0.0),
            cross_reference_count=graph_stats.get('cross_references', 0),
            synthetic_indicators=graph_stats.get('synthetic_indicators', []),
            red_flags=red_flags,
            trust_indicators=score_result['trust_indicators'],
            osint_analysis=OSINTAnalysis(
                total_hits=osint_data.get('total_hits', 0) if osint_data else 0,
                unique_domains=len(osint_data.get('unique_domains', [])) if osint_data else 0,
                high_trust_domains=osint_data.get('domain_distribution', {}).get('high_trust', []) if osint_data else [],
                social_profiles=osint_data.get('social_profiles', []) if osint_data else [],
                search_queries_executed=osint_data.get('queries_executed', 0) if osint_data else 0,
            ),
            domains_seen=osint_data.get('unique_domains', []) if osint_data else [],
            social_profiles=osint_data.get('social_profiles', []) if osint_data else [],
            enrichment=build_enrichment_model(enrichment),
            analysis_timestamp=datetime.utcnow().isoformat(),
            analysis_duration_ms=elapsed,
            queries_executed=osint_data.get('queries_executed', 0) if osint_data else 0,
        )
        
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# =============================================================================
# ENRICHMENT FUNCTIONS
# =============================================================================

async def _noop():
    """No-operation coroutine for parallel task alignment."""
    return None


async def enrich_identity(identity: Dict) -> Dict:
    """Enrich identity with API data."""
    enrichment = {}
    
    tasks = []
    
    # Email enrichment
    if identity.get('email'):
        tasks.append(enrich_email(identity['email']))
    else:
        tasks.append(_noop())
    
    # Phone enrichment
    if identity.get('phone'):
        tasks.append(enrich_phone(identity['phone']))
    else:
        tasks.append(_noop())
    
    # Address enrichment
    if identity.get('location'):
        tasks.append(enrich_address(identity['location']))
    else:
        tasks.append(_noop())
    
    # Run parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    if results[0] and not isinstance(results[0], Exception):
        enrichment['email'] = results[0]
    
    if results[1] and not isinstance(results[1], Exception):
        enrichment['phone'] = results[1]
    
    if results[2] and not isinstance(results[2], Exception):
        enrichment['address'] = results[2]
    
    # Indian documents (estimate ages)
    if identity.get('aadhaar') or identity.get('pan'):
        analyzer = ClaudeAnalyzer()
        ages = await analyzer.estimate_document_ages(identity)
        
        if identity.get('aadhaar'):
            enrichment['aadhaar'] = {
                'aadhaar': identity['aadhaar'],
                'enrollment_year': 2024 - ages.get('aadhaar_years', 0) if ages.get('aadhaar_years') else None,
                'years_active': ages.get('aadhaar_years', 0),
                'source': 'claude_estimate',
            }
        
        if identity.get('pan'):
            enrichment['pan'] = {
                'pan': identity['pan'],
                'issue_year': 2024 - ages.get('pan_years', 0) if ages.get('pan_years') else None,
                'years_active': ages.get('pan_years', 0),
                'source': 'claude_estimate',
            }
    
    return enrichment


async def enrich_email(email: str) -> Dict:
    """Enrich email data."""
    # Local analysis
    analysis = EmailAnalyzer.analyze(email)
    
    # Breach check
    breach_data = await HaveIBeenPwnedAPI.check_breaches(email)
    
    # Calculate email age from oldest breach (real data!)
    oldest_breach_year = breach_data.get('oldest_breach_year')
    if oldest_breach_year:
        account_age = datetime.now().year - oldest_breach_year
    else:
        account_age = 5.0  # Default if no breach history
    
    return {
        'email': email,
        'account_age_years': account_age,
        'breach_count': breach_data.get('breach_count', 0),
        'breaches': breach_data.get('breaches', []),
        'breach_details': breach_data.get('breach_details', []),  # NEW: detailed breach info
        'oldest_breach_year': oldest_breach_year,
        'domain_reputation': 'trusted' if not analysis['is_disposable'] else 'disposable',
        'is_disposable': analysis['is_disposable'],
        'is_educational': analysis['is_educational'],
        'is_corporate': analysis['is_corporate'],
        'pattern': analysis['pattern'],
        'verified': breach_data.get('breached') is False,
    }


async def enrich_phone(phone: str) -> Dict:
    """Enrich phone data."""
    result = await NumverifyAPI.validate_phone(phone)
    return {
        'phone': phone,
        'carrier': result.get('carrier', 'Unknown'),
        'line_type': result.get('line_type', 'mobile'),
        'location': result.get('location'),
        'registration_age_years': result.get('registration_age_years', 5.0),
        'valid': result.get('valid'),
    }


async def enrich_address(address: str) -> Dict:
    """Enrich address data."""
    import re
    
    # Extract PIN code
    pincode_match = re.search(r'\b\d{6}\b', address)
    pincode = pincode_match.group(0) if pincode_match else None
    
    if pincode:
        result = await IndiaPostAPI.validate_pincode(pincode)
        return {
            'address': address,
            'city': result.get('city'),
            'state': result.get('state'),
            'district': result.get('district'),
            'pincode': pincode,
            'valid': result.get('valid'),
            'years_at_address': 5.0,  # Default estimate
        }
    
    return {
        'address': address,
        'city': None,
        'state': None,
        'pincode': None,
        'valid': None,
        'years_at_address': 5.0,
    }


# =============================================================================
# OSINT FUNCTIONS
# =============================================================================

async def run_osint_analysis(identity: Dict) -> tuple:
    """Run OSINT analysis with Google Dorking."""
    
    # Check if search API is available
    if not APIConfig.TAVILY_API_KEY and not APIConfig.SERPAPI_API_KEY:
        print("   ⚠️ No search API configured, skipping OSINT")
        return None, []
    
    # Generate dork queries
    generator = GoogleDorkGenerator(aggressive=True)
    all_dorks = generator.generate_all_dorks(
        name=identity.get('name'),
        email=identity.get('email'),
        phone=identity.get('phone'),
        username=identity.get('username'),
        company=identity.get('company'),
        location=identity.get('location'),
    )
    
    # Get priority queries (limit to 20)
    priority_dorks = generator.get_priority_queries(all_dorks, max_queries=20)
    queries = [d.query for d in priority_dorks]
    
    print(f"   Generated {len(queries)} dork queries")
    
    # Execute searches
    search_api = WebSearchAPI()
    all_hits = await search_api.search_batch(queries, max_results=8, max_concurrent=5)
    
    print(f"   Found {len(all_hits)} total results")
    
    # Analyze results
    analysis = OSINTResultAnalyzer.analyze_results(all_hits)
    analysis['queries_executed'] = search_api.request_count
    
    print(f"   High-trust domains: {analysis['high_trust_count']}")
    print(f"   Unique domains: {len(analysis['unique_domains'])}")
    
    return analysis, all_hits


async def run_claude_analysis(
    identity: Dict,
    search_hits: List[Dict],
    enrichment: Dict,
) -> Optional[ClaudeVerdict]:
    """Run Claude AI analysis."""
    
    if not APIConfig.GROQ_API_KEY:
        print("   ⚠️ Claude API not configured, skipping AI analysis")
        return None
    
    analyzer = ClaudeAnalyzer()
    verdict = await analyzer.analyze_identity(identity, search_hits, enrichment)
    
    print(f"   Verdict: {verdict.verdict} ({verdict.confidence}%)")
    
    return verdict


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def build_enrichment_model(enrichment: Dict) -> EnrichmentData:
    """Convert enrichment dict to Pydantic model."""
    return EnrichmentData(
        email=EmailEnrichment(**enrichment['email']) if enrichment.get('email') else None,
        phone=PhoneEnrichment(**enrichment['phone']) if enrichment.get('phone') else None,
        aadhaar=AadhaarEnrichment(**enrichment['aadhaar']) if enrichment.get('aadhaar') else None,
        pan=PANEnrichment(**enrichment['pan']) if enrichment.get('pan') else None,
        address=AddressEnrichment(**enrichment['address']) if enrichment.get('address') else None,
    )


# =============================================================================
# SIMPLE ENDPOINTS
# =============================================================================

@app.get("/api/config")
async def get_config():
    """Get current API configuration status."""
    return {
        "apis": APIConfig.get_status(),
        "search_provider": APIConfig.SEARCH_PROVIDER,
        "claude_model": APIConfig.CLAUDE_MODEL,
    }


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

