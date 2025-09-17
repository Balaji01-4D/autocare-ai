import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import LoginForm from './LoginForm';
import SignupForm from './SignupForm';
import './AuthPage.css';

const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);

  const handleSwitchToSignup = () => setIsLogin(false);
  const handleSwitchToLogin = () => setIsLogin(true);

  const handleAuthSuccess = () => {
    // Refresh the page to trigger authentication state check
    window.location.href = '/';
  };

  return (
    <div className="auth-page-wrapper">
      <Link to="/" className="back-to-home">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </Link>
      
      <div className="auth-container fade">
        {isLogin ? (
          <LoginForm 
            onSwitchToSignup={handleSwitchToSignup}
            onLoginSuccess={handleAuthSuccess}
          />
        ) : (
          <SignupForm 
            onSwitchToLogin={handleSwitchToLogin}
            onSignupSuccess={handleAuthSuccess}
          />
        )}
        <div className="image-section">
          <div className="overlay"></div>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
