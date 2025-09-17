import React from 'react';
import { Link } from 'react-router-dom';
import './Chatbot.css';

const Chatbot: React.FC = () => {
  return (
    <div className="chatbot-page">
      <Link to="/" className="back-to-home-chatbot">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        <span>Back to Home</span>
      </Link>
      
      <div className="chatbot-header">
        <h1>AI Sales Assistant</h1>
        <p>Your intelligent automotive companion for personalized recommendations and support</p>
      </div>

      <div className="chatbot-container">
        <div className="chat-placeholder">
          <div className="placeholder-content">
            <div className="ai-icon">🤖</div>
            <h2>AI Chatbot Coming Soon</h2>
            <p>
              We're developing an advanced AI-powered sales assistant that will help you:
            </p>
            <div className="features-list">
              <div className="feature-item">
                <span className="icon">💬</span>
                <span>Get personalized vehicle recommendations</span>
              </div>
              <div className="feature-item">
                <span className="icon">📊</span>
                <span>Compare models and features</span>
              </div>
              <div className="feature-item">
                <span className="icon">💰</span>
                <span>Calculate financing options</span>
              </div>
              <div className="feature-item">
                <span className="icon">📅</span>
                <span>Schedule test drives and appointments</span>
              </div>
              <div className="feature-item">
                <span className="icon">🔧</span>
                <span>Get maintenance and service advice</span>
              </div>
            </div>
            <div className="coming-soon-badge">
              <span>Coming Soon</span>
            </div>
          </div>
        </div>
      </div>

      <div className="preview-section">
        <div className="preview-content">
          <h2>What to Expect</h2>
          <div className="preview-grid">
            <div className="preview-card">
              <h3>Natural Conversations</h3>
              <p>Talk to our AI just like you would with a human sales representative. Ask questions, get recommendations, and explore options naturally.</p>
            </div>
            <div className="preview-card">
              <h3>Smart Recommendations</h3>
              <p>Our AI analyzes your preferences, budget, and needs to suggest the perfect vehicle matches tailored just for you.</p>
            </div>
            <div className="preview-card">
              <h3>Real-time Assistance</h3>
              <p>Get instant answers about pricing, features, availability, and scheduling without waiting for human assistance.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
