/**
 * DocumentUpload Component
 * Allows users to upload identity documents (Aadhaar, PAN, etc.)
 */

import React, { useState, useRef } from 'react';
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react';

const DocumentUpload = ({ onDocumentsChange, isLoading }) => {
  const [documents, setDocuments] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
  const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (files) => {
    const newDocuments = [];
    const errors = [];

    Array.from(files).forEach((file) => {
      // Check file type
      if (!ALLOWED_TYPES.includes(file.type)) {
        errors.push(`${file.name}: Invalid file type. Only JPG, PNG, WEBP allowed.`);
        return;
      }

      // Check file size
      if (file.size > MAX_FILE_SIZE) {
        errors.push(`${file.name}: File too large. Maximum size is 5MB.`);
        return;
      }

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        const newDoc = {
          id: Math.random().toString(36).substr(2, 9),
          file: file,
          type: guessDocumentType(file.name),
          preview: e.target.result,
          name: file.name,
          size: file.size,
          status: 'ready'
        };

        setDocuments(prev => {
          const updated = [...prev, newDoc];
          onDocumentsChange(updated);
          return updated;
        });
      };
      reader.readAsDataURL(file);
    });

    // Show errors if any
    if (errors.length > 0) {
      alert(errors.join('\n'));
    }
  };

  const guessDocumentType = (filename) => {
    const lower = filename.toLowerCase();
    if (lower.includes('aadhaar') || lower.includes('aadhar')) {
      return 'aadhaar_card';
    } else if (lower.includes('pan')) {
      return 'pan_card';
    }
    return 'other';
  };

  const handleDocumentTypeChange = (docId, newType) => {
    setDocuments(prev => {
      const updated = prev.map(doc =>
        doc.id === docId ? { ...doc, type: newType } : doc
      );
      onDocumentsChange(updated);
      return updated;
    });
  };

  const removeDocument = (docId) => {
    setDocuments(prev => {
      const updated = prev.filter(doc => doc.id !== docId);
      onDocumentsChange(updated);
      return updated;
    });
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const onButtonClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Document Upload</h2>
        <p className="card-description">
          Upload identity documents for verification (Aadhaar, PAN, etc.)
        </p>
      </div>

      {/* Upload Area */}
      <div
        className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={onButtonClick}
        style={{
          border: `2px dashed ${dragActive ? 'var(--accent-cyan)' : 'rgba(255, 255, 255, 0.2)'}`,
          borderRadius: 'var(--radius-lg)',
          padding: '2rem',
          textAlign: 'center',
          cursor: 'pointer',
          background: dragActive ? 'rgba(0, 217, 255, 0.05)' : 'rgba(255, 255, 255, 0.02)',
          transition: 'all 0.2s ease',
          marginBottom: documents.length > 0 ? '1.5rem' : '0'
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/jpeg,image/jpg,image/png,image/webp"
          onChange={handleChange}
          style={{ display: 'none' }}
          disabled={isLoading}
        />

        <Upload
          size={48}
          style={{
            color: dragActive ? 'var(--accent-cyan)' : 'var(--text-muted)',
            marginBottom: '1rem'
          }}
        />

        <p style={{ fontSize: '1rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
          {dragActive ? 'Drop files here' : 'Click to upload or drag and drop'}
        </p>

        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          JPG, PNG, WEBP up to 5MB
        </p>
      </div>

      {/* Uploaded Documents List */}
      {documents.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {documents.map((doc) => (
            <div
              key={doc.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                padding: '1rem',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 'var(--radius-md)',
              }}
            >
              {/* Preview Thumbnail */}
              <div
                style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: 'var(--radius-sm)',
                  overflow: 'hidden',
                  flexShrink: 0,
                  background: 'rgba(255, 255, 255, 0.05)'
                }}
              >
                {doc.preview ? (
                  <img
                    src={doc.preview}
                    alt={doc.name}
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover'
                    }}
                  />
                ) : (
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    height: '100%' 
                  }}>
                    <FileText size={32} style={{ color: 'var(--text-muted)' }} />
                  </div>
                )}
              </div>

              {/* Document Info */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                  <p style={{ 
                    fontSize: '0.875rem', 
                    fontWeight: 500,
                    color: 'var(--text-primary)',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}>
                    {doc.name}
                  </p>
                  {doc.status === 'ready' && (
                    <CheckCircle size={16} style={{ color: 'var(--color-verified)', flexShrink: 0 }} />
                  )}
                </div>

                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                  {formatFileSize(doc.size)}
                </p>

                {/* Document Type Selector */}
                <select
                  value={doc.type}
                  onChange={(e) => handleDocumentTypeChange(doc.id, e.target.value)}
                  disabled={isLoading}
                  style={{
                    padding: '0.25rem 0.5rem',
                    fontSize: '0.75rem',
                    background: 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--text-primary)',
                    cursor: 'pointer'
                  }}
                >
                  <option value="aadhaar_card">Aadhaar Card</option>
                  <option value="pan_card">PAN Card</option>
                  <option value="other">Other Document</option>
                </select>
              </div>

              {/* Remove Button */}
              <button
                onClick={() => removeDocument(doc.id)}
                disabled={isLoading}
                style={{
                  padding: '0.5rem',
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid var(--color-reject)',
                  borderRadius: 'var(--radius-sm)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.2s ease',
                  flexShrink: 0
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = 'rgba(239, 68, 68, 0.2)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
                }}
              >
                <X size={20} style={{ color: 'var(--color-reject)' }} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Info Message */}
      {documents.length === 0 && (
        <div 
          className="alert alert-info" 
          style={{ 
            marginTop: '1rem',
            marginBottom: 0
          }}
        >
          <AlertCircle size={20} />
          <div>
            <p style={{ fontSize: '0.875rem', marginBottom: '0.25rem', fontWeight: 500 }}>
              Document upload is optional
            </p>
            <p style={{ fontSize: '0.75rem', opacity: 0.8 }}>
              You can verify identity with just the form data, or upload documents for more comprehensive analysis.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;