import { useState } from 'react';
import './LoginSignup.css';

const LoginSignup = () => {
  const [isLoginForm, setIsLoginForm] = useState(true);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const toggleForm = () => {
    setIsLoginForm(!isLoginForm);
  };

  const handleSignupSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }
    // Add your signup logic here
  };

  const handleLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Add your login logic here
  };

  return (
    <div className="container">
      {isLoginForm ? (
        <div id="loginForm">
          <h1>Login</h1>
          <form onSubmit={handleLoginSubmit}>
            <input type="text" placeholder="Username" required />
            <input type="email" placeholder="Email" required />
            <input type="password" placeholder="Password" required />
            <div className="remember">
              <input type="checkbox" id="remember" />
              <label htmlFor="remember">Remember me</label>
            </div>
            <button type="submit">Login</button>
            <p className="toggle-text">
              Don't have an account? <a onClick={toggleForm}>Sign Up</a>
            </p>
          </form>
        </div>
      ) : (
        <div id="signupForm" style={{ display: 'block' }}>
          <h1>Sign Up</h1>
          <form onSubmit={handleSignupSubmit}>
            <input type="text" placeholder="Full Name" required />
            <input type="text" placeholder="Username" required />
            <input type="email" placeholder="Email" required />
            <input 
              type="password" 
              id="password" 
              placeholder="Password" 
              required 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <input 
              type="password" 
              id="confirmPassword" 
              placeholder="Confirm Password" 
              required 
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
            <button type="submit">Sign Up</button>
            <p className="toggle-text">
              Already have an account? <a onClick={toggleForm}>Login</a>
            </p>
          </form>
        </div>
      )}
    </div>
  );
};

export default LoginSignup;
