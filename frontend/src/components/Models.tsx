import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { carService, type Car } from '../services/car';
import './Models.css';

const Models: React.FC = () => {
  const navigate = useNavigate();
  const [cars, setCars] = useState<Car[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCars();
  }, []);

  const loadCars = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await carService.getCars();
      setCars(response.cars);
    } catch (err) {
      console.error('Error loading cars:', err);
      setError('Failed to load car models. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleCardClick = (car: Car) => {
    navigate(`/models/${car.id}`);
  };

  const handleAskAI = (car: Car, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click
    // Navigate to specialized chatbot page with car context
    navigate(`/chatbot/${car.id}`, { 
      state: { 
        carModel: car,
        context: 'model-specific' 
      }
    });
  };

  const handleLearnMore = (car: Car, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click
    navigate(`/models/${car.id}`);
  };

  if (loading) {
    return (
      <div className="models-page">
        <div className="models-hero">
          <div className="hero-content">
            <h1>BMW Model Range</h1>
            <p>Discover our complete lineup of luxury vehicles, from electric innovations to performance legends</p>
          </div>
        </div>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading BMW models...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="models-page">
        <div className="models-hero">
          <div className="hero-content">
            <h1>BMW Model Range</h1>
            <p>Discover our complete lineup of luxury vehicles, from electric innovations to performance legends</p>
          </div>
        </div>
        <div className="error-container">
          <p className="error-message">{error}</p>
          <button onClick={loadCars} className="retry-btn">
            Try Again
          </button>
        </div>
      </div>
    );
  }
  return (
    <div className="models-page">
      <div className="models-hero">
        <div className="hero-content">
          <h1>BMW Model Range</h1>
          <p>Discover our complete lineup of luxury vehicles, from electric innovations to performance legends</p>
        </div>
      </div>

      <div className="models-container">
        <div className="models-grid">
          {cars.map(car => (
            <div key={car.id} className="model-card" onClick={() => handleCardClick(car)}>
              <div className="model-image-container">
                <img 
                  src={carService.getDisplayImage(car)} 
                  alt={car.display_name || `${car.model_year} ${car.model_name} ${car.trim_variant}`}
                  className="model-image"
                  loading="lazy"
                />
                <div className="model-overlay">
                  <span className="model-type">{car.body_type}</span>
                </div>
              </div>
              
              <div className="model-info">
                <div className="model-header">
                  <h3 className="model-name">
                    {car.display_name || `${car.model_name} ${car.trim_variant}`}
                  </h3>
                  <p className="model-price">{carService.getDisplayPrice(car)}</p>
                </div>
                
                <p className="model-description">
                  {car.model_year} {car.model_name} {car.trim_variant} - 
                  {car.engine_type && ` ${carService.getEngineInfo(car)}`}
                  {car.horsepower_hp && ` with ${car.horsepower_hp} HP`}
                  {car.drivetrain && ` and ${car.drivetrain} drivetrain`}.
                </p>
                
                <div className="model-features">
                  {carService.getKeyFeatures(car).map((feature, index) => (
                    <span key={index} className="feature-badge">
                      {feature}
                    </span>
                  ))}
                </div>
                
                <div className="model-actions">
                  <button 
                    className="ask-ai-btn"
                    onClick={(e) => handleAskAI(car, e)}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="currentColor"/>
                      <path d="M12 6c-1.1 0-2 .9-2 2 0 .74.4 1.38 1 1.72v.78h2v-.78c.6-.34 1-.98 1-1.72 0-1.1-.9-2-2-2zM11 16h2v-2h-2v2z" fill="white"/>
                    </svg>
                    Ask AI about this model
                  </button>
                  <button className="learn-more-btn" onClick={(e) => handleLearnMore(car, e)}>
                    Learn More
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="models-cta-section">
        <div className="cta-content">
          <h2>Find Your Perfect BMW</h2>
          <p>Let our AI assistant help you choose the ideal BMW model based on your preferences and needs</p>
          <div className="cta-buttons">
            <button className="btn-primary">Talk to AI Assistant</button>
            <button className="btn-secondary">Schedule Test Drive</button>
            <button className="btn-secondary">Build & Price</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Models;
