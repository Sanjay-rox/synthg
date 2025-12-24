"""
Unified Identity Verification System - Graph Engine
====================================================

NetworkX-based identity graph construction with REAL temporal data.
Maps relationships between identity elements using actual discovered ages.

Key Features:
- Uses real breach dates from HaveIBeenPwned
- Extracts ages from OSINT search result timestamps
- Detects cross-references when identifiers appear together
- Calculates graph density for synthetic detection
"""

import re
import networkx as nx
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from models import GraphNode, GraphEdge, NodeType


# =============================================================================
# RELATIONSHIP TYPES
# =============================================================================

class RelationType:
    """Relationship type constants."""
    HAS_EMAIL = "HAS_EMAIL"
    HAS_PHONE = "HAS_PHONE"
    HAS_AADHAAR = "HAS_AADHAAR"
    HAS_PAN = "HAS_PAN"
    LIVED_AT = "LIVED_AT"
    HAS_PROFILE = "HAS_PROFILE"
    APPEARED_ON = "APPEARED_ON"
    MENTIONED_IN = "MENTIONED_IN"
    LINKED_TO = "LINKED_TO"
    USED_WITH = "USED_WITH"
    BREACHED_IN = "BREACHED_IN"
    VERIFIED_TOGETHER = "VERIFIED_TOGETHER"  # New: Strong cross-reference


# =============================================================================
# NODE COLORS
# =============================================================================

def get_node_color(node_type: str) -> str:
    """Get color for node type."""
    colors = {
        NodeType.PERSON.value: "#4CAF50",       # Green
        NodeType.EMAIL.value: "#2196F3",        # Blue
        NodeType.PHONE.value: "#9C27B0",        # Purple
        NodeType.AADHAAR.value: "#FF9800",      # Orange
        NodeType.PAN.value: "#FF5722",          # Deep Orange
        NodeType.ADDRESS.value: "#795548",      # Brown
        NodeType.SOCIAL_PROFILE.value: "#00BCD4",  # Cyan
        NodeType.DOMAIN.value: "#607D8B",       # Blue Grey
        NodeType.BREACH.value: "#F44336",       # Red
    }
    return colors.get(node_type, "#9E9E9E")


def get_age_color(age_years: float) -> str:
    """Get color based on relationship age (green=old, red=new)."""
    if age_years >= 10:
        return "#00C853"  # Green - very established
    elif age_years >= 5:
        return "#4CAF50"  # Light green - established
    elif age_years >= 3:
        return "#CDDC39"  # Yellow-green - medium
    elif age_years >= 1:
        return "#FFC107"  # Amber - recent
    else:
        return "#FF5722"  # Red - very new


# =============================================================================
# PLATFORM METADATA
# =============================================================================

PLATFORM_LAUNCH_YEARS = {
    'linkedin': 2003,
    'github': 2008,
    'twitter': 2006,
    'x': 2006,
    'facebook': 2004,
    'instagram': 2010,
    'stackoverflow': 2008,
    'medium': 2012,
    'reddit': 2005,
    'quora': 2009,
    'youtube': 2005,
    'researchgate': 2008,
    'academia': 2008,
    'crunchbase': 2007,
    'kaggle': 2010,
    'dev': 2016,
    'hashnode': 2019,
}


# =============================================================================
# IDENTITY GRAPH BUILDER
# =============================================================================

