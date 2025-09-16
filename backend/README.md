# AutoCare AI Backend API

Production-ready FastAPI backend with JWT authentication for the AutoCare AI application.

## Features

- ✅ JWT-based authentication (access & refresh tokens)
- ✅ Password hashing with bcrypt
- ✅ Input validation and sanitization
- ✅ Rate limiting for login attempts
- ✅ One-to-one user-address relationship
- ✅ CORS support
- ✅ Comprehensive error handling
- ✅ Production-ready security practices

## Installation

1. **Clone the repository**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the application**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication

#### POST /auth/register
Register a new user with address.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "number": "1234567890",
  "password": "SecurePass123!",
  "door_no": "123",
  "street": "Main Street",
  "city": "New York",
  "state": "NY",
  "zipcode": "10001"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "number": "1234567890",
    "address": {
      "id": 1,
      "door_no": "123",
      "street": "Main Street",
      "city": "New York",
      "state": "NY",
      "zipcode": "10001"
    }
  }
}
```

#### POST /auth/login
Authenticate user and get tokens.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": { /* user data */ }
}
```

#### POST /auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### GET /auth/profile
Get current user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "number": "1234567890",
    "address": { /* address data */ }
  }
}
```

#### POST /auth/logout
Logout user (client should discard tokens).

### Health Check

#### GET /health
Check API health status.

## Security Features

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

### Rate Limiting
- Maximum 5 failed login attempts per email
- 5-minute lockout period

### Input Validation
- Email format validation
- Phone number format validation
- Input sanitization to prevent XSS
- Maximum length limits on all fields

## Environment Variables

```env
# Database Configuration
DATABASE_URL=sqlite:///./autocare.db

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=development

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Production Deployment

### Security Checklist
- [ ] Change `SECRET_KEY` to a strong, random value
- [ ] Use a production database (PostgreSQL recommended)
- [ ] Configure proper CORS origins
- [ ] Use HTTPS in production
- [ ] Set up proper logging
- [ ] Configure rate limiting with Redis
- [ ] Set up database backups
- [ ] Monitor and alert on errors

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Schema

### User Table
- `id` (Primary Key)
- `name`
- `email` (Unique)
- `number` (Unique)
- `password` (Hashed)

### Address Table
- `id` (Primary Key)
- `user_id` (Foreign Key, Unique)
- `door_no`
- `street`
- `city`
- `state`
- `zipcode`

## Error Codes

- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid credentials)
- `404` - Not Found (user/resource not found)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error
