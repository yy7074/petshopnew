# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a pet auction platform with three main components:
- **Flutter Mobile App** (`petshop_app/`) - Cross-platform mobile application
- **FastAPI Backend** (`backend/`) - Python API server with JWT authentication
- **Admin Dashboard** (`admin/`) - HTML-based management interface

## Development Commands

### Flutter App (petshop_app/)
```bash
# Navigate to Flutter app directory first
cd petshop_app

# Install dependencies
flutter pub get

# Run the app (debug mode)
flutter run

# Build for production
flutter build apk                # Android APK
flutter build ios               # iOS build
flutter build web               # Web build

# Testing
flutter test                    # Run unit tests
flutter analyze                 # Static analysis
flutter doctor                  # Check Flutter setup

# Code generation (if needed)
flutter packages pub run build_runner build --delete-conflicting-outputs
```

### Python Backend (backend/)
```bash
# Navigate to backend directory first
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run production server
uvicorn main:app --host 0.0.0.0 --port 8000

# Database migrations (if using Alembic)
alembic upgrade head
```

### Admin Dashboard (admin/)
```bash
# Navigate to admin directory first
cd admin

# Serve static files (development)
python -m http.server 8080
# OR use VS Code Live Server extension
```

## Architecture Overview

### Flutter App Architecture
- **State Management**: Provider + GetX for routing
- **Network Layer**: Dio with interceptors for authentication
- **Storage**: SharedPreferences + SQLite
- **UI Framework**: Material Design with custom theming
- **Screen Adaptation**: flutter_screenutil for responsive design

**Key Directories:**
- `lib/pages/` - UI screens organized by feature
- `lib/services/` - API and storage services  
- `lib/widgets/` - Reusable UI components
- `lib/constants/` - App themes and colors
- `lib/utils/` - Route definitions and utilities

### Backend Architecture  
- **Framework**: FastAPI with async/await
- **Database**: SQLAlchemy ORM with MySQL
- **Authentication**: JWT tokens with Bearer auth
- **API Structure**: Modular routers by feature
- **File Upload**: Static file serving with local storage

**Key Directories:**
- `app/api/` - API route handlers
- `app/models/` - Database models
- `app/schemas/` - Pydantic request/response models
- `app/core/` - Configuration and database setup
- `app/services/` - Business logic layer

## Key Configuration

### Flutter Configuration
- **Target SDK**: Flutter 3.x with Dart >=3.1.0
- **Design Size**: 375x812 (iPhone X dimensions)
- **API Base URL**: `http://localhost:8000/api` (configured in `api_service.dart`)
- **Supported Platforms**: iOS, Android, Web, Desktop

### Backend Configuration
- **API Documentation**: Available at `http://localhost:8000/docs` (Swagger UI)
- **CORS**: Configured for cross-origin requests
- **Static Files**: Served from `/static` endpoint
- **Database**: MySQL with SQLAlchemy ORM

## Development Workflow

1. **Backend First**: Start the FastAPI server to provide API endpoints
2. **Database Setup**: Ensure MySQL is running and database is created
3. **Flutter Development**: Use hot reload for rapid UI development
4. **API Integration**: Use the configured Dio client for HTTP requests
5. **State Management**: Use Provider for app state, GetX for navigation

## Authentication Flow

1. User credentials sent to `/api/auth/login`
2. JWT token returned and stored in SharedPreferences
3. Token automatically added to all API requests via Dio interceptor
4. Token expiration handled with automatic logout

## Important Notes

- Backend API base URL is hardcoded in `api_service.dart` - update for production
- Database models use SQLAlchemy with automatic table creation
- Flutter app uses both Provider and GetX - Provider for state, GetX for routing
- Admin dashboard is static HTML - requires backend API for data
- All Flutter widgets follow Material Design patterns