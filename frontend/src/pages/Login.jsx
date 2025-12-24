import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../utils/api'
import { setUser, setToken } from '../utils/auth'
import './Auth.css'

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
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
      const response = await api.post('/api/v1/auth/login', formData)
      const { access_token } = response.data
      
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
      
      // Get user info with the token
      const userResponse = await api.get('/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${cleanToken}`
        }
      })
      setUser(userResponse.data)
      
      onLogin(cleanToken)
    } catch (err) {
      console.error('Login error:', err)
      console.error('Error details:', err.response?.data)
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Document Processing Platform</h1>
          <p>Sign in to your account</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
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
            <label className="label" htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              className="input"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="••••••••"
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? <span className="loading"></span> : 'Sign In'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Don't have an account? <Link to="/register">Sign up</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login

