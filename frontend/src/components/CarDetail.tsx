import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { carService, type Car } from '../services/car';
import './CarDetail.css';

const CarDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [car, setCar] = useState<Car | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'specs' | 'features' | 'colors'>('overview');

  useEffect(() => {
    if (id) {
      loadCarDetails(parseInt(id));
    }
  }, [id]);

  const loadCarDetails = async (carId: number) => {
    try {
      setLoading(true);
      setError(null);
      const carData = await carService.getCarById(carId);
      setCar(carData);
    } catch (err) {
      console.error('Error loading car details:', err);
      setError('Failed to load car details. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToModels = () => {
    navigate('/models');
  };

  const handleAskAI = () => {
    if (car) {
      // Navigate to chatbot with this car pre-selected
      navigate(`/dashboard?selectedCar=${car.id}&message=Tell me more about the ${car.display_name}`);
    }
  };

  if (loading) {
    return (
      <div className="car-detail-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading car details...</p>
        </div>
      </div>
    );
  }

  if (error || !car) {
    return (
      <div className="car-detail-page">
        <div className="error-container">
          <p className="error-message">{error || 'Car not found'}</p>
          <button onClick={() => id && loadCarDetails(parseInt(id))} className="retry-btn">
            Try Again
          </button>
          <button onClick={handleBackToModels} className="back-btn">
            Back to Models
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="car-detail-page">
      {/* Hero Section */}
      <div className="car-hero">
        <button className="back-button" onClick={handleBackToModels}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Back to Models
        </button>
        
        <div className="car-hero-content">
          <div className="car-hero-text">
            <h1 className="car-title">{car.display_name || `${car.model_year} ${car.model_name} ${car.trim_variant}`}</h1>
            <p className="car-subtitle">{car.body_type} • {car.model_year}</p>
            <div className="car-price-hero">
              <span className="price-label">Starting at</span>
              <span className="price-amount">{carService.getDisplayPrice(car)}</span>
            </div>
            <div className="hero-actions">
              <button className="btn-primary" onClick={handleAskAI}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="currentColor"/>
                  <path d="M12 6c-1.1 0-2 .9-2 2 0 .74.4 1.38 1 1.72v.78h2v-.78c.6-.34 1-.98 1-1.72 0-1.1-.9-2-2-2zM11 16h2v-2h-2v2z" fill="white"/>
                </svg>
                Ask AI Assistant
              </button>
              <button className="btn-secondary">Schedule Test Drive</button>
              <button className="btn-secondary">Build & Price</button>
            </div>
          </div>
          <div className="car-hero-image">
            <img 
              src={carService.getDisplayImage(car)} 
              alt={car.display_name || `${car.model_name} ${car.trim_variant}`}
              className="hero-car-image"
            />
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="car-nav-tabs">
        <div className="tabs-container">
          <button 
            className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`tab ${activeTab === 'specs' ? 'active' : ''}`}
            onClick={() => setActiveTab('specs')}
          >
            Specifications
          </button>
          <button 
            className={`tab ${activeTab === 'features' ? 'active' : ''}`}
            onClick={() => setActiveTab('features')}
          >
            Features
          </button>
          <button 
            className={`tab ${activeTab === 'colors' ? 'active' : ''}`}
            onClick={() => setActiveTab('colors')}
          >
            Colors & Options
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="car-content">
        {activeTab === 'overview' && (
          <div className="overview-content">
            <div className="overview-grid">
              <div className="overview-section">
                <h3>Performance</h3>
                <div className="specs-grid">
                  {car.horsepower_hp && (
                    <div className="spec-item">
                      <span className="spec-label">Horsepower</span>
                      <span className="spec-value">{car.horsepower_hp} HP</span>
                    </div>
                  )}
                  {car.torque_nm && (
                    <div className="spec-item">
                      <span className="spec-label">Torque</span>
                      <span className="spec-value">{car.torque_nm} Nm</span>
                    </div>
                  )}
                  {car.acceleration_0_100_s && (
                    <div className="spec-item">
                      <span className="spec-label">0-100 km/h</span>
                      <span className="spec-value">{car.acceleration_0_100_s}s</span>
                    </div>
                  )}
                  {car.top_speed_kmh && (
                    <div className="spec-item">
                      <span className="spec-label">Top Speed</span>
                      <span className="spec-value">{car.top_speed_kmh} km/h</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="overview-section">
                <h3>Engine & Drivetrain</h3>
                <div className="specs-grid">
                  {car.engine_type && (
                    <div className="spec-item">
                      <span className="spec-label">Engine Type</span>
                      <span className="spec-value">{car.engine_type}</span>
                    </div>
                  )}
                  {car.displacement_cc && (
                    <div className="spec-item">
                      <span className="spec-label">Displacement</span>
                      <span className="spec-value">{car.displacement_cc} cc</span>
                    </div>
                  )}
                  {car.cylinders && (
                    <div className="spec-item">
                      <span className="spec-label">Cylinders</span>
                      <span className="spec-value">{car.cylinders}</span>
                    </div>
                  )}
                  {car.drivetrain && (
                    <div className="spec-item">
                      <span className="spec-label">Drivetrain</span>
                      <span className="spec-value">{car.drivetrain}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="overview-section">
                <h3>Efficiency</h3>
                <div className="specs-grid">
                  {car.fuel_consumption_combined && (
                    <div className="spec-item">
                      <span className="spec-label">Fuel Consumption</span>
                      <span className="spec-value">{car.fuel_consumption_combined} L/100km</span>
                    </div>
                  )}
                  {car.co2_emissions && (
                    <div className="spec-item">
                      <span className="spec-label">CO₂ Emissions</span>
                      <span className="spec-value">{car.co2_emissions} g/km</span>
                    </div>
                  )}
                  {car.electric_range_km && (
                    <div className="spec-item">
                      <span className="spec-label">Electric Range</span>
                      <span className="spec-value">{car.electric_range_km} km</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'specs' && (
          <div className="specs-content">
            <div className="specs-sections">
              <div className="specs-section">
                <h3>Dimensions</h3>
                <div className="specs-list">
                  {car.length_mm && <div className="spec-row"><span>Length</span><span>{car.length_mm} mm</span></div>}
                  {car.width_mm && <div className="spec-row"><span>Width</span><span>{car.width_mm} mm</span></div>}
                  {car.height_mm && <div className="spec-row"><span>Height</span><span>{car.height_mm} mm</span></div>}
                  {car.wheelbase_mm && <div className="spec-row"><span>Wheelbase</span><span>{car.wheelbase_mm} mm</span></div>}
                  {car.curb_weight_kg && <div className="spec-row"><span>Curb Weight</span><span>{car.curb_weight_kg} kg</span></div>}
                </div>
              </div>

              <div className="specs-section">
                <h3>Powertrain</h3>
                <div className="specs-list">
                  {car.engine_type && <div className="spec-row"><span>Engine Type</span><span>{car.engine_type}</span></div>}
                  {car.displacement_cc && <div className="spec-row"><span>Displacement</span><span>{car.displacement_cc} cc</span></div>}
                  {car.cylinders && <div className="spec-row"><span>Cylinders</span><span>{car.cylinders}</span></div>}
                  {car.horsepower_hp && <div className="spec-row"><span>Max Power</span><span>{car.horsepower_hp} HP</span></div>}
                  {car.torque_nm && <div className="spec-row"><span>Max Torque</span><span>{car.torque_nm} Nm</span></div>}
                  {car.transmission && <div className="spec-row"><span>Transmission</span><span>{car.transmission}</span></div>}
                  {car.drivetrain && <div className="spec-row"><span>Drivetrain</span><span>{car.drivetrain}</span></div>}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'features' && (
          <div className="features-content">
            <div className="features-sections">
              {car.safety_features && car.safety_features.length > 0 && (
                <div className="features-section">
                  <h3>Safety Features</h3>
                  <div className="features-grid">
                    {car.safety_features.map((feature, index) => (
                      <div key={index} className="feature-item">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                        {feature}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {car.infotainment && (
                <div className="features-section">
                  <h3>Infotainment</h3>
                  <div className="features-grid">
                    <div className="feature-item">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      {car.infotainment}
                    </div>
                  </div>
                </div>
              )}

              {car.wheel_sizes_available && car.wheel_sizes_available.length > 0 && (
                <div className="features-section">
                  <h3>Wheel Options</h3>
                  <div className="features-grid">
                    {car.wheel_sizes_available.map((size, index) => (
                      <div key={index} className="feature-item">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                          <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2"/>
                        </svg>
                        {size}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'colors' && (
          <div className="colors-content">
            <div className="colors-sections">
              {car.exterior_colors_available && car.exterior_colors_available.length > 0 && (
                <div className="colors-section">
                  <h3>Exterior Colors</h3>
                  <div className="colors-grid">
                    {car.exterior_colors_available.map((color, index) => (
                      <div key={index} className="color-item">
                        <div className="color-swatch" style={{ backgroundColor: getColorHex(color) }}></div>
                        <span className="color-name">{color}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {car.interior_materials_colors && car.interior_materials_colors.length > 0 && (
                <div className="colors-section">
                  <h3>Interior Materials & Colors</h3>
                  <div className="colors-grid">
                    {car.interior_materials_colors.map((material, index) => (
                      <div key={index} className="color-item">
                        <div className="color-swatch interior" style={{ backgroundColor: getColorHex(material) }}></div>
                        <span className="color-name">{material}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper function to get color hex codes (simplified version)
const getColorHex = (colorName: string): string => {
  const colorMap: { [key: string]: string } = {
    'Alpine White': '#FFFFFF',
    'Jet Black': '#000000',
    'Carbon Black': '#1a1a1a',
    'Mineral Grey': '#808080',
    'Space Grey': '#4a4a4a',
    'Storm Bay': '#2c3e50',
    'Midnight Black': '#191919',
    'Glacier Silver': '#c0c0c0',
    'Sophisto Grey': '#5a5a5a',
    'Barcelona Blue': '#1f4e79',
    'Phytonic Blue': '#0066cc',
    'Arctic Race Blue': '#87ceeb',
    'Melbourne Red': '#8b0000',
    'Sunset Orange': '#ff8c00',
    'Mineral White': '#f5f5f5',
  };
  
  return colorMap[colorName] || '#cccccc';
};

export default CarDetail;