import React from 'react';
import './Home.css';
import homescreenImage from '../assets/homescreen_image.jpg';

const Home: React.FC = () => {
  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-text">
            <h2 className="hero-subtitle">Inside BMW India</h2>
            <h1 className="hero-title">
              Driving Innovation,<br />
              Defining the Future
            </h1>
            <button className="cta-button">
              Learn more →
            </button>
          </div>
        </div>
        <div className="hero-image">
          <img 
            src={homescreenImage} 
            alt="BMW India - BMW Vehicle" 
            className="hero-image-content"
          />
        </div>
      </section>

      {/* Additional Sections */}
      <section className="features-section">
        <div className="container">
          <div className="features-grid">
            <div className="feature-card">
              <h3>AI Diagnostics</h3>
              <p>Advanced AI-powered vehicle diagnostics for accurate problem detection and maintenance predictions.</p>
            </div>
            <div className="feature-card">
              <h3>Smart Maintenance</h3>
              <p>Intelligent maintenance scheduling based on your driving patterns and vehicle condition.</p>
            </div>
            <div className="feature-card">
              <h3>Expert Support</h3>
              <p>24/7 AI-powered customer support to help you with all your automotive needs.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
