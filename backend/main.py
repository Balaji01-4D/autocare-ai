from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional
from llama import get_response  
from controllers import (
    register_user_controller,
    login_user_controller, 
    refresh_token_controller,
    get_user_profile_controller,
    get_current_user,
    engine
)
from car_controllers import (
    get_all_cars_controller,
    get_cars_by_ids_controller,
    get_cars_for_comparison_controller,
    convert_car_to_response,
    convert_car_to_comparison_response
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
    CarComparisonResponse,
    CarsComparisonListResponse,
    ChatbotRequest,
    ChatbotResponse
)
from models import User
from pydantic import BaseModel
from memory_store import ConversationMemory

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

class Query(BaseModel):
    user_id: str
    query: str

memory = ConversationMemory()

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
        # Get all cars from database
        cars_from_db = get_all_cars_controller()
        
        # Convert to response format
        cars = [convert_car_to_response(car) for car in cars_from_db]
        
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

@app.get("/api/cars/comparison", response_model=CarsComparisonListResponse)
def get_cars_for_comparison(limit: int = 10):
    """
    Get limited cars for comparison with only essential data - Public endpoint
    Maximum limit is 10 cars to prevent performance issues
    """
    try:
        # Enforce maximum limit of 10 cars
        comparison_limit = min(limit, 10)
        
        # Get limited cars from database
        cars_from_db = get_cars_for_comparison_controller(comparison_limit)
        
        # Get total count for reference
        from car_controllers import get_car_count_controller
        total_count = get_car_count_controller()
        
        # Convert to lightweight response format
        cars = [convert_car_to_comparison_response(car) for car in cars_from_db]
        
        return CarsComparisonListResponse(
            cars=cars,
            limit=comparison_limit,
            total_available=total_count,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching cars for comparison: {str(e)}"
        )

@app.get("/api/cars/{car_id}", response_model=CarResponse)
def get_car_by_id(car_id: int):
    """
    Get single car by ID - Public endpoint, no authentication required
    """
    try:
        from car_controllers import get_car_by_id_controller
        
        # Get car from database
        car_from_db = get_car_by_id_controller(car_id)
        
        if not car_from_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Car with ID {car_id} not found"
            )
        
        # Convert to response format
        car_response = convert_car_to_response(car_from_db)
        
        return car_response
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching car: {str(e)}"
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
            try:
                # Convert string IDs to integers
                car_ids = [int(car_id) for car_id in selected_car_ids]
                # Get cars from database
                selected_cars_from_db = get_cars_by_ids_controller(car_ids)
                selected_cars_info = [convert_car_to_response(car) for car in selected_cars_from_db]
            except ValueError:
                # Handle invalid car IDs gracefully
                selected_cars_info = []
        
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
            temp_user = UserModel(id=0, name="Guest", email="guest@example.com", number="", password="")
            response_text = generate_enhanced_automotive_response(user_message, selected_cars_info, temp_user)
            user_data = None

        return ChatbotResponse(
            response=response_text,
            user=user_data,
            timestamp=datetime.utcnow(),
            selected_cars_info=selected_cars_info if selected_cars_info else None
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
    except HTTPException as e:
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
    print(lower_message + f" (my name details are : {str(user)})")

    return get_response(lower_message + f" (my name details are : {str(user)})")

def generate_enhanced_automotive_response(message: str, selected_cars: list, user: User) -> str:
    """
    Generate enhanced automotive response with car comparison support
    """
    lower_message = message.lower()
    
    # Build context with selected car information if available
    car_context = ""
    if selected_cars:
        car_context = "Selected cars for comparison: "
        for car in selected_cars:
            car_context += f"{car.display_name} (${car.base_msrp_usd:,} USD), "
        car_context = car_context.rstrip(", ") + ". "
    
    # Add car context to the message
    enhanced_message = car_context + message

    return generate_automotive_response(enhanced_message, user)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)