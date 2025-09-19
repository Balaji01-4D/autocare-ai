import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Types matching the backend CarResponse schema
export interface Car {
  id: number;
  model_name: string;
  model_year: number;
  trim_variant: string;
  body_type: string;
  
  // Dimensions
  length_mm?: number;
  width_mm?: number;
  height_mm?: number;
  wheelbase_mm?: number;
  curb_weight_kg?: number;
  
  // Engine specs
  engine_type?: string;
  displacement_cc?: number;
  cylinders?: string;
  horsepower_hp?: number;
  torque_nm?: number;
  
  // Drivetrain
  transmission?: string;
  drivetrain?: string;
  
  // Performance
  acceleration_0_100_s?: number;
  top_speed_kmh?: number;
  fuel_consumption_combined?: number;
  co2_emissions?: number;
  electric_range_km?: number;
  
  // Features and colors
  infotainment?: string;
  safety_features?: string[];
  exterior_colors_available?: string[];
  interior_materials_colors?: string[];
  wheel_sizes_available?: string[];
  
  // Pricing and media
  base_msrp_usd?: number;
  image_link?: string;
  display_name?: string;
}

export interface CarsResponse {
  cars: Car[];
  user?: any;
  timestamp: string;
}

// Lightweight interface for car comparison
export interface CarComparison {
  id: number;
  model_name: string;
  model_year: number;
  trim_variant: string;
  body_type: string;
  base_msrp_usd?: number;
  display_name?: string;
}

export interface CarsComparisonResponse {
  cars: CarComparison[];
  limit: number;
  total_available: number;
  timestamp: string;
}

export interface ChatbotRequest {
  message: string;
  selected_cars?: string[];
}

export interface ChatbotResponse {
  response: string;
  user?: any;
  timestamp: string;
  selected_cars_info?: Car[];
}

// Car service functions
export const carService = {
  // Get all cars
  async getCars(): Promise<CarsResponse> {
    try {
      const response = await api.get('/api/cars');
      return response.data;
    } catch (error) {
      console.error('Error fetching cars:', error);
      throw error;
    }
  },

  // Get car by ID
  async getCarById(carId: number): Promise<Car> {
    try {
      const response = await api.get(`/api/cars/${carId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching car by ID:', error);
      throw error;
    }
  },

  // Get lightweight cars for comparison (max 10 cars)
  async getCarsForComparison(limit: number = 10): Promise<CarsComparisonResponse> {
    try {
      // Ensure limit doesn't exceed 10
      const comparisonLimit = Math.min(limit, 10);
      const response = await api.get(`/api/cars/comparison?limit=${comparisonLimit}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching cars for comparison:', error);
      throw error;
    }
  },

  // Send message to chatbot with optional car selection
  async sendChatbotMessage(message: string, selectedCarIds: string[] = []): Promise<ChatbotResponse> {
    try {
      const response = await api.post('/api/chatbot', {
        message,
        selected_cars: selectedCarIds
      });
      return response.data;
    } catch (error) {
      console.error('Error sending chatbot message:', error);
      throw error;
    }
  },

  // Helper function to get display price
  getDisplayPrice(car: Car): string {
    if (car.base_msrp_usd && car.base_msrp_usd > 0) {
      return `Starting at $${car.base_msrp_usd.toLocaleString()}`;
    }
    return 'Price on request';
  },

  // Helper function to get display image
  getDisplayImage(car: Car): string {
    if (car.image_link) {
      return car.image_link;
    }
    // Fallback to a default car image or placeholder
    return 'https://images.unsplash.com/photo-1555215695-3004980ad54e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80';
  },

  // Helper function to format engine info
  getEngineInfo(car: Car): string {
    if (car.displacement_cc && car.engine_type) {
      return `${car.displacement_cc}cc ${car.engine_type}`;
    } else if (car.engine_type) {
      return car.engine_type;
    }
    return 'Engine info not available';
  },

  // Helper function to format power info
  getPowerInfo(car: Car): string {
    if (car.horsepower_hp) {
      return `${car.horsepower_hp} HP`;
    }
    return '';
  },

  // Helper function to get key features
  getKeyFeatures(car: Car): string[] {
    const features: string[] = [];
    
    if (car.drivetrain) {
      features.push(car.drivetrain);
    }
    
    if (car.horsepower_hp) {
      features.push(`${car.horsepower_hp} HP`);
    }
    
    if (car.transmission) {
      features.push(car.transmission);
    }
    
    if (car.safety_features && car.safety_features.length > 0) {
      // Add first few safety features
      features.push(...car.safety_features.slice(0, 2));
    }
    
    // If we have fewer than 4 features, add some based on body type
    if (features.length < 4) {
      if (car.body_type === 'SUV') {
        features.push('Premium Interior');
      } else if (car.body_type === 'Sedan') {
        features.push('Sport Suspension');
      }
      
      if (car.infotainment) {
        features.push(car.infotainment);
      }
    }
    
    return features.slice(0, 4); // Return max 4 features
  },

  // Helper functions for comparison data
  getComparisonDisplayPrice(car: CarComparison): string {
    if (car.base_msrp_usd && car.base_msrp_usd > 0) {
      return `$${car.base_msrp_usd.toLocaleString()}`;
    }
    return 'Price on request';
  },

  getComparisonDisplayName(car: CarComparison): string {
    return car.display_name || `${car.model_year} ${car.model_name} ${car.trim_variant}`;
  },

  // Validate comparison selection (max 10 cars)
  validateComparisonSelection(selectedIds: string[]): { isValid: boolean; message?: string } {
    if (selectedIds.length === 0) {
      return { isValid: false, message: 'Please select at least one car for comparison' };
    }
    
    if (selectedIds.length > 10) {
      return { isValid: false, message: 'You can compare a maximum of 10 cars at once' };
    }
    
    return { isValid: true };
  }
};

export default carService;
