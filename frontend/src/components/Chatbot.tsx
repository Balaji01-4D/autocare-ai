import React, { useState, useEffect, useRef } from 'react';
import { Link, useParams, useLocation } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import carService from '../services/car';
import './Chatbot.css';

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Interface for chat messages
interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

// Interface for car data used in comparison - lightweight version
interface Car {
  id: string;
  model_name: string;
  model_year: number;
  trim_variant: string;
  body_type: string;
  base_msrp_usd?: number;
  display_name?: string;
}

// Markdown Message Component
const MarkdownMessage: React.FC<{ content: string; sender: 'user' | 'bot' }> = ({ content, sender }) => {
  // Custom components for markdown elements
  const markdownComponents = {
    // Headers
    h1: ({ children }: any) => <h1 className="md-h1">{children}</h1>,
    h2: ({ children }: any) => <h2 className="md-h2">{children}</h2>,
    h3: ({ children }: any) => <h3 className="md-h3">{children}</h3>,
    h4: ({ children }: any) => <h4 className="md-h4">{children}</h4>,
    
    // Paragraphs
    p: ({ children }: any) => <p className="md-paragraph">{children}</p>,
    
    // Lists
    ul: ({ children }: any) => <ul className="md-list md-list-unordered">{children}</ul>,
    ol: ({ children }: any) => <ol className="md-list md-list-ordered">{children}</ol>,
    li: ({ children }: any) => <li className="md-list-item">{children}</li>,
    
    // Emphasis
    strong: ({ children }: any) => <strong className="md-bold">{children}</strong>,
    em: ({ children }: any) => <em className="md-italic">{children}</em>,
    
    // Code
    code: ({ children, className }: any) => {
      // Check if it's inline code or code block
      const isInline = !className;
      return isInline ? (
        <code className="md-code-inline">{children}</code>
      ) : (
        <code className="md-code-block">{children}</code>
      );
    },
    pre: ({ children }: any) => <pre className="md-pre">{children}</pre>,
    
    // Links
    a: ({ href, children }: any) => (
      <a href={href} className="md-link" target="_blank" rel="noopener noreferrer">
        {children}
      </a>
    ),
    
    // Tables
    table: ({ children }: any) => <table className="md-table">{children}</table>,
    thead: ({ children }: any) => <thead className="md-table-head">{children}</thead>,
    tbody: ({ children }: any) => <tbody className="md-table-body">{children}</tbody>,
    tr: ({ children }: any) => <tr className="md-table-row">{children}</tr>,
    th: ({ children }: any) => <th className="md-table-header">{children}</th>,
    td: ({ children }: any) => <td className="md-table-cell">{children}</td>,
    
    // Blockquotes
    blockquote: ({ children }: any) => <blockquote className="md-blockquote">{children}</blockquote>,
    
    // Horizontal rule
    hr: () => <hr className="md-hr" />,
  };

  if (sender === 'user') {
    // Users typically don't need full markdown rendering, keep simple
    return <span className="message-text">{content}</span>;
  }

  // For bot messages, render with full markdown support
  return (
    <div className="message-text markdown-content">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={markdownComponents}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

const Chatbot: React.FC = () => {
  // Route parameters and location for car-specific mode
  const { carId } = useParams<{ carId: string }>();
  const location = useLocation();
  const passedCarModel = location.state?.carModel;

  // State management for chat functionality
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [selectedCars, setSelectedCars] = useState<Car[]>([]);
  const [availableCars, setAvailableCars] = useState<Car[]>([]);
  const [showCarSelector, setShowCarSelector] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoadingCars, setIsLoadingCars] = useState(false);
  const [currentCar, setCurrentCar] = useState<Car | null>(passedCarModel || null);
  
  // Refs for DOM manipulation
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages are added
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Auto-resize textarea based on content
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const maxHeight = 120; // Max 5 lines approximately
      const newHeight = Math.min(textarea.scrollHeight, maxHeight);
      textarea.style.height = `${newHeight}px`;
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [inputValue]);

  // Initialize car-specific mode
  useEffect(() => {
    const initializeChat = async () => {
      if (carId && !currentCar) {
        try {
          // Fetch car details if not passed via state
          const response = await carService.getCars();
          const foundCar = response.cars.find(car => car.id.toString() === carId);
          if (foundCar) {
            const carData: Car = {
              id: foundCar.id.toString(),
              model_name: foundCar.model_name,
              model_year: foundCar.model_year,
              trim_variant: foundCar.trim_variant,
              body_type: foundCar.body_type,
              base_msrp_usd: foundCar.base_msrp_usd,
              display_name: foundCar.display_name || `${foundCar.model_year} ${foundCar.model_name} ${foundCar.trim_variant}`
            };
            setCurrentCar(carData);
            setSelectedCars([carData]);
            
            // Set specialized welcome message
            setMessages([{
              id: '1',
              text: `Hello! I'm your **BMW AI assistant**, specialized to help you with the **${carData.display_name}**. 

## What I can help you with:

- **Detailed specifications** and performance data
- **Feature explanations** and benefits
- **Pricing information** and financing options
- **Comparisons** with other BMW models
- **Real-world insights** and ownership experience

> I have comprehensive knowledge about this specific model and can answer questions about its features, specifications, performance, pricing, and more. 

What would you like to know about the **${carData.display_name}**?`,
              sender: 'bot',
              timestamp: new Date()
            }]);
          }
        } catch (error) {
          console.error('Error loading car details:', error);
        }
      } else if (!carId && messages.length === 0) {
        // Set general welcome message for regular chatbot mode
        setMessages([{
          id: '1',
          text: `Hello! I'm **BMW AI**, your intelligent automotive assistant. 

## How I can assist you:

- **Explore our BMW lineup** with detailed model information
- **Compare vehicles** side-by-side with specifications
- **Answer automotive questions** with expert knowledge
- **Provide personalized recommendations** based on your needs

> I'm here to help you make informed decisions about your BMW purchase!

How can I assist you today?`,
          sender: 'bot',
          timestamp: new Date()
        }]);
      }
    };

    initializeChat();
  }, [carId, currentCar, messages.length]);

  // Real API functions - fetch all cars for search, limit selection to 10
  const fetchCarsFromAPI = async (): Promise<Car[]> => {
    try {
      // Use full cars endpoint to get all available cars for searching
      const response = await carService.getCars();
      // Convert full Car objects to lightweight Car interface for consistency
      return response.cars.map(fullCar => ({
        id: fullCar.id.toString(),
        model_name: fullCar.model_name,
        model_year: fullCar.model_year,
        trim_variant: fullCar.trim_variant,
        body_type: fullCar.body_type,
        base_msrp_usd: fullCar.base_msrp_usd,
        display_name: `${fullCar.model_year} ${fullCar.model_name} ${fullCar.trim_variant}`
      }));
    } catch (error) {
      console.error('Error fetching cars from API:', error);
      throw error;
    }
  };

  const sendToChatbotAPI = async (message: string, cars: Car[]): Promise<string> => {
    try {
      const token = localStorage.getItem('token');
      
      // Use specialized endpoint for car-specific mode
      const endpoint = carId && currentCar 
        ? `${API_BASE_URL}/api/chatbot/car/${carId}`
        : `${API_BASE_URL}/api/chatbot`;
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({
          message: message,
          selected_cars: cars.map(car => car.id) // Extract only car IDs as strings
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.response; // Extract response from ChatbotResponse
    } catch (error) {
      console.error('Error calling chatbot API:', error);
      throw error;
    }
  };

  // Generate unique ID for messages
  const generateId = () => Date.now().toString() + Math.random().toString(36).substr(2, 9);

  // Handle compare cars functionality
  const handleCompareCars = async () => {
    setIsLoadingCars(true);
    try {
      const cars = await fetchCarsFromAPI();
      setAvailableCars(cars);
      setSearchQuery(''); // Clear search when opening modal
      setShowCarSelector(true);
    } catch (error) {
      console.error('Error fetching cars:', error);
      // Add user-friendly error message
      const errorMessage: ChatMessage = {
        id: generateId(),
        text: 'Sorry, I\'m having trouble loading the car data right now. Please check your connection and try again.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoadingCars(false);
    }
  };

  // Handle car selection - enforce 10 car limit for comparison
  const toggleCarSelection = (car: Car) => {
    setSelectedCars(prev => {
      const isSelected = prev.find(c => c.id === car.id);
      if (isSelected) {
        return prev.filter(c => c.id !== car.id);
      } else if (prev.length < 10) { // Limit to 10 cars for comparison performance
        return [...prev, car];
      } else {
        // Optional: Show a message that limit is reached
        console.warn('Cannot select more than 10 cars for comparison');
        return prev;
      }
    });
  };

  // Remove selected car
  const removeSelectedCar = (carId: string) => {
    setSelectedCars(prev => prev.filter(car => car.id !== carId));
  };

  // Filter cars based on search query
  const filteredCars = availableCars.filter(car => {
    if (!searchQuery) return true;
    const searchLower = searchQuery.toLowerCase();
    const displayName = carService.getComparisonDisplayName({
      id: parseInt(car.id),
      model_name: car.model_name,
      model_year: car.model_year,
      trim_variant: car.trim_variant,
      body_type: car.body_type,
      base_msrp_usd: car.base_msrp_usd,
      display_name: car.display_name
    }).toLowerCase();
    
    return displayName.includes(searchLower) || 
           car.model_name.toLowerCase().includes(searchLower) ||
           car.body_type?.toLowerCase().includes(searchLower) ||
           car.trim_variant?.toLowerCase().includes(searchLower) ||
           car.model_year.toString().includes(searchQuery);
  });

  // Handle quick question buttons for car-specific mode
  const handleQuickQuestion = (question: string) => {
    setInputValue(question);
    // Trigger send after setting the input
    setTimeout(() => {
      sendMessage();
    }, 100);
  };

  // Handle sending messages
  const sendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: ChatMessage = {
      id: generateId(),
      text: inputValue.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    // Add user message to chat
    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue.trim();
    const currentSelectedCars = [...selectedCars];
    setInputValue('');
    
    // Show typing indicator
    setIsTyping(true);

    try {
      // Call chatbot API with selected cars
      const botResponseText = await sendToChatbotAPI(currentInput, currentSelectedCars);
      
      const botResponse: ChatMessage = {
        id: generateId(),
        text: botResponseText,
        sender: 'bot',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, botResponse]);
      
      // Clear selected cars after sending
      if (currentSelectedCars.length > 0) {
        setSelectedCars([]);
      }
    } catch (error) {
      console.error('Error calling chatbot API:', error);
      const errorResponse: ChatMessage = {
        id: generateId(),
        text: 'I apologize, but I\'m experiencing technical difficulties right now. Please check your connection and try asking again.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsTyping(false);
    }
  };

  // Handle keyboard events
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Format timestamp for display
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  return (
    <div className="chatbot-page">
      {/* Top Navigation Bar */}
      <div className="chat-nav-bar">
        <Link to="/" className="back-button">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="14" cy="14" r="12" stroke="currentColor" strokeWidth="2" fill="none" />
            <path d="M16.5 9L12 14L16.5 19" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </Link>
        <h1 className={`chat-title ${currentCar ? 'car-specific' : ''}`}>
          {currentCar ? (
            <>
              <span className="car-model-name">{currentCar.display_name}</span>
              <span className="car-specialist-label">BMW Specialist</span>
            </>
          ) : (
            'BMW AI'
          )}
        </h1>
        <div className="nav-spacer"></div>
      </div>

      {/* Main Chat Container */}
      <div className="chat-main-container">
        {/* Car Info Panel - only show in car-specific mode */}
        {currentCar && (
          <div className="car-info-panel">
            <div className="car-info-header">
              <h3 className="car-info-title">{currentCar.display_name}</h3>
              <span className="car-info-price">
                {currentCar.base_msrp_usd ? `Starting at $${currentCar.base_msrp_usd.toLocaleString()}` : 'Contact for pricing'}
              </span>
            </div>
            <div className="car-info-details">
              <div className="car-info-item">
                <span className="car-info-label">Year:</span> {currentCar.model_year}
              </div>
              <div className="car-info-item">
                <span className="car-info-label">Body Type:</span> {currentCar.body_type}
              </div>
              <div className="car-info-item">
                <span className="car-info-label">Model:</span> {currentCar.model_name}
              </div>
              <div className="car-info-item">
                <span className="car-info-label">Trim:</span> {currentCar.trim_variant}
              </div>
            </div>
            <div className="car-quick-actions">
              <button 
                className="car-quick-action-btn"
                onClick={() => handleQuickQuestion('Tell me about the **key features** and what makes this model special')}
              >
                Key Features
              </button>
              <button 
                className="car-quick-action-btn"
                onClick={() => handleQuickQuestion('What are the **performance specifications** and engine details?')}
              >
                Performance
              </button>
              <button 
                className="car-quick-action-btn"
                onClick={() => handleQuickQuestion('How does this model **compare with similar BMW models**?')}
              >
                Compare
              </button>
              <button 
                className="car-quick-action-btn"
                onClick={() => handleQuickQuestion('What are the **ownership costs** including maintenance and insurance?')}
              >
                Costs
              </button>
            </div>
          </div>
        )}
        
        {/* Messages Area */}
        <div className="chat-messages-container" ref={chatContainerRef}>
          <div className="chat-messages">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.sender}`}>
                <div className="message-bubble">
                  <MarkdownMessage content={message.text} sender={message.sender} />
                  <div className="message-timestamp">{formatTime(message.timestamp)}</div>
                </div>
              </div>
            ))}
            
            {/* Typing Indicator */}
            {isTyping && (
              <div className="message bot typing-message">
                <div className="message-bubble">
                  <div className="typing-indicator">
                    <span>Bot is typing</span>
                    <div className="typing-dots">
                      <div className="dot"></div>
                      <div className="dot"></div>
                      <div className="dot"></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="chat-input-container">
          {/* Selected Cars Display */}
          {selectedCars.length > 0 && (
            <div className="selected-cars-container">
              <div className="selected-cars-header">
                <span>Comparing {selectedCars.length} car{selectedCars.length > 1 ? 's' : ''}:</span>
              </div>
              <div className="selected-cars-list">
                {selectedCars.map((car) => (
                  <div key={car.id} className="selected-car-item">
                    <span className="car-name">{carService.getComparisonDisplayName({
                      id: parseInt(car.id),
                      model_name: car.model_name,
                      model_year: car.model_year,
                      trim_variant: car.trim_variant,
                      body_type: car.body_type,
                      base_msrp_usd: car.base_msrp_usd,
                      display_name: car.display_name
                    })}</span>
                    <span className="car-price">{carService.getComparisonDisplayPrice({
                      id: parseInt(car.id),
                      model_name: car.model_name,
                      model_year: car.model_year,
                      trim_variant: car.trim_variant,
                      body_type: car.body_type,
                      base_msrp_usd: car.base_msrp_usd,
                      display_name: car.display_name
                    })}</span>
                    <button 
                      onClick={() => removeSelectedCar(car.id)}
                      className="remove-car-btn"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Car Selector Modal */}
          {showCarSelector && (
            <div className="car-selector-modal">
              <div className="car-selector-content">
                <div className="car-selector-header">
                  <div>
                    <h3>Select cars to compare (max 10)</h3>
                    <p className="search-info">
                      {isLoadingCars ? 
                        'Loading...' : 
                        searchQuery ? 
                          `${filteredCars.length} of ${availableCars.length} cars match "${searchQuery}"` :
                          `${availableCars.length} cars available`
                      }
                    </p>
                  </div>
                  <button 
                    onClick={() => {
                      setShowCarSelector(false);
                      setSearchQuery(''); // Clear search when closing
                    }}
                    className="close-selector-btn"
                  >
                    ×
                  </button>
                </div>
                
                {/* Search Input */}
                <div className="car-search-container">
                  <input
                    type="text"
                    placeholder="Search across all BMW models, years (2000-2025), trims..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="car-search-input"
                  />
                  <svg className="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 21L16.514 16.506L21 21ZM19 10.5C19 15.194 15.194 19 10.5 19C5.806 19 2 15.194 2 10.5C2 5.806 5.806 2 10.5 2C15.194 2 19 5.806 19 10.5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  {searchQuery && (
                    <button 
                      onClick={() => setSearchQuery('')}
                      className="clear-search-btn"
                    >
                      ×
                    </button>
                  )}
                  
                  {/* Quick search suggestions */}
                  {!searchQuery && (
                    <div className="search-suggestions">
                      {['3 Series', '2024', 'SUV', 'M3', 'X5'].map((suggestion) => (
                        <button
                          key={suggestion}
                          onClick={() => setSearchQuery(suggestion)}
                          className="suggestion-btn"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                
                <div className="car-list">
                  {isLoadingCars ? (
                    <div className="loading-cars">
                      <div className="loading-spinner"></div>
                      <p>Loading all BMW models...</p>
                    </div>
                  ) : filteredCars.length === 0 ? (
                    <div className="no-results">
                      {searchQuery ? (
                        <div>
                          <p>No cars found matching "{searchQuery}"</p>
                          <p className="search-suggestion">
                            Try searching for: 3 Series, 5 Series, X5, M3, Z4<br/>
                            Available years: 2000-2025
                          </p>
                        </div>
                      ) : (
                        'No cars available'
                      )}
                    </div>
                  ) : (
                    filteredCars.map((car) => {
                      const isSelected = selectedCars.find(c => c.id === car.id);
                      const canSelect = selectedCars.length < 10 || isSelected;
                      
                      return (
                        <div 
                          key={car.id} 
                          className={`car-item ${isSelected ? 'selected' : ''} ${!canSelect ? 'disabled' : ''}`}
                          onClick={() => canSelect && toggleCarSelection(car)}
                        >
                          <div className="car-info">
                            <span className="car-name">{carService.getComparisonDisplayName({
                              id: parseInt(car.id),
                              model_name: car.model_name,
                              model_year: car.model_year,
                              trim_variant: car.trim_variant,
                              body_type: car.body_type,
                              base_msrp_usd: car.base_msrp_usd,
                              display_name: car.display_name
                            })}</span>
                            <span className="car-details">{car.model_year} • {carService.getComparisonDisplayPrice({
                              id: parseInt(car.id),
                              model_name: car.model_name,
                              model_year: car.model_year,
                              trim_variant: car.trim_variant,
                              body_type: car.body_type,
                              base_msrp_usd: car.base_msrp_usd,
                              display_name: car.display_name
                            })}</span>
                          </div>
                          <div className={`car-checkbox ${isSelected ? 'checked' : ''}`}>
                            {isSelected && '✓'}
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
                <div className="car-selector-footer">
                  <button 
                    onClick={() => setShowCarSelector(false)}
                    className="done-btn"
                    disabled={selectedCars.length === 0}
                  >
                    Done ({selectedCars.length} selected)
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* ChatGPT-like Input Area */}
          <div className="chatgpt-input-wrapper">
            <div className="input-actions-left">
              <button 
                onClick={handleCompareCars}
                className="action-button compare-btn"
                title="Compare Cars"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M8 3l4 4-4 4M16 21l-4-4 4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M12 3h9M12 21H3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" opacity="0.6"/>
                </svg>
                <span>Compare</span>
              </button>
            </div>
            
            <div className="input-field-container">
              <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Message BMW AI"
                className="chatgpt-textarea"
                rows={1}
              />
              
              <button 
                onClick={sendMessage}
                disabled={!inputValue.trim()}
                className="chatgpt-send-button"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="m5 12 7-7 7 7M12 19V5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" transform="rotate(90 12 12)"/>
                </svg>
              </button>
            </div>
          </div>
          
          <div className="chatgpt-input-hint">
            BMW AI can make mistakes. Check important info.
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
