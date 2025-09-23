
# AutoCare AI

AutoCare AI is an intelligent, full-stack automotive care platform designed to revolutionize the car ownership experience. It combines a robust FastAPI backend with a modern React + TypeScript frontend, delivering advanced AI-powered diagnostics, smart maintenance, and seamless customer support for BMW India vehicles.

## Project Overview

AutoCare AI provides users with:

- **AI-Powered Chatbot:** Get instant answers to car-related queries, maintenance tips, and model-specific information using advanced language models.
- **Comprehensive Car Model Explorer:** Browse, compare, and learn about the full BMW India lineup, including detailed specs, features, and pricing.
- **Smart Maintenance & Diagnostics:** Leverage AI to predict maintenance needs, diagnose issues, and optimize vehicle performance.
- **Secure User Authentication:** JWT-based authentication with robust security practices, including password hashing, rate limiting, and input validation.
- **Personalized Dashboard:** Access a user dashboard for managing vehicles, service history, and interacting with the AI assistant.
- **24/7 Support:** AI-driven customer support and emergency assistance features.

## Architecture

### Backend (FastAPI)
- RESTful API with JWT authentication (access & refresh tokens)
- User registration, login, and profile management
- Car data management and comparison endpoints
- AI chatbot endpoints (general and car-specific)
- Security best practices: password policies, rate limiting, CORS, input validation
- SQLite (default) with easy migration to PostgreSQL for production

### Frontend (React + TypeScript + Vite)
- Modern, responsive UI for web and mobile
- Car model browsing, detail, and comparison pages
- Integrated AI chatbot interface
- Auth flows (login, signup, protected routes)
- Service and maintenance scheduling
- Dashboard for personalized user experience

## Key Features

- **AI Diagnostics:** Advanced vehicle diagnostics and predictive maintenance
- **Smart Maintenance:** Personalized schedules and reminders
- **Expert Support:** 24/7 AI-powered customer service
- **Car Model Explorer:** Detailed specs, images, and comparisons
- **Secure Auth:** JWT, password hashing, rate limiting
- **Production-Ready:** Docker support, environment configs, and security checklist

## Getting Started

See `backend/README.md` and `frontend/README.md` for setup instructions for each part of the stack.

## License

This project is for educational and demonstration purposes. For production use, review and update security, environment, and deployment settings.
