# FemmeForward Educational Platform - Backend API

A Flask-based REST API backend that powers the FemmeForward educational platform. This application provides personalized learning experiences, quiz generation, and progress tracking functionality.

## Features

- 🔐 User Authentication with Firebase
- 👤 User Profile Management
- 📚 Personalized Content Generation
- 📝 Dynamic Quiz Generation and Scoring
- 📊 Progress Tracking
- 🎯 Learning Path Management

## Prerequisites

- Python 3.x
- Firebase Admin SDK
- Google Generative AI API Access
- Firebase Project

## Environment Setup

1. Create a `.env` file in the root directory:
```
GENAI_API=your_gemini_api_key
```

2. Place your Firebase service account key in `empowerwomen.json`

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd femmeforward-backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /register` - Register a new user
- `POST /verify-token` - Verify Firebase authentication token

### User Profile
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile

### Content
- `GET /interests` - List available content tags
- `GET /topics` - Get personalized learning topics
- `GET /content` - Get personalized content recommendations

### Quiz Management
- `POST /generate_quiz` - Generate a new quiz
- `GET /quiz/<quiz_id>` - Get quiz questions
- `POST /quiz/start` - Start a quiz attempt
- `POST /quiz/submit-answer` - Submit an answer
- `POST /quiz/complete` - Complete a quiz
- `GET /user/quiz-history` - Get user's quiz history

## Authentication

The API uses Firebase Authentication. Include the Firebase ID token in the Authorization header:

```
Authorization: Bearer <firebase_id_token>
```

## CORS Configuration

The API supports CORS for the following origins:
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)

## Project Structure

- `app.py` - Main application file with route definitions
- `src/`
  - `ContentGenerator.py` - Handles content and quiz generation
  - `ProgressTracker.py` - Manages user progress and learning paths
  - `PromptGenerator.py` - Creates a personalized prompt according to user progress

## Database Structure (Firestore)

### Collections:
- `users` - User profiles and preferences
- `content` - Educational content and quizzes
- `quiz_attempts` - Quiz attempt records and scores
