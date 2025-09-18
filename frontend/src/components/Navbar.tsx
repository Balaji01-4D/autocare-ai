import React from 'react';
import { Link } from 'react-router-dom';
import { authService } from '../services/auth';
import BMWLogo from './BMWLogo';
import './Navbar.css';

interface NavbarProps {
  isAuthenticated: boolean;
  setIsAuthenticated: (auth: boolean) => void;
}

const Navbar: React.FC<NavbarProps> = ({ isAuthenticated, setIsAuthenticated }) => {
  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        {/* Logo */}
        <Link to="/" className="nav-logo">
          <BMWLogo size={50} />
          <div>
            <span className="logo-text">BMW India</span>
            <span className="tagline">Sheer Driving Pleasure</span>
          </div>
        </Link>

        {/* Navigation Links */}
        <div className="nav-menu">
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/models" className="nav-link">Models</Link>
          
          {/* Protected Routes */}
          {isAuthenticated ? (
            <>
              <Link to="/service" className="nav-link">Service</Link>
              <Link to="/chatbot" className="nav-link">AI Chatbot</Link>
              <button onClick={handleLogout} className="nav-button logout-btn">
                Logout
              </button>
            </>
          ) : (
            <Link to="/auth" className="nav-button login-btn">
              Login / Register
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
