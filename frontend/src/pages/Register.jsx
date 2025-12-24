import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../utils/api'
import { setUser, setToken } from '../utils/auth'
import './Auth.css'

const Register = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    tenant_name: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Register user
      const response = await api.post('/api/v1/auth/register', formData)
      const user = response.data
      setUser(user)
      
      // Auto-login after registration
      const loginResponse = await api.post('/api/v1/auth/login', {
        email: formData.email,
        password: formData.password
      })
      
      const { access_token } = loginResponse.data
      
      if (!access_token) {
        throw new Error('No token received from server')
      }
      
      // Clean and store token
      const cleanToken = access_token.trim()
      setToken(cleanToken)
      
      // Update API client with token immediately
      api.defaults.headers.common['Authorization'] = `Bearer ${cleanToken}`
      
      // Small delay to ensure token is set
      await new Promise(resolve => setTimeout(resolve, 100))
      
      onLogin(cleanToken)
    } catch (err) {
      console.error('Registration error:', err)
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Create Account</h1>
          <p>Get started with document processing</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="label" htmlFor="full_name">Full Name</label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              className="input"
              value={formData.full_name}
              onChange={handleChange}
              required
              placeholder="John Doe"
            />
          </div>

          <div className="form-group">
            <label className="label" htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              className="input"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="you@example.com"
            />
          </div>

          <div className="form-group">
            <label className="label" htmlFor="tenant_name">Company Name</label>
            <input
              type="text"
              id="tenant_name"
              name="tenant_name"
              className="input"
              value={formData.tenant_name}
              onChange={handleChange}
              required
              placeholder="Acme Corporation"
            />
          </div>

          <div className="form-group">
            <label className="label" htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              className="input"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
              placeholder="••••••••"
            />
            <small style={{ color: 'var(--text-light)', marginTop: '0.25rem', display: 'block' }}>
              Must be at least 8 characters
            </small>
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? <span className="loading"></span> : 'Create Account'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Register

