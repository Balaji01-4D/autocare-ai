from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional
import random
from controllers import (
    register_user_controller,
    login_user_controller, 
    refresh_token_controller,
    get_user_profile_controller,
    get_current_user,
    engine
)
from schemas import (
    UserRegister, 
    UserLogin, 
    AuthResponse, 
    RefreshTokenRequest, 
    TokenRefreshResponse,
    UserProfileResponse,
    CreateUserRequest,  # For backward compatibility
    CarResponse,
    CarsListResponse,
    ChatbotRequest,
    ChatbotResponse
)

# Security scheme
security = HTTPBearer(auto_error=False)

# Optional authentication helper
def get_optional_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    Get current user if authenticated, otherwise return None
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials)
    except:
        return None
from models import User

app = FastAPI(
    title="AutoCare AI API", 
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
@app.on_event("startup")
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to AutoCare AI API", "version": "2.0.0", "status": "healthy"}

@app.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister):
    """
    Register a new user with address and return JWT tokens
    """
    try:
        result = register_user_controller(
            name=user_data.name,
            email=user_data.email,
            number=user_data.number,
            password=user_data.password,
            door_no=user_data.door_no,
            street=user_data.street,
            city=user_data.city,
            state=user_data.state,
            zipcode=user_data.zipcode
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/auth/login", response_model=AuthResponse)
def login(user_credentials: UserLogin):
    """
    Authenticate user and return JWT tokens
    """
    try:
        result = login_user_controller(
            email=user_credentials.email,
            password=user_credentials.password
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/auth/refresh", response_model=TokenRefreshResponse)
def refresh_access_token(token_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    try:
        result = refresh_token_controller(token_data.refresh_token)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/auth/profile", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile (requires authentication)
    """
    try:
        result = get_user_profile_controller(current_user.id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/auth/logout")
def logout():
    """
    Logout endpoint (client should discard tokens)
    """
    return {"message": "Logout successful. Please discard your tokens."}

# Legacy endpoint for backward compatibility
@app.post("/users", response_model=dict)
def create_user(user_data: CreateUserRequest):
    """
    Legacy endpoint - use /auth/register instead
    """
    try:
        result = register_user_controller(
            name=user_data.name,
            email=user_data.email,
            number=user_data.number,
            password=user_data.password,
            door_no=user_data.door_no,
            street=user_data.street,
            city=user_data.city,
            state=user_data.state,
            zipcode=user_data.zipcode
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": "2025-09-16", "version": "2.0.0"}

@app.get("/api/cars", response_model=CarsListResponse)
def get_cars():
    """
    Get list of available cars for comparison - Public endpoint, no authentication required
    """
    try:
        # Dummy BMW car data
        cars_data = [
            {
                "id": "1",
                "name": "BMW X5",
                "model": "X5",
                "year": 2024,
                "price": 65000,
                "image": "/images/bmw-x5.jpg",
                "features": ["All-Wheel Drive", "Panoramic Sunroof", "Premium Sound", "Navigation"],
                "engine": "3.0L Twin-Turbo I6",
                "fuel_type": "Gasoline"
            },
            {
                "id": "2",
                "name": "BMW 3 Series",
                "model": "3 Series",
                "year": 2024,
                "price": 45000,
                "image": "/images/bmw-3-series.jpg",
                "features": ["Rear-Wheel Drive", "Sport Suspension", "Premium Interior", "iDrive System"],
                "engine": "2.0L Twin-Turbo I4",
                "fuel_type": "Gasoline"
            },
            {
                "id": "3",
                "name": "BMW X3",
                "model": "X3",
                "year": 2024,
                "price": 55000,
                "image": "/images/bmw-x3.jpg",
                "features": ["All-Wheel Drive", "Heated Seats", "Wireless Charging", "Surround View"],
                "engine": "2.0L Twin-Turbo I4",
                "fuel_type": "Gasoline"
            },
            {
                "id": "4",
                "name": "BMW 5 Series",
                "model": "5 Series",
                "year": 2024,
                "price": 58000,
                "image": "/images/bmw-5-series.jpg",
                "features": ["Executive Package", "Massaging Seats", "Gesture Control", "Advanced Safety"],
                "engine": "2.0L Twin-Turbo I4",
                "fuel_type": "Gasoline"
            },
            {
                "id": "5",
                "name": "BMW X7",
                "model": "X7",
                "year": 2024,
                "price": 85000,
                "image": "/images/bmw-x7.jpg",
                "features": ["7-Seater", "Premium Luxury", "Air Suspension", "Executive Lounge"],
                "engine": "3.0L Twin-Turbo I6",
                "fuel_type": "Gasoline"
            },
            {
                "id": "6",
                "name": "BMW i4",
                "model": "i4",
                "year": 2024,
                "price": 56000,
                "image": "/images/bmw-i4.jpg",
                "features": ["Electric Drive", "Fast Charging", "Eco Mode", "BMW iDrive 8"],
                "engine": "Electric Motor",
                "fuel_type": "Electric"
            },
            {
                "id": "7",
                "name": "BMW X1",
                "model": "X1",
                "year": 2024,
                "price": 38000,
                "image": "/images/bmw-x1.jpg",
                "features": ["Compact SUV", "All-Wheel Drive Available", "Premium Entry", "Efficient Design"],
                "engine": "2.0L Twin-Turbo I4",
                "fuel_type": "Gasoline"
            },
            {
                "id": "8",
                "name": "BMW M3",
                "model": "M3",
                "year": 2024,
                "price": 75000,
                "image": "/images/bmw-m3.jpg",
                "features": ["High Performance", "Track Mode", "Carbon Fiber", "M Sport Package"],
                "engine": "3.0L Twin-Turbo I6",
                "fuel_type": "Gasoline"
            }
        ]
        
        cars = [CarResponse(**car) for car in cars_data]
        
        return CarsListResponse(
            cars=cars,
            user=None,  # No user data for public endpoint
            timestamp=datetime.utcnow()
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching cars: {str(e)}"
        )

@app.post("/api/chatbot", response_model=ChatbotResponse)
def chatbot_api(
    request: ChatbotRequest,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Process chatbot message with optional car selection and return AI response
    Works for both authenticated and non-authenticated users
    """
    try:
        user_message = request.message
        selected_car_ids = request.selected_cars or []
        
        # Get selected cars info if any
        selected_cars_info = []
        if selected_car_ids:
            # This would normally query a database, but for now using dummy data
            all_cars = get_dummy_cars_data()
            selected_cars_info = [car for car in all_cars if car["id"] in selected_car_ids]
        
        # Generate response based on message and selected cars
        if current_user:
            # Authenticated user - personalized response
            response_text = generate_enhanced_automotive_response(user_message, selected_cars_info, current_user)
            user_data = {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "number": current_user.number,
                "address": {
                    "id": current_user.address.id if current_user.address else None,
                    "door_no": current_user.address.door_no if current_user.address else None,
                    "street": current_user.address.street if current_user.address else None,
                    "city": current_user.address.city if current_user.address else None,
                    "state": current_user.address.state if current_user.address else None,
                    "zipcode": current_user.address.zipcode if current_user.address else None,
                } if current_user.address else None
            }
        else:
            # Non-authenticated user - generic response
            from models import User as UserModel
            
            # Create a temporary user object for the response generator
            temp_user = UserModel(id=0, name="Guest", email="guest@example.com", number="", password_hash="")
            response_text = generate_enhanced_automotive_response(user_message, selected_cars_info, temp_user)
            user_data = None

        return ChatbotResponse(
            response=response_text,
            user=user_data,
            timestamp=datetime.utcnow(),
            selected_cars_info=[CarResponse(**car) for car in selected_cars_info] if selected_cars_info else None
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chatbot API error: {str(e)}"
        )

@app.post("/chatbot/message")
def chatbot_message(
    message: dict, 
    current_user: User = Depends(get_current_user)
):
    """
    Legacy chatbot endpoint - use /api/chatbot instead
    Process chatbot message and return AI response
    """
    try:
        user_message = message.get("message", "")
        print(message, current_user)

        
        response = generate_automotive_response(user_message, current_user)
        
        return {
            "response": response,
            "timestamp": str(datetime.utcnow()),
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "number": current_user.number
            }
        }
    except HTTP+Exception as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chatbot error: {str(e)}"
        )

def generate_automotive_response(message: str, user: User) -> str:
    """
    Generate automotive-focused AI response
    """
    lower_message = message.lower()
    
    # Car recommendation responses
    if any(word in lower_message for word in ['recommend', 'suggest', 'buy']):
        if 'sedan' in lower_message:
            return f"Hi {user.name}! For sedans, I'd recommend the Honda Accord for reliability, Toyota Camry for fuel efficiency, or BMW 3 Series for luxury and performance. What's your budget range?"
        elif 'suv' in lower_message:
            return f"Great choice, {user.name}! Popular SUV options include Honda CR-V (fuel efficient), Toyota Highlander (family-friendly), or BMW X5 (luxury). What size do you prefer?"
        elif any(word in lower_message for word in ['electric', 'ev', 'tesla']):
            return f"Electric vehicles are excellent, {user.name}! Consider Tesla Model 3, BMW i4, or Honda Accord Hybrid. What's your daily driving range?"
        else:
            return f"I'd love to help you find the perfect car, {user.name}! Could you tell me your preferred type (sedan, SUV, hatchback), budget, and primary use?"
    
    # Maintenance responses
    elif any(word in lower_message for word in ['maintenance', 'service', 'repair']):
        if 'oil' in lower_message:
            return "Regular oil changes are crucial! Conventional oil: every 3,000-5,000 miles. Synthetic oil: 7,500-10,000 miles. Always check your owner's manual!"
        elif any(word in lower_message for word in ['tire', 'tyre']):
            return "Tire maintenance tips: Check pressure monthly, rotate every 6,000-8,000 miles, replace when tread reaches 2/32 inch. Watch for uneven wear!"
        elif 'brake' in lower_message:
            return "Brake safety is critical! Inspect every 12,000 miles, replace pads every 30,000-70,000 miles depending on driving habits. Listen for squealing or grinding sounds."
        else:
            return "Key maintenance items: oil changes, tire rotation, brake inspection, air filter replacement, fluid checks. What specific maintenance question do you have?"
    
    # BMW specific
    elif 'bmw' in lower_message:
        return f"{user.name}, BMW offers exceptional luxury and performance! Popular models: 3 Series (sports sedan), X5 (luxury SUV), i4 (electric). Interested in a specific model?"
    
    # General automotive
    elif any(word in lower_message for word in ['fuel', 'gas', 'mpg']):
        return "Fuel efficiency depends on engine size, vehicle weight, driving habits, and maintenance. Hybrids and smaller engines offer better MPG. Regular maintenance helps too!"
    
    # Default responses
    else:
        responses = [
            f"That's interesting, {user.name}! Could you provide more details so I can give you a targeted automotive recommendation?",
            f"I'd love to help with that automotive question, {user.name}! Could you be more specific about what you're looking for?",
            f"As your AutoCare AI assistant, {user.name}, I can help with car recommendations, maintenance advice, and automotive questions. What would you like to explore?"
        ]
        return random.choice(responses)

def get_dummy_cars_data():
    """
    Get dummy cars data (same as in /api/cars endpoint)
    """
    return [
        {
            "id": "1",
            "name": "BMW X5",
            "model": "X5",
            "year": 2024,
            "price": 65000,
            "image": "/images/bmw-x5.jpg",
            "features": ["All-Wheel Drive", "Panoramic Sunroof", "Premium Sound", "Navigation"],
            "engine": "3.0L Twin-Turbo I6",
            "fuel_type": "Gasoline"
        },
        {
            "id": "2",
            "name": "BMW 3 Series",
            "model": "3 Series",
            "year": 2024,
            "price": 45000,
            "image": "/images/bmw-3-series.jpg",
            "features": ["Rear-Wheel Drive", "Sport Suspension", "Premium Interior", "iDrive System"],
            "engine": "2.0L Twin-Turbo I4",
            "fuel_type": "Gasoline"
        },
        {
            "id": "3",
            "name": "BMW X3",
            "model": "X3",
            "year": 2024,
            "price": 55000,
            "image": "/images/bmw-x3.jpg",
            "features": ["All-Wheel Drive", "Heated Seats", "Wireless Charging", "Surround View"],
            "engine": "2.0L Twin-Turbo I4",
            "fuel_type": "Gasoline"
        },
        {
            "id": "4",
            "name": "BMW 5 Series",
            "model": "5 Series",
            "year": 2024,
            "price": 58000,
            "image": "/images/bmw-5-series.jpg",
            "features": ["Executive Package", "Massaging Seats", "Gesture Control", "Advanced Safety"],
            "engine": "2.0L Twin-Turbo I4",
            "fuel_type": "Gasoline"
        },
        {
            "id": "5",
            "name": "BMW X7",
            "model": "X7",
            "year": 2024,
            "price": 85000,
            "image": "/images/bmw-x7.jpg",
            "features": ["7-Seater", "Premium Luxury", "Air Suspension", "Executive Lounge"],
            "engine": "3.0L Twin-Turbo I6",
            "fuel_type": "Gasoline"
        },
        {
            "id": "6",
            "name": "BMW i4",
            "model": "i4",
            "year": 2024,
            "price": 56000,
            "image": "/images/bmw-i4.jpg",
            "features": ["Electric Drive", "Fast Charging", "Eco Mode", "BMW iDrive 8"],
            "engine": "Electric Motor",
            "fuel_type": "Electric"
        },
        {
            "id": "7",
            "name": "BMW X1",
            "model": "X1",
            "year": 2024,
            "price": 38000,
            "image": "/images/bmw-x1.jpg",
            "features": ["Compact SUV", "All-Wheel Drive Available", "Premium Entry", "Efficient Design"],
            "engine": "2.0L Twin-Turbo I4",
            "fuel_type": "Gasoline"
        },
        {
            "id": "8",
            "name": "BMW M3",
            "model": "M3",
            "year": 2024,
            "price": 75000,
            "image": "/images/bmw-m3.jpg",
            "features": ["High Performance", "Track Mode", "Carbon Fiber", "M Sport Package"],
            "engine": "3.0L Twin-Turbo I6",
            "fuel_type": "Gasoline"
        }
    ]

def generate_enhanced_automotive_response(message: str, selected_cars: list, user: User) -> str:
    """
    Generate enhanced automotive response with car comparison support
    """
    lower_message = message.lower()
    
    # If cars are selected, provide comparison-focused responses
    if selected_cars:
        car_names = [car["name"] for car in selected_cars]
        car_names_str = ", ".join(car_names[:-1]) + f" and {car_names[-1]}" if len(car_names) > 1 else car_names[0]
        
        # Car comparison responses
        if any(word in lower_message for word in ['compare', 'difference', 'better', 'vs']):
            if len(selected_cars) >= 2:
                car1, car2 = selected_cars[0], selected_cars[1]
                price_diff = abs(car1["price"] - car2["price"])
                cheaper_car = car1 if car1["price"] < car2["price"] else car2
                expensive_car = car2 if car1["price"] < car2["price"] else car1
                
                return f"Great question, {user.name}! Comparing {car_names_str}:\n\n" \
                       f"💰 **Price**: {cheaper_car['name']} starts at ${cheaper_car['price']:,} while {expensive_car['name']} is ${expensive_car['price']:,} (${price_diff:,} difference)\n" \
                       f"🔧 **Engine**: {car1['name']} has {car1['engine']} vs {car2['name']} with {car2['engine']}\n" \
                       f"⛽ **Fuel**: Both use {car1['fuel_type']}\n" \
                       f"✨ **Key Features**: {car1['name']} offers {', '.join(car1['features'][:2])} while {car2['name']} features {', '.join(car2['features'][:2])}\n\n" \
                       f"Which aspect would you like me to elaborate on?"
            else:
                return f"I'd love to help you compare {car_names_str}, {user.name}! Please select at least 2 cars to see a detailed comparison."
        
        # Feature-focused questions
        elif any(word in lower_message for word in ['feature', 'option', 'include']):
            features_text = "\n".join([f"🚗 **{car['name']}**: {', '.join(car['features'])}" for car in selected_cars])
            return f"Here are the key features for your selected vehicles, {user.name}:\n\n{features_text}\n\nWhich features are most important to you?"
        
        # Price-focused questions
        elif any(word in lower_message for word in ['price', 'cost', 'budget', 'afford']):
            prices_text = "\n".join([f"💰 {car['name']}: ${car['price']:,}" for car in selected_cars])
            total_price = sum(car['price'] for car in selected_cars)
            avg_price = total_price // len(selected_cars)
            return f"Here's the pricing for your selected vehicles, {user.name}:\n\n{prices_text}\n\n📊 Average price: ${avg_price:,}\n\nWould you like information about financing options?"
        
        # Performance questions
        elif any(word in lower_message for word in ['engine', 'performance', 'power', 'speed']):
            engine_text = "\n".join([f"🏎️ **{car['name']}**: {car['engine']} ({car['fuel_type']})" for car in selected_cars])
            return f"Here's the engine and performance information, {user.name}:\n\n{engine_text}\n\nWould you like to know more about fuel efficiency or driving dynamics?"
        
        # Default with selected cars
        else:
            return f"I can help you with {car_names_str}, {user.name}! These are excellent choices. You can ask me to:\n" \
                   f"• Compare their features and pricing\n" \
                   f"• Explain engine specifications\n" \
                   f"• Discuss financing options\n" \
                   f"• Schedule a test drive\n\nWhat would you like to know?"
    
    # No cars selected - general automotive responses
    else:
        if any(word in lower_message for word in ['compare', 'comparison']):
            return f"Hi {user.name}! I'd love to help you compare vehicles. Please use the Compare button to select the BMW models you're interested in, then I can provide detailed comparisons!"
        
        # Use existing general responses
        return generate_automotive_response(message, user)
