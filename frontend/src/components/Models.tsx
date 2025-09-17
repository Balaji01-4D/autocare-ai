import React from 'react';
import './Models.css';

const Models: React.FC = () => {
  const bmwModels = [
    {
      id: 1,
      name: 'BMW X5',
      type: 'Sports Activity Vehicle',
      price: 'Starting at $62,200',
      image: 'https://images.unsplash.com/photo-1555215695-3004980ad54e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80',
      features: ['xDrive AWD', '523 HP', 'Premium Interior', 'Advanced Safety'],
      description: 'The ultimate Sports Activity Vehicle with commanding presence and exceptional performance.'
    },
    {
      id: 2,
      name: 'BMW 3 Series',
      type: 'Sedan',
      price: 'Starting at $36,350',
      image: 'https://images.unsplash.com/photo-1617788138017-80ad40651399?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2071&q=80',
      features: ['255 HP', 'Sport Suspension', 'BMW Live Cockpit', '8-Speed Automatic'],
      description: 'The benchmark in the luxury sport sedan segment with perfect balance of performance and efficiency.'
    },
    {
      id: 3,
      name: 'BMW i4',
      type: 'Electric Gran Coupe',
      price: 'Starting at $56,400',
      image: 'https://images.unsplash.com/photo-1617886322207-569a06eebef1?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80',
      features: ['270 Mile Range', '536 HP', 'Zero Emissions', 'Fast Charging'],
      description: 'Pure electric driving pleasure with the soul of a BMW and zero local emissions.'
    },
    {
      id: 4,
      name: 'BMW X3',
      type: 'Sports Activity Vehicle',
      price: 'Starting at $45,400',
      image: 'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80',
      features: ['xDrive AWD', '248 HP', 'Panoramic Roof', 'BMW Gesture Control'],
      description: 'Versatile luxury SAV that masters every terrain with athletic performance and premium comfort.'
    },
    {
      id: 5,
      name: 'BMW 5 Series',
      type: 'Executive Sedan',
      price: 'Starting at $55,700',
      image: 'https://images.unsplash.com/photo-1580414206179-e7f012737e90?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80',
      features: ['335 HP', 'Executive Lounge', 'Adaptive Suspension', 'Gesture Control'],
      description: 'The executive sedan that sets the standard for luxury, innovation, and driving dynamics.'
    },
    {
      id: 6,
      name: 'BMW iX',
      type: 'Electric SAV',
      price: 'Starting at $87,100',
      image: 'https://images.unsplash.com/photo-1617788138017-80ad40651399?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2071&q=80',
      features: ['324 Mile Range', '516 HP', 'Panoramic Roof', '5G Connectivity'],
      description: 'The future of luxury electric driving with groundbreaking technology and sustainable materials.'
    }
  ];

  const handleAskAI = (modelName: string) => {
    // For now, we'll show an alert. Later this can redirect to chatbot with model context
    alert(`AI Assistant: I'd be happy to help you learn more about the ${modelName}! This feature will be available soon in our AI Chatbot.`);
  };

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
          {bmwModels.map(model => (
            <div key={model.id} className="model-card">
              <div className="model-image-container">
                <img 
                  src={model.image} 
                  alt={model.name}
                  className="model-image"
                  loading="lazy"
                />
                <div className="model-overlay">
                  <span className="model-type">{model.type}</span>
                </div>
              </div>
              
              <div className="model-info">
                <div className="model-header">
                  <h3 className="model-name">{model.name}</h3>
                  <p className="model-price">{model.price}</p>
                </div>
                
                <p className="model-description">{model.description}</p>
                
                <div className="model-features">
                  {model.features.map((feature, index) => (
                    <span key={index} className="feature-badge">
                      {feature}
                    </span>
                  ))}
                </div>
                
                <div className="model-actions">
                  <button 
                    className="ask-ai-btn"
                    onClick={() => handleAskAI(model.name)}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="currentColor"/>
                      <path d="M12 6c-1.1 0-2 .9-2 2 0 .74.4 1.38 1 1.72v.78h2v-.78c.6-.34 1-.98 1-1.72 0-1.1-.9-2-2-2zM11 16h2v-2h-2v2z" fill="white"/>
                    </svg>
                    Ask AI about this model
                  </button>
                  <button className="learn-more-btn">
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
