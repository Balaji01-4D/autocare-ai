import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
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

// Interface for car data - matches backend CarResponse
interface Car {
  id: string;
  name: string;
  model: string;
  year: number;
  price: number;
  image?: string;
  features: string[];
  engine: string;
  fuel_type: string;
}

const Chatbot: React.FC = () => {
  // State management for chat functionality
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      text: 'Hello! I\'m BMW AI, your intelligent automotive assistant. I can help you explore our BMW lineup, compare vehicles, and answer all your automotive questions. How can I assist you today?',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [selectedCars, setSelectedCars] = useState<Car[]>([]);
  const [availableCars, setAvailableCars] = useState<Car[]>([]);
  const [showCarSelector, setShowCarSelector] = useState(false);
  
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

  // Real API functions
  const fetchCarsFromAPI = async (): Promise<Car[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/cars`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.cars; // Extract cars array from CarsListResponse
    } catch (error) {
      console.error('Error fetching cars from API:', error);
      throw error;
    }
  };

  const sendToChatbotAPI = async (message: string, cars: Car[]): Promise<string> => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/chatbot`, {
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
    try {
      const cars = await fetchCarsFromAPI();
      setAvailableCars(cars);
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
    }
  };

  // Handle car selection
  const toggleCarSelection = (car: Car) => {
    setSelectedCars(prev => {
      const isSelected = prev.find(c => c.id === car.id);
      if (isSelected) {
        return prev.filter(c => c.id !== car.id);
      } else if (prev.length < 3) { // Limit to 3 cars for comparison
        return [...prev, car];
      }
      return prev;
    });
  };

  // Remove selected car
  const removeSelectedCar = (carId: string) => {
    setSelectedCars(prev => prev.filter(car => car.id !== carId));
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
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </Link>
        <h1 className="chat-title">BMW AI</h1>
        <div className="nav-spacer"></div>
      </div>

      {/* Main Chat Container */}
      <div className="chat-main-container">
        {/* Messages Area */}
        <div className="chat-messages-container" ref={chatContainerRef}>
          <div className="chat-messages">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.sender}`}>
                <div className="message-bubble">
                  <div className="message-text">{message.text}</div>
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
                    <span className="car-name">{car.name}</span>
                    <span className="car-price">${car.price.toLocaleString()}</span>
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
                  <h3>Select cars to compare (max 3)</h3>
                  <button 
                    onClick={() => setShowCarSelector(false)}
                    className="close-selector-btn"
                  >
                    ×
                  </button>
                </div>
                <div className="car-list">
                  {availableCars.map((car) => {
                    const isSelected = selectedCars.find(c => c.id === car.id);
                    const canSelect = selectedCars.length < 3 || isSelected;
                    
                    return (
                      <div 
                        key={car.id} 
                        className={`car-item ${isSelected ? 'selected' : ''} ${!canSelect ? 'disabled' : ''}`}
                        onClick={() => canSelect && toggleCarSelection(car)}
                      >
                        <div className="car-info">
                          <span className="car-name">{car.name}</span>
                          <span className="car-details">{car.year} • ${car.price.toLocaleString()}</span>
                        </div>
                        <div className={`car-checkbox ${isSelected ? 'checked' : ''}`}>
                          {isSelected && '✓'}
                        </div>
                      </div>
                    );
                  })}
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
