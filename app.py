from flask import Flask, request, jsonify
from firebase_admin import firestore, credentials, auth
import firebase_admin
import google.generativeai as genai
from functools import wraps
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Add the src folder to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from ContentGenerator import ContentGenerator

app = Flask(__name__)
load_dotenv()

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("empowerwomen-fbbda-firebase-adminsdk-96bfo-3ab2cc60b5.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize the Gemini API
genai.configure(api_key='AIzaSyA1cVBZoZmq8dm3qCQuzu5_k6iVOWbr-5Q')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Verify the Firebase ID token
            token = token.split(" ")[1]  # Remove 'Bearer ' prefix
            decoded_token = auth.verify_id_token(token)
            user_email = decoded_token['email']
            
            # Get user profile from Firestore
            current_user = db.collection('users').document(user_email).get()
            if not current_user.exists:
                return jsonify({'message': 'User profile not found'}), 404
                
            return f(current_user.to_dict(), *args, **kwargs)
        except auth.InvalidIdTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'message': f'Error: {str(e)}'}), 401
    
    return decorated

@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    required_fields = ['name', 'email', 'birthdate']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    user_ref = db.collection('users').document(data['email'])
    
    if user_ref.get().exists:
        return jsonify({"error": "User already exists"}), 400
    
    # Create user profile
    user_profile = {
        'name': data['name'],
        'email': data['email'],
        'birthdate': data['birthdate'],
        'interests': data.get('interests', []),
        'difficulty_level': data.get('difficulty', 'beginner'),
        'created_at': firestore.SERVER_TIMESTAMP,
        'profile_picture': data.get('profile_picture', ''),
        'bio': data.get('bio', ''),
        'learning_goals': data.get('learning_goals', []),
        'completed_courses': [],
        'achievements': [],
        'preferences': {
            'notification_settings': data.get('notification_settings', True),
            'language': data.get('language', 'en'),
            'theme': data.get('theme', 'light')
        }
    }
    
    user_ref.set(user_profile)
    
    # Create initial learning path
    learning_path_ref = db.collection('learning_paths').document(data['email'])
    learning_path_ref.set({
        'user_email': data['email'],
        'current_level': 'beginner',
        'completed_modules': [],
        'current_module': None,
        'progress': 0,
        'created_at': firestore.SERVER_TIMESTAMP
    })
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/verify-token', methods=['POST'])
def verify_token():
    token = request.json.get('token')
    try:
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(token)
        user_email = decoded_token['email']
        
        # Check if user exists in our database
        user_ref = db.collection('users').document(user_email)
        user = user_ref.get()
        
        if not user.exists:
            return jsonify({'error': 'User not registered', 'email': user_email}), 404
            
        user_data = user.to_dict()
        return jsonify({
            'user': {
                'email': user_data['email'],
                'name': user_data['name'],
                'profile_picture': user_data.get('profile_picture', ''),
                'difficulty_level': user_data.get('difficulty_level', 'beginner')
            }
        })
    except:
        return jsonify({'error': 'Invalid token'}), 401

@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify(current_user), 200

@app.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.json
    user_ref = db.collection('users').document(current_user['email'])
    
    # Fields that cannot be updated
    protected_fields = ['email', 'created_at']
    update_data = {k: v for k, v in data.items() if k not in protected_fields}
    
    user_ref.update(update_data)
    return jsonify({'message': 'Profile updated successfully'}), 200

@app.route('/generate_quiz', methods=['POST'])
@token_required
def generate_quiz(current_user):
    data = request.json
    content_generator = ContentGenerator()
    
    # Add user's difficulty level if not specified in request
    if 'difficulty' not in data:
        data['difficulty'] = current_user.get('difficulty_level', 'beginner')
    
    quiz = content_generator.generate_quiz(
        topic=data['topic'],
        tags=data['tags'],
        age_group=data['age_group'],
        difficulty=data['difficulty'],
        num_questions=data['num_questions']
    )
    
    quiz_list = content_generator.store_quiz(quiz)
    
    # Store quiz attempt in user's history
    quiz_history_ref = db.collection('quiz_history').document()
    quiz_history_ref.set({
        'user_email': current_user['email'],
        'quiz_id': quiz_list['id'],
        'started_at': firestore.SERVER_TIMESTAMP,
        'completed': False,
        'score': None
    })
    
    return jsonify(quiz_list), 201

