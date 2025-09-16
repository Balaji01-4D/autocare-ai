from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
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
    CreateUserRequest  # For backward compatibility
)
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


