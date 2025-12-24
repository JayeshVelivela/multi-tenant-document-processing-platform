import React, { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import api from '../utils/api'
import { getUser } from '../utils/auth'
import './Dashboard.css'

const Dashboard = ({ onLogout }) => {
  const [user, setUser] = useState(null)
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    processing: 0,
    completed: 0,
    failed: 0
  })
  const [loading, setLoading] = useState(true)
  const location = useLocation()

  useEffect(() => {
    loadData()
    // Refresh data every 5 seconds to see status updates (without showing loading)
    const interval = setInterval(() => loadData(false), 5000)
    return () => clearInterval(interval)
  }, [])

  // Refresh when navigating back to dashboard
  useEffect(() => {
    if (location.pathname === '/dashboard') {
      loadData(false) // Refresh without showing loading spinner
    }
  }, [location.pathname])

  const loadData = async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true)
      }
      
      const userData = getUser()
      if (userData) {
        setUser(userData)
      } else {
        const response = await api.get('/api/v1/auth/me')
        setUser(response.data)
      }

      // Fetch all documents with max page size to get accurate counts
      // API limit is 100, so we'll fetch all pages if needed
      let allDocuments = []
      let page = 1
      let hasMore = true
      
      while (hasMore) {
        const docsResponse = await api.get('/api/v1/documents/', {
          params: { page, page_size: 100 }
        })
        const { items, total, total_pages } = docsResponse.data
        allDocuments = allDocuments.concat(items)
        
        if (page >= total_pages) {
          hasMore = false
        } else {
          page++
        }
      }

      setStats({
        total: allDocuments.length,
        pending: allDocuments.filter(d => d.status === 'pending').length,
        processing: allDocuments.filter(d => d.status === 'processing').length,
        completed: allDocuments.filter(d => d.status === 'completed').length,
        failed: allDocuments.filter(d => d.status === 'failed').length
      })
    } catch (err) {
      console.error('Failed to load data:', err)
      // Set error state but don't break the UI
      setStats({
        total: 0,
        pending: 0,
        processing: 0,
        completed: 0,
        failed: 0
      })
    } finally {
      if (showLoading) {
        setLoading(false)
      }
    }
  }

  const handleLogout = () => {
    onLogout()
  }

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading"></div>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <nav className="navbar">
        <div className="container">
          <div className="navbar-content">
            <h2>Document Platform</h2>
            <div className="navbar-actions">
              <Link to="/documents" className="btn btn-secondary">Documents</Link>
              <button onClick={handleLogout} className="btn btn-secondary">Logout</button>
            </div>
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="container">
          <div className="dashboard-header">
            <h1>Welcome back, {user?.full_name || user?.email}!</h1>
            <p>Manage and process your documents</p>
          </div>

          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon" style={{ background: '#dbeafe' }}>
                📄
              </div>
              <div className="stat-info">
                <h3>{stats.total}</h3>
                <p>Total Documents</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon" style={{ background: '#fef3c7' }}>
                ⏳
              </div>
              <div className="stat-info">
                <h3>{stats.pending}</h3>
                <p>Pending</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon" style={{ background: '#dbeafe' }}>
                🔄
              </div>
              <div className="stat-info">
                <h3>{stats.processing}</h3>
                <p>Processing</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon" style={{ background: '#d1fae5' }}>
                ✅
              </div>
              <div className="stat-info">
                <h3>{stats.completed}</h3>
                <p>Completed</p>
              </div>
            </div>
          </div>

          <div className="dashboard-actions">
            <Link to="/documents" className="btn btn-primary">
              View All Documents →
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