@app.route('/content', methods=['GET'])
@token_required
def get_personalized_content(current_user):
    content_query = db.collection('content').where('tags', 'array_contains_any', current_user['interests']).limit(5)
    content = [doc.to_dict() for doc in content_query.stream()]
    return jsonify(content), 200

@app.route('/progress', methods=['POST'])
@token_required
def update_progress(current_user):
    data = request.json
    progress_ref = db.collection('user_progress').document(f"{current_user['email']}_{data['content_id']}")
    
    progress_data = {
        'user_email': current_user['email'],
        'content_id': data['content_id'],
        'completed': data['completed'],
        'score': data.get('score'),
        'last_accessed': firestore.SERVER_TIMESTAMP
    }
    
    progress_ref.set(progress_data, merge=True)
    
    # Update user's achievements if applicable
    if data.get('completed') and data.get('score', 0) > 80:
        user_ref = db.collection('users').document(current_user['email'])
        user_ref.update({
            'achievements': firestore.ArrayUnion(['high_scorer'])
        })
    
    return jsonify({"message": "Progress updated successfully"}), 200

@app.route('/user/<string:user_email>/stats', methods=['GET'])
@token_required
def get_user_stats(current_user, user_email):
    if current_user['email'] != user_email:
        return jsonify({"error": "Unauthorized"}), 403
    
    progress_query = db.collection('user_progress').where('user_email', '==', user_email)
    progress_docs = progress_query.stream()
    
    completed_content = sum(1 for doc in progress_docs if doc.to_dict()['completed'])
    total_content = db.collection('content').count().get()[0][0].value
    
    scores = [doc.to_dict()['score'] for doc in progress_docs if 'score' in doc.to_dict()]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    return jsonify({
        "total_content": total_content,
        "completed_content": completed_content,
        "completion_rate": completed_content / total_content if total_content > 0 else 0,
        "average_score": round(avg_score, 2)
    }), 200

@app.route('/quiz/start', methods=['POST'])
@token_required
def start_quiz(current_user):
    data = request.json
    if not data.get('quiz_id'):
        return jsonify({'error': 'Quiz ID is required'}), 400
        
    # Create a new quiz attempt
    quiz_attempt = {
        'user_email': current_user['email'],
        'quiz_id': data['quiz_id'],
        'started_at': firestore.SERVER_TIMESTAMP,
        'status': 'in_progress',
        'current_question': 0,
        'answers': [],
        'score': 0,
        'completed_at': None
    }
    
    # Store the quiz attempt
    attempt_ref = db.collection('quiz_attempts').document()
    attempt_ref.set(quiz_attempt)
    
    return jsonify({
        'attempt_id': attempt_ref.id,
        'status': 'started',
        'started_at': datetime.now().isoformat()
    }), 201

