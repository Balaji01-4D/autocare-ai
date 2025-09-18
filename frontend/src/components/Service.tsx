import React from 'react';
import './Service.css';

const Service: React.FC = () => {
  const services = [
    {
      id: 1,
      title: 'AI Diagnostics',
      description: 'Advanced AI-powered vehicle diagnostics to identify issues before they become problems.',
      icon: '🔍',
      features: ['Real-time monitoring', 'Predictive analysis', 'Detailed reports']
    },
    {
      id: 2,
      title: 'Smart Maintenance',
      description: 'Intelligent maintenance scheduling based on your driving patterns and vehicle condition.',
      icon: '🔧',
      features: ['Personalized schedules', 'Cost optimization', 'Service reminders']
    },
    {
      id: 3,
      title: 'Emergency Support',
      description: '24/7 emergency roadside assistance with AI-powered dispatch and routing.',
      icon: '🚨',
      features: ['Instant response', 'GPS tracking', 'Live support']
    },
    {
      id: 4,
      title: 'Performance Tuning',
      description: 'Optimize your vehicle performance with AI-driven tuning recommendations.',
      icon: '⚡',
      features: ['Custom tuning', 'Fuel efficiency', 'Performance metrics']
    }
  ];

  return (
    <div className="service-page">
      <div className="service-header">
        <h1>BMW India Services</h1>
        <p>Experience the future of automotive care with our intelligent service solutions</p>
      </div>

      <div className="services-container">
        <div className="services-grid">
          {services.map(service => (
            <div key={service.id} className="service-card">
              <div className="service-icon">
                <span>{service.icon}</span>
              </div>
              <div className="service-content">
                <h3>{service.title}</h3>
                <p>{service.description}</p>
                <div className="service-features">
                  {service.features.map((feature, index) => (
                    <div key={index} className="feature-item">
                      <span className="check-icon">✓</span>
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>
                <button className="service-cta">
                  Book Service
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="service-booking">
        <div className="booking-section">
          <h2>Schedule Your Service</h2>
          <p>Let our AI find the best service time and location for you</p>
          
          <div className="booking-form">
            <div className="form-row">
              <div className="form-group">
                <label>Vehicle Model</label>
                <select className="form-input">
                  <option>Select your model</option>
                  <option>EcoSedan</option>
                  <option>UrbanSUV</option>
                  <option>SportCoupe</option>
                  <option>ElectricCompact</option>
                </select>
              </div>
              <div className="form-group">
                <label>Service Type</label>
                <select className="form-input">
                  <option>Select service type</option>
                  <option>AI Diagnostics</option>
                  <option>Smart Maintenance</option>
                  <option>Performance Tuning</option>
                  <option>General Service</option>
                </select>
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label>Preferred Date</label>
                <input type="date" className="form-input" />
              </div>
              <div className="form-group">
                <label>Preferred Time</label>
                <select className="form-input">
                  <option>Select time</option>
                  <option>9:00 AM</option>
                  <option>11:00 AM</option>
                  <option>2:00 PM</option>
                  <option>4:00 PM</option>
                </select>
              </div>
            </div>

            <button className="booking-submit">
              Schedule with AI Assistant
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Service;
