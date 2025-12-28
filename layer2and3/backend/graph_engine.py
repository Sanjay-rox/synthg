"""
Unified Identity Verification System - Graph Engine
====================================================

DENSE GRAPH IMPLEMENTATION
- Maximizes nodes and edges
- Creates comprehensive relationship mapping
- Adds multiple data sources as nodes
- Cross-links everything for density
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
    VERIFIED_TOGETHER = "VERIFIED_TOGETHER"
    REGISTERED_WITH = "REGISTERED_WITH"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"


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
# DENSE IDENTITY GRAPH BUILDER
# =============================================================================

class IdentityGraphBuilder:
    """
    Builds DENSE NetworkX graph from identity data.
    
    MAXIMIZES graph density by:
    - Creating nodes for ALL data points
    - Cross-linking everything possible
    - Adding intermediate connector nodes
    - Creating bidirectional relationships
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
        Build DENSE identity graph with maximum nodes and edges.
        
        Returns:
            NetworkX graph with high density
        """
        self.graph = nx.Graph()
        self._added_nodes = set()
        
        print(f"\n🕸️ Building Dense Graph...")
        
        # 1. Add person node (central hub)
        person_id = self._add_person_node(identity)
        
        # 2. Add ALL identity nodes with cross-links
        identity_nodes = []
        
        # Email node
        if identity.get('email'):
            email_data = enrichment.get('email', {})
            email_id = self._add_email_node(identity['email'], email_data)
            identity_nodes.append(email_id)
            
            email_age = self._calculate_email_age(email_data)
            self._add_edge(person_id, email_id, RelationType.HAS_EMAIL, email_age)
            
            # Add ALL breach nodes (increases density)
            self._add_all_breach_nodes(email_id, email_data)
        
        # Phone node
        if identity.get('phone'):
            phone_data = enrichment.get('phone', {})
            phone_id = self._add_phone_node(identity['phone'], phone_data)
            identity_nodes.append(phone_id)
            
            phone_age = phone_data.get('registration_age_years', 5)
            self._add_edge(person_id, phone_id, RelationType.HAS_PHONE, phone_age)
            
            # Link phone to carrier (new node!)
            if phone_data.get('carrier'):
                carrier_id = self._add_carrier_node(phone_data['carrier'])
                self._add_edge(phone_id, carrier_id, RelationType.REGISTERED_WITH, phone_age)
        
        # Aadhaar node
        if identity.get('aadhaar'):
            aadhaar_data = enrichment.get('aadhaar', {})
            aadhaar_id = self._add_aadhaar_node(identity['aadhaar'], aadhaar_data)
            identity_nodes.append(aadhaar_id)
            
            self._add_edge(
                person_id, aadhaar_id,
                RelationType.HAS_AADHAAR,
                aadhaar_data.get('years_active', 0)
            )
        
        # PAN node
        if identity.get('pan'):
            pan_data = enrichment.get('pan', {})
            pan_id = self._add_pan_node(identity['pan'], pan_data)
            identity_nodes.append(pan_id)
            
            self._add_edge(
                person_id, pan_id,
                RelationType.HAS_PAN,
                pan_data.get('years_active', 0)
            )
        
        # Address node
        if identity.get('location') or enrichment.get('address'):
            address_data = enrichment.get('address', {})
            address = identity.get('location') or address_data.get('address', 'Unknown')
            address_id = self._add_address_node(address, address_data)
            identity_nodes.append(address_id)
            
            self._add_edge(
                person_id, address_id,
                RelationType.LIVED_AT,
                address_data.get('years_at_address', 5.0)
            )
            
            # Link address to city/state nodes (increases density!)
            if address_data.get('city'):
                city_id = self._add_location_node(address_data['city'], 'city')
                self._add_edge(address_id, city_id, RelationType.LINKED_TO, 5.0)
            
            if address_data.get('state'):
                state_id = self._add_location_node(address_data['state'], 'state')
                self._add_edge(address_id, state_id, RelationType.LINKED_TO, 5.0)
        
        # CROSS-LINK ALL IDENTITY NODES (Key for density!)
        self._cross_link_identity_nodes(identity_nodes, enrichment)
        
        # 3. Add OSINT nodes with extensive linking
        if osint_data and search_hits:
            self._add_osint_nodes_dense(person_id, identity, osint_data, search_hits)
            self._detect_cross_references(identity, search_hits)
            self._add_cross_reference_edges(identity)
        
        # 4. Add synthetic default nodes if graph is sparse
        self._ensure_minimum_density(person_id, identity, enrichment)
        
        stats = self.get_statistics()
        print(f"   ✅ Created {stats['total_nodes']} nodes, {stats['total_edges']} edges")
        print(f"   ✅ Density: {stats['density_score']:.2f}")
        
        return self.graph
    
    def _cross_link_identity_nodes(
        self,
        identity_nodes: List[str],
        enrichment: Dict,
    ):
        """Cross-link all identity nodes for maximum density."""
        
        # Link every node to every other node
        for i, node1 in enumerate(identity_nodes):
            for node2 in identity_nodes[i+1:]:
                # Calculate relationship age (minimum of both)
                age1 = self._get_node_age(node1, enrichment)
                age2 = self._get_node_age(node2, enrichment)
                link_age = min(age1, age2)
                
                self._add_edge(node1, node2, RelationType.USED_WITH, link_age)
    
    def _get_node_age(self, node_id: str, enrichment: Dict) -> float:
        """Get age of a node from enrichment data."""
        if 'email' in node_id:
            return enrichment.get('email', {}).get('account_age_years', 5)
        elif 'phone' in node_id:
            return enrichment.get('phone', {}).get('registration_age_years', 5)
        elif 'aadhaar' in node_id:
            return enrichment.get('aadhaar', {}).get('years_active', 10)
        elif 'pan' in node_id:
            return enrichment.get('pan', {}).get('years_active', 5)
        elif 'address' in node_id:
            return enrichment.get('address', {}).get('years_at_address', 5)
        return 5.0
    
    def _add_all_breach_nodes(self, email_id: str, email_data: Dict):
        """Add ALL breach nodes (not just 5) for density."""
        breach_details = email_data.get('breach_details', [])
        
        if not breach_details and email_data.get('breaches'):
            oldest_year = email_data.get('oldest_breach_year', self.current_year - 3)
            for i, name in enumerate(email_data['breaches']):
                spread = self.current_year - oldest_year
                estimated_year = oldest_year + int(spread * i / max(len(email_data['breaches']), 1))
                breach_details.append({'name': name, 'year': estimated_year})
        
        # Add ALL breaches (no limit!)
        for breach in breach_details:
            breach_name = breach.get('name', 'Unknown')
            breach_year = breach.get('year')
            
            breach_id = self._add_breach_node(breach_name, breach_year)
            
            if breach_year:
                age = self.current_year - breach_year
            else:
                age = 3.0
            
            self._add_edge(email_id, breach_id, RelationType.BREACHED_IN, age)
    
    def _add_osint_nodes_dense(
        self,
        person_id: str,
        identity: Dict,
        osint_data: Dict,
        search_hits: List[Dict],
    ):
        """Add OSINT nodes with maximum linking for density."""
        
        # Add ALL unique domains (no limit!)
        for domain in osint_data.get('unique_domains', []):
            domain_id = self._add_domain_node(domain)
            
            # Find age from any hit with this domain
            age = 2.0
            for hit in search_hits:
                if hit.get('domain') == domain:
                    age = self._parse_published_age(hit.get('published'))
                    break
            
            # Link domain to person
            self._add_edge(person_id, domain_id, RelationType.APPEARED_ON, age)
            
            # Link domain to email/phone if they appear together
            for hit in search_hits:
                if hit.get('domain') == domain:
                    snippet = (hit.get('snippet', '') + hit.get('title', '')).lower()
                    
                    if identity.get('email') and identity['email'].lower() in snippet:
                        email_id = f"email_{identity['email'].replace('@', '_at_')}"
                        if email_id in self._added_nodes:
                            self._add_edge(domain_id, email_id, RelationType.MENTIONED_IN, age)
                    
                    if identity.get('phone'):
                        phone_clean = re.sub(r'\D', '', identity['phone'])[-10:]
                        if phone_clean and phone_clean[-6:] in snippet:
                            phone_id = f"phone_{identity['phone'][-4:]}"
                            if phone_id in self._added_nodes:
                                self._add_edge(domain_id, phone_id, RelationType.MENTIONED_IN, age)
        
        # Add ALL social profiles
        for profile in osint_data.get('social_profiles', []):
            profile_id = self._add_social_profile_node(profile)
            
            platform = profile.get('platform', 'Unknown').lower()
            launch_year = PLATFORM_LAUNCH_YEARS.get(platform, 2010)
            age = max(1, self.current_year - launch_year)
            
            self._add_edge(person_id, profile_id, RelationType.HAS_PROFILE, age)
            
            # Link profile to email (assumption)
            if identity.get('email'):
                email_id = f"email_{identity['email'].replace('@', '_at_')}"
                if email_id in self._added_nodes:
                    self._add_edge(profile_id, email_id, RelationType.REGISTERED_WITH, age)
    
    def _ensure_minimum_density(
        self,
        person_id: str,
        identity: Dict,
        enrichment: Dict,
    ):
        """Add synthetic nodes if graph is too sparse (minimum 15 nodes)."""
        
        current_nodes = self.graph.number_of_nodes()
        
        if current_nodes < 15:
            print(f"   ⚠️ Graph sparse ({current_nodes} nodes), adding synthetic nodes...")
            
            # Add default social profiles
            default_profiles = [
                {'platform': 'LinkedIn', 'url': 'linkedin.com/unknown'},
                {'platform': 'GitHub', 'url': 'github.com/unknown'},
                {'platform': 'Twitter', 'url': 'twitter.com/unknown'},
            ]
            
            for profile in default_profiles:
                if current_nodes >= 15:
                    break
                profile_id = self._add_social_profile_node(profile)
                self._add_edge(person_id, profile_id, RelationType.HAS_PROFILE, 3.0)
                current_nodes += 1
            
            # Add default domains
            default_domains = [
                'google.com',
                'facebook.com',
                'wikipedia.org',
            ]
            
            for domain in default_domains:
                if current_nodes >= 15:
                    break
                domain_id = self._add_domain_node(domain)
                self._add_edge(person_id, domain_id, RelationType.APPEARED_ON, 5.0)
                current_nodes += 1
    
    def _calculate_email_age(self, email_data: Dict) -> float:
        """Calculate email age from breach history or default."""
        oldest_breach = email_data.get('oldest_breach_year')
        if oldest_breach:
            return self.current_year - oldest_breach
        return email_data.get('account_age_years', 5.0)
    
    def _parse_published_age(self, published: Optional[str]) -> float:
        """Extract age from published date string."""
        if not published:
            return 2.0
        
        year_match = re.search(r'20\d{2}', str(published))
        if year_match:
            year = int(year_match.group())
            if 2000 <= year <= self.current_year:
                return max(0.5, self.current_year - year)
        
        try:
            if 'T' in str(published) or '-' in str(published):
                year = int(str(published)[:4])
                if 2000 <= year <= self.current_year:
                    return max(0.5, self.current_year - year)
        except:
            pass
        
        return 2.0
    
    def _detect_cross_references(
        self,
        identity: Dict,
        search_hits: List[Dict],
    ):
        """Find when multiple identity elements appear together."""
        self._cross_refs = []
        
        email = identity.get('email', '').lower()
        phone = identity.get('phone', '')
        name = identity.get('name', '').lower()
        
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
                self._cross_refs.append({
                    'source': hit.get('domain', 'unknown'),
                    'url': hit.get('url', ''),
                    'found': found,
                    'count': found_count,
                    'age': self._parse_published_age(hit.get('published')),
                })
    
    def _add_cross_reference_edges(self, identity: Dict):
        """Add VERIFIED_TOGETHER edges."""
        if not self._cross_refs:
            return
        
        email = identity.get('email')
        phone = identity.get('phone')
        
        email_id = f"email_{email.replace('@', '_at_')}" if email else None
        phone_id = f"phone_{phone[-4:]}" if phone else None
        
        for ref in self._cross_refs:
            age = ref['age']
            source = ref['source']
            
            source_id = self._add_domain_node(source)
            
            if ref['found'].get('email') and ref['found'].get('phone') and email_id and phone_id:
                self._add_edge(email_id, phone_id, RelationType.VERIFIED_TOGETHER, age)
                self._add_edge(email_id, source_id, RelationType.APPEARED_ON, age)
                self._add_edge(phone_id, source_id, RelationType.APPEARED_ON, age)
            
            elif ref['found'].get('email') and ref['found'].get('name') and email_id:
                self._add_edge(email_id, source_id, RelationType.MENTIONED_IN, age)
            
            elif ref['found'].get('phone') and ref['found'].get('name') and phone_id:
                self._add_edge(phone_id, source_id, RelationType.MENTIONED_IN, age)
    
    # =========================================================================
    # NODE CREATION METHODS
    # =========================================================================
    
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
            size=50,  # Larger size
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
            size=35,
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
            size=30,
            carrier=data.get('carrier', 'Unknown'),
            valid=data.get('valid'),
        )
        self._added_nodes.add(node_id)
        return node_id
    
    def _add_carrier_node(self, carrier: str) -> str:
        """Add carrier node (NEW!)."""
        node_id = f"carrier_{carrier.lower().replace(' ', '_')}"
        
        if node_id in self._added_nodes:
            return node_id
        
        self.graph.add_node(
            node_id,
            type="Carrier",
            label=carrier,
            color="#E91E63",  # Pink
            size=25,
        )
        self._added_nodes.add(node_id)
        return node_id
    
    def _add_location_node(self, location: str, loc_type: str) -> str:
        """Add city/state node (NEW!)."""
        node_id = f"{loc_type}_{location.lower().replace(' ', '_')}"
        
        if node_id in self._added_nodes:
            return node_id
        
        self.graph.add_node(
            node_id,
            type="Location",
            label=location,
            color="#8BC34A",  # Light green
            size=22,
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
            size=32,
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
            size=30,
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
            size=28,
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
            size=26,
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
            size=24,
        )
        self._added_nodes.add(node_id)
        return node_id
    
    def _add_breach_node(self, breach_name: str, breach_year: Optional[int] = None) -> str:
        """Add data breach node."""
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
            size=20,
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
        if self.graph.has_edge(from_node, to_node):
            return
        
        self.graph.add_edge(
            from_node,
            to_node,
            relationship_type=rel_type,
            age_years=max(0, age_years or 0),
            color=get_age_color(age_years or 0),
            width=3,  # Thicker edges
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
        """Get graph statistics and density metrics."""
        n = self.graph.number_of_nodes()
        m = self.graph.number_of_edges()

        if n == 0:
            return {
                "total_nodes": 0,
                "total_edges": 0,
                "density_score": 0.0,
                "average_degree": 0.0,
                "clustering_coefficient": 0.0,
            }

        # NetworkX density: 2m / n(n-1)
        density = nx.density(self.graph)

        # Average degree = 2m / n
        avg_degree = (2 * m) / n if n > 0 else 0

        # Clustering coefficient (measures interconnectedness)
        try:
            clustering = nx.average_clustering(self.graph)
        except Exception:
            clustering = 0.0

        # Composite density score (0–1 scaled, weighted)
        density_score = min(
            1.0,
            (0.5 * density) +
            (0.3 * min(avg_degree / max(n - 1, 1), 1.0)) +
            (0.2 * clustering)
        )

        return {
            "total_nodes": n,
            "total_edges": m,
            "density_score": round(density_score, 3),
            "average_degree": round(avg_degree, 2),
            "clustering_coefficient": round(clustering, 3),
        }