@app.route('/quiz/submit-answer', methods=['POST'])
@token_required
def submit_answer(current_user):
    data = request.json
    if not all(k in data for k in ['attempt_id', 'question_index', 'answer']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    attempt_ref = db.collection('quiz_attempts').document(data['attempt_id'])
    attempt = attempt_ref.get()
    
    if not attempt.exists:
        return jsonify({'error': 'Quiz attempt not found'}), 404
    
    attempt_data = attempt.to_dict()
    if attempt_data['user_email'] != current_user['email']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if attempt_data['status'] == 'completed':
        return jsonify({'error': 'Quiz already completed'}), 400
    
    # Get the quiz to check the correct answer
    quiz_ref = db.collection('quizzes').document(attempt_data['quiz_id'])
    quiz = quiz_ref.get()
    
    if not quiz.exists:
        return jsonify({'error': 'Quiz not found'}), 404
    
    quiz_data = quiz.to_dict()
    question = quiz_data['questions'][data['question_index']]
    is_correct = data['answer'] == question['correct_answer']
    
    # Update the answers array
    answer_data = {
        'question_index': data['question_index'],
        'user_answer': data['answer'],
        'is_correct': is_correct,
        'submitted_at': firestore.SERVER_TIMESTAMP
    }
    
    # Update the attempt with the new answer
    attempt_ref.update({
        'answers': firestore.ArrayUnion([answer_data]),
        'current_question': data['question_index'] + 1
    })
    
    return jsonify({
        'is_correct': is_correct,
        'correct_answer': question['correct_answer'],
        'explanation': question.get('explanation', '')
    }), 200

@app.route('/quiz/complete', methods=['POST'])
@token_required
def complete_quiz(current_user):
    data = request.json
    if not data.get('attempt_id'):
        return jsonify({'error': 'Attempt ID is required'}), 400
    
    attempt_ref = db.collection('quiz_attempts').document(data['attempt_id'])
    attempt = attempt_ref.get()
    
    if not attempt.exists:
        return jsonify({'error': 'Quiz attempt not found'}), 404
    
    attempt_data = attempt.to_dict()
    if attempt_data['user_email'] != current_user['email']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Calculate final score
    correct_answers = sum(1 for answer in attempt_data['answers'] if answer['is_correct'])
    total_questions = len(attempt_data['answers'])
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Update the attempt with completion data
    completion_data = {
        'status': 'completed',
        'completed_at': firestore.SERVER_TIMESTAMP,
        'score': score,
        'total_questions': total_questions,
        'correct_answers': correct_answers
    }
    attempt_ref.update(completion_data)
    
    # Update user's progress in the learning path
    learning_path_ref = db.collection('learning_paths').document(current_user['email'])
    learning_path_ref.update({
        'completed_quizzes': firestore.ArrayUnion([attempt_data['quiz_id']]),
        'total_quizzes_taken': firestore.Increment(1),
        'total_score': firestore.Increment(score)
    })
    
    # Update user's achievements if applicable
    if score >= 80:
        user_ref = db.collection('users').document(current_user['email'])
        user_ref.update({
            'achievements': firestore.ArrayUnion(['quiz_master'])
        })
    
    return jsonify({
        'status': 'completed',
        'score': score,
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'completed_at': datetime.now().isoformat()
    }), 200

@app.route('/quiz/progress/<string:attempt_id>', methods=['GET'])
@token_required
def get_quiz_progress(current_user, attempt_id):
    attempt_ref = db.collection('quiz_attempts').document(attempt_id)
    attempt = attempt_ref.get()
    
    if not attempt.exists:
        return jsonify({'error': 'Quiz attempt not found'}), 404
    
    attempt_data = attempt.to_dict()
    if attempt_data['user_email'] != current_user['email']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'status': attempt_data['status'],
        'current_question': attempt_data['current_question'],
        'answers_submitted': len(attempt_data['answers']),
        'score': attempt_data.get('score', 0),
        'started_at': attempt_data['started_at'],
        'completed_at': attempt_data.get('completed_at')
    }), 200

@app.route('/user/quiz-history', methods=['GET'])
@token_required
def get_quiz_history(current_user):
    attempts_query = (db.collection('quiz_attempts')
                     .where('user_email', '==', current_user['email'])
                     .order_by('started_at', direction=firestore.Query.DESCENDING)
                     .limit(10))
    
    attempts = []
    for attempt in attempts_query.stream():
        attempt_data = attempt.to_dict()
        attempts.append({
            'attempt_id': attempt.id,
            'quiz_id': attempt_data['quiz_id'],
            'status': attempt_data['status'],
            'score': attempt_data.get('score', 0),
            'started_at': attempt_data['started_at'],
            'completed_at': attempt_data.get('completed_at')
        })
    
    return jsonify(attempts), 200

if __name__ == '__main__':
    app.run(debug=True)