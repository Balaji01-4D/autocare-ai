import React, { useState, useEffect } from 'react'
import AuthPage from './components/AuthPage'
import Dashboard from './components/Dashboard'
import { authService } from './services/auth'
import './App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is authenticated on app load
    const checkAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          // Verify token by trying to get profile
          await authService.getProfile()
          setIsAuthenticated(true)
        } else {
          setIsAuthenticated(false)
        }
      } catch (error) {
        // Token is invalid, clear it
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        setIsAuthenticated(false)
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: '#ffffff'
      }}>
        <div style={{ color: '#333', fontSize: '18px' }}>Loading...</div>
      </div>
    )
  }

  // Route based on authentication status
  const currentPath = window.location.pathname

  if (currentPath === '/dashboard') {
    return isAuthenticated ? <Dashboard /> : <AuthPage />
  }

  return isAuthenticated ? <Dashboard /> : <AuthPage />
}

export default App
