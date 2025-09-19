import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './components/Home'
import Models from './components/Models'
import CarDetail from './components/CarDetail'
import Service from './components/Service'
import Chatbot from './components/Chatbot'
import AuthPage from './components/AuthPage'
import Dashboard from './components/Dashboard'
import ProtectedRoute from './components/ProtectedRoute'
import { authService } from './services/auth'
import './App.css'

// Component to handle conditional navbar rendering
const AppContent = ({ isAuthenticated, setIsAuthenticated }: { 
  isAuthenticated: boolean, 
  setIsAuthenticated: (auth: boolean) => void 
}) => {
  const location = useLocation();
  const hideNavbarRoutes = ['/auth', '/chatbot'];
  const shouldHideNavbar = hideNavbarRoutes.includes(location.pathname);

  return (
    <div className="App">
      {!shouldHideNavbar && (
        <Navbar 
          isAuthenticated={isAuthenticated} 
          setIsAuthenticated={setIsAuthenticated} 
        />
      )}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/models" element={<Models />} />
        <Route path="/models/:id" element={<CarDetail />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/dashboard" element={
          <ProtectedRoute isAuthenticated={isAuthenticated}>
            <Dashboard />
          </ProtectedRoute>
        } />
        <Route path="/service" element={
          <ProtectedRoute isAuthenticated={isAuthenticated}>
            <Service />
          </ProtectedRoute>
        } />
        <Route path="/chatbot" element={
          <ProtectedRoute isAuthenticated={isAuthenticated}>
            <Chatbot />
          </ProtectedRoute>
        } />
      </Routes>
    </div>
  );
};

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

  return (
    <Router>
      <AppContent 
        isAuthenticated={isAuthenticated || false} 
        setIsAuthenticated={setIsAuthenticated} 
      />
    </Router>
  )
}

export default App