class IdentityGraphBuilder:
    """
    Builds NetworkX graph from identity data with REAL temporal information.
    
    Uses:
    - Actual breach dates from HaveIBeenPwned
    - Published dates from OSINT search results
    - Cross-reference detection from search snippets
    """
    
    def __init__(self):
        self.graph = nx.Graph()
        self.current_year = datetime.now().year
        self._added_nodes: Set[str] = set()
        self._cross_refs: List[Dict] = []
    
    def build_graph(
        self,
        identity: Dict[str, Any],
        enrichment: Dict[str, Any],
        osint_data: Optional[Dict[str, Any]] = None,
        search_hits: Optional[List[Dict]] = None,
    ) -> nx.Graph:
        """
        Build complete identity graph with real data.
        
        Args:
            identity: Original identity input
            enrichment: API enrichment data (includes breach_details now)
            osint_data: Analyzed OSINT results
            search_hits: Raw search results (for cross-reference detection)
            
        Returns:
            NetworkX graph
        """
        self.graph = nx.Graph()
        self._added_nodes = set()
        
        # 1. Add person node (central)
        person_id = self._add_person_node(identity)
        
        # 2. Add email node with real breach ages
        if identity.get('email'):
            email_data = enrichment.get('email', {})
            email_id = self._add_email_node(identity['email'], email_data)
            
            # Calculate email age from breach history
            email_age = self._calculate_email_age(email_data)
            self._add_edge(person_id, email_id, RelationType.HAS_EMAIL, email_age)
            
            # Add breach nodes with REAL dates
            self._add_breach_nodes(email_id, email_data)
        
        # 3. Add phone node
        if identity.get('phone'):
            phone_data = enrichment.get('phone', {})
            phone_id = self._add_phone_node(identity['phone'], phone_data)
            phone_age = phone_data.get('registration_age_years', 0)
            self._add_edge(person_id, phone_id, RelationType.HAS_PHONE, phone_age)
            
            # Link email and phone if both exist
            if identity.get('email'):
                email_id = f"email_{identity['email'].replace('@', '_at_')}"
                email_age = self._calculate_email_age(enrichment.get('email', {}))
                link_age = min(email_age, phone_age) if phone_age else email_age
                self._add_edge(email_id, phone_id, RelationType.USED_WITH, link_age)
        
        # 4. Add Aadhaar node (Indian)
        if identity.get('aadhaar'):
            aadhaar_data = enrichment.get('aadhaar', {})
            aadhaar_id = self._add_aadhaar_node(identity['aadhaar'], aadhaar_data)
            self._add_edge(
                person_id, aadhaar_id,
                RelationType.HAS_AADHAAR,
                aadhaar_data.get('years_active', 0)
            )
        
        # 5. Add PAN node (Indian)
        if identity.get('pan'):
            pan_data = enrichment.get('pan', {})
            pan_id = self._add_pan_node(identity['pan'], pan_data)
            self._add_edge(
                person_id, pan_id,
                RelationType.HAS_PAN,
                pan_data.get('years_active', 0)
            )
            
            # Link PAN to Aadhaar
            if identity.get('aadhaar'):
                aadhaar_id = f"aadhaar_{identity['aadhaar'][-4:]}"
                link_age = min(
                    enrichment.get('pan', {}).get('years_active', 0),
                    enrichment.get('aadhaar', {}).get('years_active', 0)
                )
                self._add_edge(pan_id, aadhaar_id, RelationType.LINKED_TO, link_age)
        
        # 6. Add address node
        if identity.get('location') or enrichment.get('address'):
            address_data = enrichment.get('address', {})
            address = identity.get('location') or address_data.get('address', 'Unknown')
            address_id = self._add_address_node(address, address_data)
            self._add_edge(
                person_id, address_id,
                RelationType.LIVED_AT,
                address_data.get('years_at_address', 3.0)
            )
            
            # Link Aadhaar to address
            if identity.get('aadhaar'):
                aadhaar_id = f"aadhaar_{identity['aadhaar'][-4:]}"
                self._add_edge(
                    aadhaar_id, address_id,
                    RelationType.APPEARED_ON,
                    enrichment.get('aadhaar', {}).get('years_active', 0)
                )
        
        # 7. Process OSINT search hits with REAL dates
        if search_hits:
            self._add_osint_nodes(person_id, identity, osint_data, search_hits)
            
            # 8. Detect cross-references (identifiers appearing together)
            self._detect_cross_references(identity, search_hits)
            self._add_cross_reference_edges(identity)
        
        return self.graph
    
    def _calculate_email_age(self, email_data: Dict) -> float:
        """Calculate email age from breach history or default."""
        # Use oldest breach year as proxy for email age
        oldest_breach = email_data.get('oldest_breach_year')
        if oldest_breach:
            return self.current_year - oldest_breach
        
        # Fallback based on account age estimate
        return email_data.get('account_age_years', 3.0)
    
    def _add_breach_nodes(self, email_id: str, email_data: Dict):
        """Add breach nodes with REAL dates from HaveIBeenPwned."""
        breach_details = email_data.get('breach_details', [])
        
        # Fallback to old format if details not available
        if not breach_details and email_data.get('breaches'):
            oldest_year = email_data.get('oldest_breach_year', self.current_year - 3)
            for i, name in enumerate(email_data['breaches'][:5]):
                # Estimate: spread breaches between oldest and now
                spread = self.current_year - oldest_year
                estimated_year = oldest_year + int(spread * i / max(len(email_data['breaches']), 1))
                breach_details.append({'name': name, 'year': estimated_year})
        
        for breach in breach_details[:5]:
            breach_name = breach.get('name', 'Unknown')
            breach_year = breach.get('year')
            
            breach_id = self._add_breach_node(breach_name, breach_year)
            
            # Calculate REAL age from breach date
            if breach_year:
                age = self.current_year - breach_year
            else:
                age = 3.0  # Conservative fallback
            
            self._add_edge(email_id, breach_id, RelationType.BREACHED_IN, age)
    
    def _add_osint_nodes(
        self,
        person_id: str,
        identity: Dict,
        osint_data: Optional[Dict],
        search_hits: List[Dict],
    ):
        """Add nodes from OSINT search results with REAL dates."""
        seen_domains: Set[str] = set()
        
        for hit in search_hits:
            domain = hit.get('domain', '')
            if not domain or domain in seen_domains:
                continue
            
            seen_domains.add(domain)
            
            # Extract REAL age from published date
            age = self._parse_published_age(hit.get('published'))
            
            # Categorize and add appropriate node
            platform = self._detect_platform(domain)
            
            if platform:
                # It's a known social/professional platform
                profile_id = self._add_social_profile_node({
                    'platform': platform.title(),
                    'url': hit.get('url', ''),
                    'title': hit.get('title', ''),
                })
                self._add_edge(person_id, profile_id, RelationType.HAS_PROFILE, age)
            else:
                # Generic domain mention
                domain_id = self._add_domain_node(domain)
                self._add_edge(person_id, domain_id, RelationType.APPEARED_ON, age)
    
    def _parse_published_age(self, published: Optional[str]) -> float:
        """Extract age from published date string."""
        if not published:
            return 2.0  # Conservative default
        
        # Try to find a year (2015, 2020, etc.)
        year_match = re.search(r'20\d{2}', str(published))
        if year_match:
            year = int(year_match.group())
            if 2000 <= year <= self.current_year:
                return max(0.5, self.current_year - year)
        
        # Try to parse ISO date
        try:
            if 'T' in str(published) or '-' in str(published):
                # ISO format: 2023-05-15 or 2023-05-15T10:30:00
                year = int(str(published)[:4])
                if 2000 <= year <= self.current_year:
                    return max(0.5, self.current_year - year)
        except:
            pass
        
        return 2.0  # Default if parsing fails
    
    def _detect_platform(self, domain: str) -> Optional[str]:
        """Detect if domain is a known platform, return platform name."""
        domain_lower = domain.lower()
        
        for platform, _ in PLATFORM_LAUNCH_YEARS.items():
            if platform in domain_lower:
                return platform
        
        return None
    
    def _detect_cross_references(
        self,
        identity: Dict,
        search_hits: List[Dict],
    ):
        """Find when multiple identity elements appear together in search results."""
        self._cross_refs = []
        
        email = identity.get('email', '').lower()
        phone = identity.get('phone', '')
        name = identity.get('name', '').lower()
        
        # Clean phone for matching (last 6-10 digits)
        phone_pattern = re.sub(r'\D', '', phone)[-10:] if phone else ''
        
        for hit in search_hits:
            text = (
                (hit.get('snippet', '') or '') + ' ' +
                (hit.get('title', '') or '') + ' ' +
                (hit.get('url', '') or '')
            ).lower()
            
            found = {
                'email': email and email in text,
                'phone': phone_pattern and phone_pattern[-6:] in text,
                'name': name and len(name) > 3 and name in text,
            }
            
            found_count = sum(found.values())
            
            if found_count >= 2:
                # Multiple identifiers found together - strong signal!
                self._cross_refs.append({
                    'source': hit.get('domain', 'unknown'),
                    'url': hit.get('url', ''),
                    'found': found,
                    'count': found_count,
                    'age': self._parse_published_age(hit.get('published')),
                })
    
    def _add_cross_reference_edges(self, identity: Dict):
        """Add VERIFIED_TOGETHER edges when identifiers appear together."""
        if not self._cross_refs:
            return
        
        email = identity.get('email')
        phone = identity.get('phone')
        
        email_id = f"email_{email.replace('@', '_at_')}" if email else None
        phone_id = f"phone_{phone[-4:]}" if phone else None
        
        for ref in self._cross_refs:
            age = ref['age']
            source = ref['source']
            
            # Add source domain as evidence node
            source_id = self._add_domain_node(source)
            
            if ref['found'].get('email') and ref['found'].get('phone') and email_id and phone_id:
                # Email and phone found together - STRONG signal
                self._add_edge(email_id, phone_id, RelationType.VERIFIED_TOGETHER, age)
                self._add_edge(email_id, source_id, RelationType.APPEARED_ON, age)
                self._add_edge(phone_id, source_id, RelationType.APPEARED_ON, age)
            
            elif ref['found'].get('email') and ref['found'].get('name') and email_id:
                # Email and name found together
                self._add_edge(email_id, source_id, RelationType.MENTIONED_IN, age)
            
            elif ref['found'].get('phone') and ref['found'].get('name') and phone_id:
                # Phone and name found together
                self._add_edge(phone_id, source_id, RelationType.MENTIONED_IN, age)
    
    def _add_person_node(self, identity: Dict) -> str:
        """Add central person node."""
        name = identity.get('name', 'Unknown')
        node_id = f"person_{name.lower().replace(' ', '_')}"
        
        if node_id in self._added_nodes:
            return node_id
        
        self.graph.add_node(
            node_id,
            type=NodeType.PERSON.value,
            label=name,
            color=get_node_color(NodeType.PERSON.value),
            size=40,
            dob=identity.get('dob'),
        )
        self._added_nodes.add(node_id)
        return node_id
    
    def _add_email_node(self, email: str, data: Dict) -> str:
        """Add email node."""
        node_id = f"email_{email.replace('@', '_at_')}"
        
        if node_id in self._added_nodes:
            return node_id
        
        age = self._calculate_email_age(data)
        
        self.graph.add_node(
            node_id,
            type=NodeType.EMAIL.value,
            label=email,
            color=get_age_color(age),
            size=30,
            account_age=round(age, 1),
            breach_count=data.get('breach_count', 0),
            is_disposable=data.get('is_disposable', False),
        )
        self._added_nodes.add(node_id)
        return node_id
    
    def _add_phone_node(self, phone: str, data: Dict) -> str:
        """Add phone node."""
        node_id = f"phone_{phone[-4:]}"
        
        if node_id in self._added_nodes:
            return node_id
        
        age = data.get('registration_age_years', 0)
        
        self.graph.add_node(
            node_id,
            type=NodeType.PHONE.value,
            label=f"Phone-{phone[-4:]}",
            color=get_age_color(age),
            size=25,
            carrier=data.get('carrier', 'Unknown'),
            valid=data.get('valid'),
        )
        self._added_nodes.add(node_id)
        return node_id
    
    def _add_aadhaar_node(self, aadhaar: str, data: Dict) -> str:
        """Add Aadhaar node."""
        node_id = f"aadhaar_{aadhaar[-4:]}"
        
        if node_id in self._added_nodes:
            return node_id
        
        age = data.get('years_active', 0)
        
        self.graph.add_node(
            node_id,
            type=NodeType.AADHAAR.value,
            label=f"Aadhaar-{aadhaar[-4:]}",
            color=get_age_color(age),
            size=30,
            years_active=age,
            enrollment_year=data.get('enrollment_year'),
        )
        self._added_nodes.add(node_id)
        return node_id
    
    def _add_pan_node(self, pan: str, data: Dict) -> str:
        """Add PAN node."""
        node_id = f"pan_{pan}"
        
        if node_id in self._added_nodes:
            return node_id
        
        age = data.get('years_active', 0)
        
        self.graph.add_node(
            node_id,
            type=NodeType.PAN.value,
            label=f"PAN-{pan}",
            color=get_age_color(age),
            size=28,
            years_active=age,
            issue_year=data.get('issue_year'),
        )
        self._added_nodes.add(node_id)
        return node_id
    
    def _add_address_node(self, address: str, data: Dict) -> str:
        """Add address node."""
        short_addr = address[:30] + "..." if len(address) > 30 else address
        node_id = f"address_{hash(address) % 10000}"
        
        if node_id in self._added_nodes:
            return node_id
        
        self.graph.add_node(
            node_id,
            type=NodeType.ADDRESS.value,
            label=short_addr,
            color=get_node_color(NodeType.ADDRESS.value),
            size=25,
            city=data.get('city'),
            state=data.get('state'),
            pincode=data.get('pincode'),
            valid=data.get('valid'),
        )
        self._added_nodes.add(node_id)
        return node_id
    
    def _add_social_profile_node(self, profile: Dict) -> str:
        """Add social profile node."""
        platform = profile.get('platform', 'Unknown')
        url_hash = hash(profile.get('url', '')) % 10000
        node_id = f"profile_{platform.lower()}_{url_hash}"
        
        if node_id in self._added_nodes:
            return node_id
        
        self.graph.add_node(
            node_id,
            type=NodeType.SOCIAL_PROFILE.value,
            label=platform,
            color=get_node_color(NodeType.SOCIAL_PROFILE.value),
            size=22,
            url=profile.get('url'),
        )
        self._added_nodes.add(node_id)
        return node_id
    
    def _add_domain_node(self, domain: str) -> str:
        """Add domain node."""
        node_id = f"domain_{domain.replace('.', '_')}"
        
        if node_id in self._added_nodes:
            return node_id
        
        self.graph.add_node(
            node_id,
            type=NodeType.DOMAIN.value,
            label=domain,
            color=get_node_color(NodeType.DOMAIN.value),
            size=20,
        )
        self._added_nodes.add(node_id)
        return node_id
    
    def _add_breach_node(self, breach_name: str, breach_year: Optional[int] = None) -> str:
        """Add data breach node with real year."""
        safe_name = breach_name.lower().replace(' ', '_')[:20]
        node_id = f"breach_{safe_name}"
        
        if node_id in self._added_nodes:
            return node_id
        
        age = (self.current_year - breach_year) if breach_year else 3.0
        
        label = f"{breach_name[:12]}"
        if breach_year:
            label += f" ({breach_year})"
        
        self.graph.add_node(
            node_id,
            type=NodeType.BREACH.value,
            label=label,
            color=get_node_color(NodeType.BREACH.value),
            size=18,
            year=breach_year,
            age_years=round(age, 1),
        )
        self._added_nodes.add(node_id)
        return node_id
    
    def _add_edge(
        self,
        from_node: str,
        to_node: str,
        rel_type: str,
        age_years: float,
    ):
        """Add edge between nodes (avoid duplicates)."""
        # Check if edge already exists
        if self.graph.has_edge(from_node, to_node):
            return
        
        self.graph.add_edge(
            from_node,
            to_node,
            relationship_type=rel_type,
            age_years=max(0, age_years or 0),
            color=get_age_color(age_years or 0),
        )
    
    def to_vis_format(self) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Convert graph to Vis.js format for frontend."""
        nodes = []
        edges = []
        
        for node_id, data in self.graph.nodes(data=True):
            nodes.append(GraphNode(
                id=node_id,
                label=data.get('label', node_id),
                type=data.get('type', 'Unknown'),
                color=data.get('color', '#9E9E9E'),
                size=data.get('size', 25),
                properties={k: v for k, v in data.items() 
                           if k not in ['label', 'type', 'color', 'size']},
            ))
        
        for from_node, to_node, data in self.graph.edges(data=True):
            age = data.get('age_years', 0)
            rel_type = data.get('relationship_type', 'RELATED')
            
            edges.append(GraphEdge(
                from_node=from_node,
                to_node=to_node,
                label=f"{rel_type}\n({age:.1f}y)",
                color=data.get('color', '#666'),
                age_years=age,
                relationship_type=rel_type,
            ))
        
        return nodes, edges
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics including synthetic detection metrics."""
        if self.graph.number_of_nodes() == 0:
            return {
                "total_nodes": 0,
                "total_edges": 0,
                "node_types": {},
                "oldest_relationship": 0,
                "average_age": 0,
                "density_score": 0,
                "cross_references": 0,
                "synthetic_indicators": [],
            }
        
        # Count node types
        node_types = {}
        for _, data in self.graph.nodes(data=True):
            ntype = data.get('type', 'Unknown')
            node_types[ntype] = node_types.get(ntype, 0) + 1
        
        # Get edge ages
        ages = []
        for _, _, data in self.graph.edges(data=True):
            age = data.get('age_years', 0)
            if age:
                ages.append(age)
        
        oldest = max(ages) if ages else 0
        avg_age = sum(ages) / len(ages) if ages else 0
        
        # Calculate density score
        nodes = self.graph.number_of_nodes()
        edges = self.graph.number_of_edges()
        density = edges / nodes if nodes > 0 else 0
        
        # Detect synthetic indicators
        synthetic_indicators = []
        if oldest < 2:
            synthetic_indicators.append("All relationships less than 2 years old")
        if edges < 5:
            synthetic_indicators.append("Very few connections (sparse graph)")
        if len(self._cross_refs) == 0:
            synthetic_indicators.append("No cross-references found")
        if density < 1.0:
            synthetic_indicators.append("Low graph density")
        
        return {
            "total_nodes": nodes,
            "total_edges": edges,
            "node_types": node_types,
            "oldest_relationship": round(oldest, 1),
            "average_age": round(avg_age, 1),
            "density_score": round(density, 2),
            "cross_references": len(self._cross_refs),
            "temporal_span": round(oldest, 1),
            "synthetic_indicators": synthetic_indicators,
            "is_likely_synthetic": len(synthetic_indicators) >= 3,
        }
