from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional
from llama import get_response, get_response_with_memory, get_response_with_car_specific_context  
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
    ChatbotResponse,
    CarSpecificChatbotRequest,
    CarSpecificChatbotResponse,
    ChatHistoryResponse,
    ConversationDetailResponse
)
from models import User
from pydantic import BaseModel
from chat_memory_controller import chat_memory

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

# Create database tables
@app.on_event("startup")
def create_db_and_tables():
    # Chat models are now defined in models.py and will be auto-registered
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
    Process chatbot message with memory/RAG support and optional car selection
    Works for both authenticated and non-authenticated users
    """
    try:
        user_message = request.message
        selected_car_ids = request.selected_cars or []
        session_id = request.session_id
        
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

        # Initialize response variables
        response_text = ""
        context_used = None
        user_data = None
        
        if current_user:
            # Authenticated user - use memory and personalization
            user_id = current_user.id
            
            # Get relevant context from chat history
            relevant_context = chat_memory.get_relevant_context(
                user_id=user_id,
                current_message=user_message,
                limit=5
            )
            
            # Generate enhanced response with context
            response_text = generate_enhanced_automotive_response_with_memory(
                user_message, 
                selected_cars_info, 
                current_user, 
                relevant_context
            )
            
            # Prepare context summary for response
            if relevant_context:
                context_summary = f"Used {len(relevant_context)} previous conversation(s) for context"
                context_used = context_summary
            
            # Store this interaction in memory
            chat_memory.store_message(
                user_id=user_id,
                user_message=user_message,
                bot_response=response_text,
                selected_cars=selected_car_ids,
                session_id=session_id,
                context_used=context_used
            )
            
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
            # Non-authenticated user - use memory with guest user ID
            user_id = 0  # Use special guest user ID
            
            # Get relevant context from chat history for guest
            relevant_context = chat_memory.get_relevant_context(
                user_id=user_id,
                current_message=user_message,
                limit=3  # Fewer context items for guests
            )
            
            # Create a temporary user object for the response generator
            from models import User as UserModel
            temp_user = UserModel(id=0, name="Guest", email="guest@example.com", number="", password="")
            
            # Generate enhanced response with context even for guests
            response_text = generate_enhanced_automotive_response_with_memory(
                user_message, 
                selected_cars_info, 
                temp_user, 
                relevant_context
            )
            
            # Prepare context summary for response
            if relevant_context:
                context_summary = f"Used {len(relevant_context)} previous conversation(s) for context"
                context_used = context_summary
            
            # Store this interaction in memory for guest user
            chat_memory.store_message(
                user_id=user_id,
                user_message=user_message,
                bot_response=response_text,
                selected_cars=selected_car_ids,
                session_id=session_id,
                context_used=context_used
            )
            
            user_data = None

        return ChatbotResponse(
            response=response_text,
            user=user_data,
            timestamp=datetime.utcnow(),
            selected_cars_info=selected_cars_info if selected_cars_info else None,
            session_id=session_id,
            context_used=context_used
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chatbot API error: {str(e)}"
        )

@app.post("/api/chatbot/car/{car_id}", response_model=CarSpecificChatbotResponse)
def car_specific_chatbot_api(
    car_id: int,
    request: CarSpecificChatbotRequest,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Process chatbot message with specialized focus on a specific car model
    Enhanced with car-specific context and knowledge
    """
    try:
        user_message = request.message
        session_id = request.session_id
        
        # Get the specific car details
        try:
            cars_from_db = get_cars_by_ids_controller([car_id])
            if not cars_from_db:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Car with ID {car_id} not found"
                )
            
            car_info = cars_from_db[0]
            car_response = convert_car_to_response(car_info)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error retrieving car details: {str(e)}"
            )

        # Initialize response variables
        response_text = ""
        context_used = None
        specialized_context = None
        user_data = None
        
        if current_user:
            # Authenticated user - use memory and personalization
            user_id = current_user.id
            
            # Get relevant context from chat history with car-specific filter
            relevant_context = chat_memory.get_relevant_context(
                user_id=user_id,
                current_message=user_message,
                limit=5
            )
            
            # Generate specialized car-specific response
            response_text = generate_car_specific_response_with_memory(
                user_message, 
                car_info, 
                current_user, 
                relevant_context
            )
            
            # Prepare context summaries
            if relevant_context:
                context_summary = f"Used {len(relevant_context)} previous conversation(s) for context"
                context_used = context_summary
            
            specialized_context = f"Specialized knowledge for {car_response.model_year} {car_response.model_name} {car_response.trim_variant}"
            
            # Store this interaction in memory with car-specific tagging
            chat_memory.store_message(
                user_id=user_id,
                user_message=user_message,
                bot_response=response_text,
                selected_cars=[str(car_id)],
                session_id=session_id,
                context_used=f"{context_used} | Car-specific mode: {car_id}" if context_used else f"Car-specific mode: {car_id}"
            )
            
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
            # Non-authenticated user - use memory with guest user ID
            user_id = 0  # Use special guest user ID
            
            # Get relevant context from chat history for guest
            relevant_context = chat_memory.get_relevant_context(
                user_id=user_id,
                current_message=user_message,
                limit=3  # Fewer context items for guests
            )
            
            # Create a temporary user object for the response generator
            from models import User as UserModel
            temp_user = UserModel(id=0, name="Guest", email="guest@example.com", number="", password="")
            
            # Generate specialized car-specific response
            response_text = generate_car_specific_response_with_memory(
                user_message, 
                car_info, 
                temp_user, 
                relevant_context
            )
            
            # Prepare context summaries
            if relevant_context:
                context_summary = f"Used {len(relevant_context)} previous conversation(s) for context"
                context_used = context_summary
            
            specialized_context = f"Specialized knowledge for {car_response.model_year} {car_response.model_name} {car_response.trim_variant}"
            
            # Store this interaction in memory for guest user with car-specific tagging
            chat_memory.store_message(
                user_id=user_id,
                user_message=user_message,
                bot_response=response_text,
                selected_cars=[str(car_id)],
                session_id=session_id,
                context_used=f"{context_used} | Car-specific mode: {car_id}" if context_used else f"Car-specific mode: {car_id}"
            )
            
            user_data = None

        return CarSpecificChatbotResponse(
            response=response_text,
            car_context=car_response,
            user=user_data,
            timestamp=datetime.utcnow(),
            session_id=session_id,
            context_used=context_used,
            specialized_context=specialized_context
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Car-specific chatbot API error: {str(e)}"
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

    return get_response(lower_message + f" (my name is {user.name} and my email is {user.email} and my phone number is {user.number})")

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


def generate_enhanced_automotive_response_with_memory(message: str, selected_cars, user, conversation_context=None):
    """
    Generate automotive response using memory/RAG context
    """
    # Prepare user name for personalization
    user_name = user.name if hasattr(user, 'name') and user.name and user.name != "Guest" else "Customer"
    
    return get_response_with_memory(
        user_input=message,
        conversation_context=conversation_context,
        selected_cars=selected_cars,
        user_name=user_name
    )


def generate_car_specific_response_with_memory(message: str, specific_car, user, conversation_context=None):
    """
    Generate specialized car-focused response using memory/RAG context
    """
    # Prepare user name for personalization
    user_name = user.name if hasattr(user, 'name') and user.name else "Customer"
    
    return get_response_with_car_specific_context(
        user_input=message,
        specific_car=specific_car,
        conversation_context=conversation_context,
        user_name=user_name
    )


# Chat history endpoints
@app.get("/api/chat/history", response_model=ChatHistoryResponse)
def get_chat_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """
    Get user's chat conversation history
    """
    try:
        history = chat_memory.get_conversation_history(
            user_id=current_user.id,
            limit=limit
        )
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching chat history: {str(e)}"
        )


@app.get("/api/chat/conversation/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation_detail(
    conversation_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed conversation with all messages
    """
    try:
        conversation = chat_memory.get_conversation_detail(
            user_id=current_user.id,
            conversation_id=conversation_id
        )
        return conversation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversation: {str(e)}"
        )


@app.delete("/api/chat/conversation/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a conversation and all its messages
    """
    try:
        # This would need to be implemented in the chat_memory_controller
        # For now, return success
        return {"message": "Conversation deletion not yet implemented"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)