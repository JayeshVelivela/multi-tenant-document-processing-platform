import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../utils/api'
import './Documents.css'

const Documents = ({ onLogout }) => {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [filter, setFilter] = useState('all')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [uploadSuccess, setUploadSuccess] = useState(null)
  const [uploadedDocument, setUploadedDocument] = useState(null)

  useEffect(() => {
    loadDocuments()
    // Refresh documents every 3 seconds to see status updates (without showing loading)
    const interval = setInterval(() => loadDocuments(false), 3000)
    return () => clearInterval(interval)
  }, [filter, page])

  const loadDocuments = async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true)
      }
      const params = { page, page_size: 20 }
      if (filter !== 'all') {
        params.status = filter
      }
      
      const response = await api.get('/api/v1/documents/', { params })
      setDocuments(response.data.items)
      setTotalPages(response.data.total_pages)
    } catch (err) {
      console.error('Failed to load documents:', err)
    } finally {
      if (showLoading) {
        setLoading(false)
      }
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    setUploadSuccess(null)
    setUploadedDocument(null)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await api.post('/api/v1/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      const uploadedDoc = response.data
      setUploadedDocument(uploadedDoc)
      setUploadSuccess({
        message: `Successfully uploaded "${uploadedDoc.original_filename}"!`,
        documentId: uploadedDoc.id
      })
      
      // Reload documents to show the new one (without showing loading spinner)
      await loadDocuments(false)
      
      // Scroll to show the uploaded document
      setTimeout(() => {
        const uploadedElement = document.querySelector(`[data-document-id="${uploadedDoc.id}"]`)
        if (uploadedElement) {
          uploadedElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }, 100)
      
      // Clear success message after 5 seconds
      setTimeout(() => {
        setUploadSuccess(null)
        setUploadedDocument(null)
      }, 5000)
      
      e.target.value = '' // Reset input
    } catch (err) {
      setUploadSuccess({
        message: err.response?.data?.detail || 'Upload failed',
        isError: true
      })
      setTimeout(() => setUploadSuccess(null), 5000)
    } finally {
      setUploading(false)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'badge-pending',
      processing: 'badge-processing',
      completed: 'badge-completed',
      failed: 'badge-failed'
    }
    return badges[status] || 'badge-pending'
  }

  return (
    <div className="documents">
      <nav className="navbar">
        <div className="container">
          <div className="navbar-content">
            <h2>Document Platform</h2>
            <div className="navbar-actions">
              <Link to="/dashboard" className="btn btn-secondary">Dashboard</Link>
              <button onClick={onLogout} className="btn btn-secondary">Logout</button>
            </div>
          </div>
        </div>
      </nav>

      <div className="documents-content">
        <div className="container">
          <div className="documents-header">
            <h1>Documents</h1>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <button
                className="btn btn-secondary"
                onClick={async () => {
                  try {
                    const response = await api.get('/api/v1/documents/export/json', {
                      responseType: 'blob'
                    })
                    const url = window.URL.createObjectURL(new Blob([response.data]))
                    const link = document.createElement('a')
                    link.href = url
                    link.setAttribute('download', 'documents_export.json')
                    document.body.appendChild(link)
                    link.click()
                    link.remove()
                  } catch (err) {
                    console.error('Export failed:', err)
                    alert('Failed to export data')
                  }
                }}
              >
                📥 Export JSON
              </button>
              <button
                className="btn btn-secondary"
                onClick={async () => {
                  try {
                    const response = await api.get('/api/v1/documents/export/csv', {
                      responseType: 'blob'
                    })
                    const url = window.URL.createObjectURL(new Blob([response.data]))
                    const link = document.createElement('a')
                    link.href = url
                    link.setAttribute('download', 'documents_export.csv')
                    document.body.appendChild(link)
                    link.click()
                    link.remove()
                  } catch (err) {
                    console.error('Export failed:', err)
                    alert('Failed to export data')
                  }
                }}
              >
                📊 Export CSV
              </button>
              <label className="upload-btn">
                <input
                  type="file"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  style={{ display: 'none' }}
                  accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg"
                />
                {uploading ? (
                  <span className="btn btn-primary" disabled>
                    <span className="loading"></span> Uploading...
                  </span>
                ) : (
                  <span className="btn btn-primary">📤 Upload Document</span>
                )}
              </label>
            </div>
          </div>

          {uploadSuccess && (
            <div className={`upload-message ${uploadSuccess.isError ? 'error' : 'success'}`}>
              <div className="message-content">
                <span>{uploadSuccess.isError ? '❌' : '✅'}</span>
                <span>{uploadSuccess.message}</span>
                {uploadedDocument && !uploadSuccess.isError && (
                  <span className="message-action">
                    Document is being processed. Check back in a few seconds to see extracted metadata!
                  </span>
                )}
              </div>
              <button 
                className="message-close"
                onClick={() => {
                  setUploadSuccess(null)
                  setUploadedDocument(null)
                }}
              >
                ×
              </button>
            </div>
          )}

          <div className="filter-tabs">
            <button
              className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
              onClick={() => { setFilter('all'); setPage(1) }}
            >
              All
            </button>
            <button
              className={`filter-tab ${filter === 'pending' ? 'active' : ''}`}
              onClick={() => { setFilter('pending'); setPage(1) }}
            >
              Pending
            </button>
            <button
              className={`filter-tab ${filter === 'processing' ? 'active' : ''}`}
              onClick={() => { setFilter('processing'); setPage(1) }}
            >
              Processing
            </button>
            <button
              className={`filter-tab ${filter === 'completed' ? 'active' : ''}`}
              onClick={() => { setFilter('completed'); setPage(1) }}
            >
              Completed
            </button>
            <button
              className={`filter-tab ${filter === 'failed' ? 'active' : ''}`}
              onClick={() => { setFilter('failed'); setPage(1) }}
            >
              Failed
            </button>
          </div>

          {loading ? (
            <div className="loading-container">
              <div className="loading"></div>
            </div>
          ) : documents.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <h3>No documents found</h3>
              <p>Upload your first document to get started</p>
            </div>
          ) : (
            <>
              <div className="documents-grid">
                {documents.map((doc) => (
                  <div key={doc.id} className="document-card fade-in" data-document-id={doc.id}>
                    <div className="document-header">
                      <h3>{doc.original_filename}</h3>
                      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <a
                          href={`/api/v1/documents/${doc.id}/download`}
                          className="btn btn-small"
                          style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                          download
                          onClick={(e) => {
                            // Ensure auth header is included
                            e.preventDefault()
                            api.get(`/api/v1/documents/${doc.id}/download`, {
                              responseType: 'blob'
                            }).then(response => {
                              const url = window.URL.createObjectURL(new Blob([response.data]))
                              const link = document.createElement('a')
                              link.href = url
                              link.setAttribute('download', doc.original_filename)
                              document.body.appendChild(link)
                              link.click()
                              link.remove()
                            }).catch(err => {
                              console.error('Download failed:', err)
                              alert('Failed to download document')
                            })
                          }}
                        >
                          📥 Download
                        </a>
                        <span className={`badge ${getStatusBadge(doc.status)}`}>
                          {doc.status}
                        </span>
                      </div>
                    </div>
                    
                    <div className="document-info">
                      <p><strong>Size:</strong> {formatFileSize(doc.file_size)}</p>
                      <p><strong>Uploaded:</strong> {formatDate(doc.created_at)}</p>
                      {doc.processed_at && (
                        <p><strong>Processed:</strong> {formatDate(doc.processed_at)}</p>
                      )}
                    </div>

                    {doc.status === 'pending' && (
                      <div className="status-info">
                        <p>⏳ <strong>Status:</strong> Waiting to be processed. The document will be processed automatically.</p>
                      </div>
                    )}
                    
                    {doc.status === 'processing' && (
                      <div className="status-info processing">
                        <p>🔄 <strong>Status:</strong> Processing document... Extracting metadata. This usually takes 2-5 seconds.</p>
                      </div>
                    )}
                    
                    {doc.status === 'completed' && !doc.extracted_metadata && (
                      <div className="status-info">
                        <p>✅ <strong>Status:</strong> Processing completed. Metadata will appear shortly.</p>
                      </div>
                    )}

                    {doc.extracted_metadata && (
                      <div className="document-metadata">
                        <h4>📊 Extracted Metadata:</h4>
                        <div className="metadata-content">
                          <div className="metadata-grid">
                            <div className="metadata-item">
                              <span className="metadata-label">Document Type:</span>
                              <span className="metadata-value">{doc.extracted_metadata.document_type || 'N/A'}</span>
                            </div>
                            <div className="metadata-item">
                              <span className="metadata-label">Pages:</span>
                              <span className="metadata-value">{doc.extracted_metadata.page_count || 'N/A'}</span>
                            </div>
                            <div className="metadata-item">
                              <span className="metadata-label">Words:</span>
                              <span className="metadata-value">{doc.extracted_metadata.word_count || 'N/A'}</span>
                            </div>
                            <div className="metadata-item">
                              <span className="metadata-label">Language:</span>
                              <span className="metadata-value">{doc.extracted_metadata.language || 'N/A'}</span>
                            </div>
                          </div>
                          {doc.extracted_metadata.summary && (
                            <div className="summary">
                              <strong>📝 Summary:</strong>
                              <p>{doc.extracted_metadata.summary}</p>
                            </div>
                          )}
                          {doc.extracted_metadata.content_categories && doc.extracted_metadata.content_categories.length > 0 && (
                            <div className="categories">
                              <strong>🏷️ Categories:</strong>
                              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                                {doc.extracted_metadata.content_categories.map((cat, idx) => (
                                  <span key={idx} style={{ 
                                    background: '#e0e7ff', 
                                    padding: '0.25rem 0.5rem', 
                                    borderRadius: '0.25rem',
                                    fontSize: '0.875rem'
                                  }}>
                                    {cat}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          {doc.extracted_metadata.entities && (
                            <div className="entities">
                              <h5>Extracted Entities:</h5>
                              {doc.extracted_metadata.entities.dates && doc.extracted_metadata.entities.dates.length > 0 && (
                                <div className="entity-group">
                                  <strong>📅 Dates:</strong> {doc.extracted_metadata.entities.dates.slice(0, 5).join(', ')}
                                  {doc.extracted_metadata.entities.dates.length > 5 && ` (+${doc.extracted_metadata.entities.dates.length - 5} more)`}
                                </div>
                              )}
                              {doc.extracted_metadata.entities.amounts && doc.extracted_metadata.entities.amounts.length > 0 && (
                                <div className="entity-group">
                                  <strong>💰 Amounts:</strong> {doc.extracted_metadata.entities.amounts.slice(0, 5).join(', ')}
                                  {doc.extracted_metadata.entities.amounts.length > 5 && ` (+${doc.extracted_metadata.entities.amounts.length - 5} more)`}
                                </div>
                              )}
                              {doc.extracted_metadata.entities.companies && doc.extracted_metadata.entities.companies.length > 0 && (
                                <div className="entity-group">
                                  <strong>🏢 Companies/Organizations:</strong> {doc.extracted_metadata.entities.companies.slice(0, 5).join(', ')}
                                  {doc.extracted_metadata.entities.companies.length > 5 && ` (+${doc.extracted_metadata.entities.companies.length - 5} more)`}
                                </div>
                              )}
                              {doc.extracted_metadata.entities.emails && doc.extracted_metadata.entities.emails.length > 0 && (
                                <div className="entity-group">
                                  <strong>📧 Email Addresses:</strong> {doc.extracted_metadata.entities.emails.join(', ')}
                                </div>
                              )}
                              {doc.extracted_metadata.entities.phone_numbers && doc.extracted_metadata.entities.phone_numbers.length > 0 && (
                                <div className="entity-group">
                                  <strong>📞 Phone Numbers:</strong> {doc.extracted_metadata.entities.phone_numbers.join(', ')}
                                </div>
                              )}
                              {doc.extracted_metadata.entities.urls && doc.extracted_metadata.entities.urls.length > 0 && (
                                <div className="entity-group">
                                  <strong>🔗 URLs:</strong> {doc.extracted_metadata.entities.urls.slice(0, 3).map(url => (
                                    <a key={url} href={url} target="_blank" rel="noopener noreferrer" style={{ marginLeft: '0.5rem' }}>
                                      {url.length > 50 ? url.substring(0, 50) + '...' : url}
                                    </a>
                                  ))}
                                </div>
                              )}
                              {doc.extracted_metadata.entities.keywords && doc.extracted_metadata.entities.keywords.length > 0 && (
                                <div className="entity-group">
                                  <strong>🔑 Key Topics:</strong> {doc.extracted_metadata.entities.keywords.slice(0, 10).join(', ')}
                                </div>
                              )}
                            </div>
                          )}
                          {doc.extracted_metadata.extracted_text_preview && (
                            <div className="text-preview">
                              <strong>Text Preview:</strong>
                              <p>{doc.extracted_metadata.extracted_text_preview}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {doc.error_message && (
                      <div className="error-message">
                        <strong>Error:</strong> {doc.error_message}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    className="btn btn-secondary"
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    Previous
                  </button>
                  <span>Page {page} of {totalPages}</span>
                  <button
                    className="btn btn-secondary"
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default Documents

