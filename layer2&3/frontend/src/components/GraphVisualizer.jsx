import React, { useEffect, useRef } from 'react';
import { Network } from 'vis-network';

function GraphVisualizer({ result }) {
  const containerRef = useRef(null);
  const networkRef = useRef(null);

  useEffect(() => {
    if (!result.nodes || result.nodes.length === 0) return;

    const visNodes = result.nodes.map(node => ({
      id: node.id,
      label: node.label,
      color: {
        background: node.color,
        border: node.color,
        highlight: {
          background: '#fafafa',
          border: node.color,
        },
        hover: {
          background: node.color,
          border: '#fafafa',
        }
      },
      font: {
        color: '#a1a1aa',
        size: 11,
        face: 'Inter, system-ui, sans-serif',
      },
      size: node.size,
      shape: getShape(node.type),
      title: buildTooltip(node),
      borderWidth: 2,
    }));

    const visEdges = result.edges.map((edge, i) => {
      // Highlight VERIFIED_TOGETHER edges (strong cross-reference evidence)
      const isVerified = edge.relationship_type === 'VERIFIED_TOGETHER';
      const isMentioned = edge.relationship_type === 'MENTIONED_IN';
      
      return {
        id: i,
        from: edge.from_node,
        to: edge.to_node,
        color: {
          color: isVerified ? '#10b981' : (edge.color + '80'),
          highlight: '#10b981',
          hover: '#10b981',
        },
        font: {
          color: isVerified ? '#10b981' : '#52525b',
          size: 9,
          align: 'middle',
          face: 'Inter, system-ui, sans-serif',
        },
        smooth: {
          type: 'curvedCW',
          roundness: 0.15,
        },
        width: isVerified ? 3 : (isMentioned ? 2 : 1.5),
        dashes: isMentioned ? [5, 5] : false,
      };
    });

    const data = { nodes: visNodes, edges: visEdges };

    const options = {
      physics: {
        enabled: true,
        stabilization: {
          iterations: 100,
          fit: true,
        },
        barnesHut: {
          gravitationalConstant: -6000,
          springLength: 180,
          springConstant: 0.03,
          damping: 0.3,
        },
      },
      interaction: {
        hover: true,
        tooltipDelay: 100,
        zoomView: true,
        dragView: true,
        hideEdgesOnDrag: true,
      },
      nodes: {
        shadow: {
          enabled: true,
          color: 'rgba(0,0,0,0.3)',
          size: 8,
          x: 0,
          y: 2,
        },
      },
      edges: {
        shadow: false,
        arrows: { to: { enabled: false } },
      },
    };

    if (containerRef.current) {
      networkRef.current = new Network(containerRef.current, data, options);
    }

    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
      }
    };
  }, [result.nodes, result.edges]);

  function getShape(type) {
    const shapes = {
      'Person': 'dot',
      'Email': 'diamond',
      'Phone': 'triangle',
      'Aadhaar': 'square',
      'PAN': 'square',
      'Address': 'hexagon',
      'SocialProfile': 'star',
      'Domain': 'dot',
      'Breach': 'triangleDown',
    };
    return shapes[type] || 'dot';
  }

  function buildTooltip(node) {
    let tooltip = `<div style="background: #18181b; padding: 10px 14px; border-radius: 8px; color: #fafafa; font-family: Inter, system-ui, sans-serif; font-size: 12px; border: 1px solid #27272a; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">`;
    tooltip += `<div style="font-weight: 600; margin-bottom: 4px; color: #10b981;">${node.type}</div>`;
    tooltip += `<div style="margin-bottom: 6px;">${node.label}</div>`;
    
    if (node.properties) {
      Object.entries(node.properties).forEach(([key, value]) => {
        if (value !== null && value !== undefined && key !== 'dob') {
          tooltip += `<div style="font-size: 11px; color: #71717a;"><span style="color: #a1a1aa;">${key}:</span> ${value}</div>`;
        }
      });
    }
    
    tooltip += `</div>`;
    return tooltip;
  }

  const legendItems = [
    { type: 'Person', color: '#4CAF50' },
    { type: 'Email', color: '#2196F3' },
    { type: 'Phone', color: '#9C27B0' },
    { type: 'Aadhaar', color: '#FF9800' },
    { type: 'PAN', color: '#FF5722' },
    { type: 'Profile', color: '#00BCD4' },
    { type: 'Domain', color: '#607D8B' },
  ];

  if (!result.nodes || result.nodes.length === 0) {
    return (
      <div className="empty-state" style={{ height: '300px' }}>
        <div className="empty-state-icon">🕸️</div>
        <p className="empty-state-text">No graph data available</p>
      </div>
    );
  }

  return (
    <div>
      <div ref={containerRef} className="graph-container" />
      
      <div className="graph-legend">
        {legendItems.map((item, i) => (
          <div key={i} className="legend-item">
            <span className="legend-color" style={{ backgroundColor: item.color }} />
            <span>{item.type}</span>
          </div>
        ))}
      </div>

      <div className="graph-stats">
        <span>Nodes: <strong>{result.nodes.length}</strong></span>
        <span>Edges: <strong>{result.edges.length}</strong></span>
        {result.cross_reference_count > 0 && (
          <span style={{ color: '#10b981' }}>
            Cross-Refs: <strong>{result.cross_reference_count}</strong>
          </span>
        )}
        {result.oldest_relationship_years > 0 && (
          <span>Oldest: <strong>{result.oldest_relationship_years.toFixed(1)}y</strong></span>
        )}
      </div>
    </div>
  );
}

export default GraphVisualizer;
