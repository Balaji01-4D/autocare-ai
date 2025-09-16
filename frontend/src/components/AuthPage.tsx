import React, { useState } from 'react';
import LoginForm from './LoginForm';
import SignupForm from './SignupForm';
import './AuthPage.css';

const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);

  const handleSwitchToSignup = () => setIsLogin(false);
  const handleSwitchToLogin = () => setIsLogin(true);

  const handleAuthSuccess = () => {
    // Redirect to dashboard or main app
    window.location.href = '/dashboard';
  };

  return (
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
  );
};

export default AuthPage;
