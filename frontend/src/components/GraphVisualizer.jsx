/**
 * GraphVisualizer Component
 * Displays identity relationship graph using vis-network
 */

import React, { useEffect, useRef, useState } from 'react';
import { Network } from 'vis-network/standalone';
import { Maximize2, Minimize2, ZoomIn, ZoomOut, RefreshCw } from 'lucide-react';

const GraphVisualizer = ({ nodes, edges }) => {
  const containerRef = useRef(null);
  const networkRef = useRef(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    if (!containerRef.current || !nodes || !edges) return;

    // Calculate statistics
    calculateStats();

    // Format nodes for vis-network
    const formattedNodes = nodes.map(node => ({
      id: node.id,
      label: node.label || node.id,
      title: node.title || `${node.type}: ${node.label}`,
      group: node.type,
      color: getNodeColor(node.type),
      shape: getNodeShape(node.type),
      size: getNodeSize(node.type),
      font: {
        color: '#ffffff',
        size: 14,
        face: 'Inter'
      }
    }));

    // Format edges for vis-network
    const formattedEdges = edges.map(edge => ({
      from: edge.from,
      to: edge.to,
      label: edge.label || edge.type,
      title: edge.title || `${edge.type}${edge.year ? ` (${edge.year})` : ''}`,
      color: getEdgeColor(edge.year),
      width: 2,
      arrows: {
        to: { enabled: false }
      },
      font: {
        color: '#b8c5d6',
        size: 10,
        strokeWidth: 0
      }
    }));

    // Network options
    const options = {
      nodes: {
        borderWidth: 2,
        borderWidthSelected: 3,
        shadow: {
          enabled: true,
          color: 'rgba(0, 217, 255, 0.5)',
          size: 10,
          x: 0,
          y: 0
        }
      },
      edges: {
        smooth: {
          enabled: true,
          type: 'continuous',
          roundness: 0.5
        },
        shadow: {
          enabled: true,
          color: 'rgba(0, 0, 0, 0.3)',
          size: 5,
          x: 0,
          y: 0
        }
      },
      physics: {
        enabled: true,
        barnesHut: {
          gravitationalConstant: -8000,
          centralGravity: 0.3,
          springLength: 150,
          springConstant: 0.04,
          damping: 0.09,
          avoidOverlap: 0.5
        },
        stabilization: {
          iterations: 150
        }
      },
      interaction: {
        hover: true,
        tooltipDelay: 100,
        zoomView: true,
        dragView: true
      },
      layout: {
        improvedLayout: true
      }
    };

    // Create network
    const network = new Network(
      containerRef.current,
      { nodes: formattedNodes, edges: formattedEdges },
      options
    );

    networkRef.current = network;

    // Event listeners
    network.on('stabilizationIterationsDone', () => {
      network.setOptions({ physics: false });
    });

    // Cleanup
    return () => {
      if (network) {
        network.destroy();
      }
    };
  }, [nodes, edges]);

  const calculateStats = () => {
    if (!nodes || !edges) return;

    const nodeTypes = {};
    nodes.forEach(node => {
      nodeTypes[node.type] = (nodeTypes[node.type] || 0) + 1;
    });

    const edgesByAge = {
      old: 0,      // 10+ years
      medium: 0,   // 3-10 years
      recent: 0    // < 3 years
    };

    const currentYear = new Date().getFullYear();
    edges.forEach(edge => {
      if (edge.year) {
        const age = currentYear - edge.year;
        if (age >= 10) edgesByAge.old++;
        else if (age >= 3) edgesByAge.medium++;
        else edgesByAge.recent++;
      }
    });

    // Calculate graph density
    const maxEdges = (nodes.length * (nodes.length - 1)) / 2;
    const density = maxEdges > 0 ? (edges.length / maxEdges).toFixed(2) : 0;

    setStats({
      nodeCount: nodes.length,
      edgeCount: edges.length,
      density: density,
      nodeTypes: nodeTypes,
      edgesByAge: edgesByAge
    });
  };

  const getNodeColor = (type) => {
    const colors = {
      person: { background: '#00d9ff', border: '#0099cc' },
      email: { background: '#a855f7', border: '#7c3aed' },
      phone: { background: '#ec4899', border: '#db2777' },
      aadhaar: { background: '#10b981', border: '#059669' },
      pan: { background: '#f59e0b', border: '#d97706' },
      address: { background: '#6366f1', border: '#4f46e5' },
      profile: { background: '#14b8a6', border: '#0d9488' },
      breach: { background: '#ef4444', border: '#dc2626' }
    };
    return colors[type?.toLowerCase()] || { background: '#6b7280', border: '#4b5563' };
  };

  const getNodeShape = (type) => {
    const shapes = {
      person: 'dot',
      email: 'diamond',
      phone: 'triangle',
      aadhaar: 'box',
      pan: 'box',
      address: 'star',
      profile: 'hexagon',
      breach: 'triangleDown'
    };
    return shapes[type?.toLowerCase()] || 'dot';
  };

  const getNodeSize = (type) => {
    return type?.toLowerCase() === 'person' ? 30 : 20;
  };

  const getEdgeColor = (year) => {
    if (!year) return { color: '#6b7280', highlight: '#9ca3af' };
    
    const currentYear = new Date().getFullYear();
    const age = currentYear - year;

    if (age >= 10) return { color: '#10b981', highlight: '#34d399' }; // Green - old
    if (age >= 3) return { color: '#f59e0b', highlight: '#fbbf24' };  // Yellow - medium
    return { color: '#ef4444', highlight: '#f87171' };                // Red - recent
  };

  const handleZoomIn = () => {
    if (networkRef.current) {
      const scale = networkRef.current.getScale();
      networkRef.current.moveTo({ scale: scale * 1.2 });
    }
  };

  const handleZoomOut = () => {
    if (networkRef.current) {
      const scale = networkRef.current.getScale();
      networkRef.current.moveTo({ scale: scale * 0.8 });
    }
  };

  const handleReset = () => {
    if (networkRef.current) {
      networkRef.current.fit({ animation: { duration: 500, easingFunction: 'easeInOutQuad' } });
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  if (!nodes || nodes.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Identity Graph</h2>
          <p className="card-description">
            Relationship network visualization
          </p>
        </div>
        <div className="alert alert-info">
          <p style={{ fontSize: '0.875rem' }}>
            No graph data available. Graph visualization requires data from Layer 2&3 (OSINT + Graph Analysis).
          </p>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="card" 
      style={{ 
        position: isFullscreen ? 'fixed' : 'relative',
        top: isFullscreen ? 0 : 'auto',
        left: isFullscreen ? 0 : 'auto',
        width: isFullscreen ? '100vw' : 'auto',
        height: isFullscreen ? '100vh' : 'auto',
        zIndex: isFullscreen ? 9999 : 'auto',
        margin: isFullscreen ? 0 : 'auto'
      }}
    >
      <div className="card-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 className="card-title">Identity Graph</h2>
            <p className="card-description">
              Relationship network analysis - {stats?.nodeCount || 0} nodes, {stats?.edgeCount || 0} connections
            </p>
          </div>

          {/* Controls */}
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={handleZoomIn}
              className="btn btn-secondary"
              style={{ padding: '0.5rem' }}
              title="Zoom In"
            >
              <ZoomIn size={20} />
            </button>
            <button
              onClick={handleZoomOut}
              className="btn btn-secondary"
              style={{ padding: '0.5rem' }}
              title="Zoom Out"
            >
              <ZoomOut size={20} />
            </button>
            <button
              onClick={handleReset}
              className="btn btn-secondary"
              style={{ padding: '0.5rem' }}
              title="Reset View"
            >
              <RefreshCw size={20} />
            </button>
            <button
              onClick={toggleFullscreen}
              className="btn btn-secondary"
              style={{ padding: '0.5rem' }}
              title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
            >
              {isFullscreen ? <Minimize2 size={20} /> : <Maximize2 size={20} />}
            </button>
          </div>
        </div>
      </div>

      {/* Graph Container */}
      <div
        ref={containerRef}
        style={{
          width: '100%',
          height: isFullscreen ? 'calc(100vh - 200px)' : '500px',
          background: 'rgba(0, 0, 0, 0.3)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}
      />

      {/* Legend & Stats */}
      {stats && (
        <div style={{ 
          marginTop: '1.5rem',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem'
        }}>
          {/* Graph Density */}
          <div style={{
            padding: '1rem',
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
              Graph Density
            </div>
            <div style={{ 
              fontSize: '1.5rem', 
              fontWeight: 700,
              color: stats.density > 1.5 ? 'var(--color-verified)' : stats.density > 1.0 ? 'var(--color-suspicious)' : 'var(--color-reject)'
            }}>
              {stats.density}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              {stats.density > 1.5 ? '✅ Dense network' : stats.density > 1.0 ? '⚠️ Moderate' : '🚨 Sparse'}
            </div>
          </div>

          {/* Edge Age Distribution */}
          <div style={{
            padding: '1rem',
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
              Relationship Age
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--color-verified)' }}>🟢 10+ years:</span>
                <span style={{ fontWeight: 600 }}>{stats.edgesByAge.old}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--color-suspicious)' }}>🟡 3-10 years:</span>
                <span style={{ fontWeight: 600 }}>{stats.edgesByAge.medium}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--color-reject)' }}>🔴 &lt;3 years:</span>
                <span style={{ fontWeight: 600 }}>{stats.edgesByAge.recent}</span>
              </div>
            </div>
          </div>

          {/* Node Types */}
          <div style={{
            padding: '1rem',
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
              Node Types
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: '0.75rem' }}>
              {Object.entries(stats.nodeTypes).map(([type, count]) => (
                <div key={type} style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ textTransform: 'capitalize' }}>{type}:</span>
                  <span style={{ fontWeight: 600 }}>{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Interpretation */}
      <div className="alert alert-info" style={{ marginTop: '1.5rem', marginBottom: 0 }}>
        <div>
          <p style={{ fontSize: '0.875rem', marginBottom: '0.5rem', fontWeight: 600 }}>
            Graph Interpretation
          </p>
          <p style={{ fontSize: '0.75rem', lineHeight: 1.5 }}>
            <strong style={{ color: 'var(--color-verified)' }}>Real identities:</strong> Dense networks with 15+ nodes, 
            multiple 10+ year old connections (green edges), high graph density (&gt;1.5)
            <br />
            <strong style={{ color: 'var(--color-reject)' }}>Synthetic identities:</strong> Sparse networks with 3-5 nodes, 
            all recent connections (red edges), low graph density (&lt;1.0)
          </p>
        </div>
      </div>
    </div>
  );
};

export default GraphVisualizer;