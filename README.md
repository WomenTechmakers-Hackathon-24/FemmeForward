# EmpowerWomen
EmpowerWomen
# API Routes Documentation

## Authentication Related Routes

### 1. Register User
- **Endpoint:** `/register`
- **Method:** POST
- **Authentication:** None (From Google SSO API)
- **Purpose:** Register a new user
- **Required Fields:** name, email, birthdate
- **Optional Fields:** interests, difficulty, profile_picture, bio, learning_goals, notification_settings, language, theme

### 2. Verify Token
- **Endpoint:** `/verify-token`
- **Method:** POST
- **Authentication:** None
- **Purpose:** Verify Firebase ID token
- **Required Fields:** token

## Profile Management

### 3. Get Profile
- **Endpoint:** `/profile`
- **Method:** GET
- **Authentication:** Required
- **Purpose:** Retrieve user profile information

### 4. Update Profile
- **Endpoint:** `/profile`
- **Method:** PUT
- **Authentication:** Required
- **Purpose:** Update user profile information
- **Protected Fields:** email, created_at

## Quiz Management

### 5. Generate Quiz
- **Endpoint:** `/generate_quiz`
- **Method:** POST
- **Authentication:** Required
- **Required Fields:** topic, tags, age_group, num_questions
- **Optional Fields:** difficulty

### 6. Start Quiz
- **Endpoint:** `/quiz/start`
- **Method:** POST
- **Authentication:** Required
- **Required Fields:** quiz_id

### 7. Submit Quiz Answer
- **Endpoint:** `/quiz/submit-answer`
- **Method:** POST
- **Authentication:** Required
- **Required Fields:** attempt_id, question_index, answer

### 8. Complete Quiz
- **Endpoint:** `/quiz/complete`
- **Method:** POST
- **Authentication:** Required
- **Required Fields:** attempt_id

### 9. Get Quiz Progress
- **Endpoint:** `/quiz/progress/<attempt_id>`
- **Method:** GET
- **Authentication:** Required
- **Purpose:** Check progress of a specific quiz attempt

### 10. Get Quiz History
- **Endpoint:** `/user/quiz-history`
- **Method:** GET
- **Authentication:** Required
- **Purpose:** Retrieve user's quiz attempt history
- **Limit:** 10 most recent attempts

## Content and Progress

### 11. Get Personalized Content
- **Endpoint:** `/content`
- **Method:** GET
- **Authentication:** Required
- **Purpose:** Retrieve content based on user interests
- **Limit:** 5 items

### 12. Update Progress
- **Endpoint:** `/progress`
- **Method:** POST
- **Authentication:** Required
- **Required Fields:** content_id, completed
- **Optional Fields:** score

## Statistics

### 13. Get User Stats
- **Endpoint:** `/user/<user_email>/stats`
- **Method:** GET
- **Authentication:** Required
- **Purpose:** Retrieve user statistics including:
  - Total content
  - Completed content
  - Completion rate
  - Average score

## Authentication Implementation
- All authenticated routes use the `@token_required` decorator
- Token must be provided in Authorization header as "Bearer {token}"
- Token is verified against Firebase Authentication
- User profile is checked in Firestore database

## Error Handling
- 401: Invalid or missing token
- 403: Unauthorized access
- 404: Resource not found
- 400: Bad request (missing required fields)

## Database Collections Used
- users
- learning_paths
- quiz_history
- content
- user_progress
- quiz_attempts
- quizzes