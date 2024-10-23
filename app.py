from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import firestore, credentials

from ContentGenerator import ContentGenerator

app = Flask(__name__)
cred = credentials.Certificate("empowerwomen-fbbda-firebase-adminsdk-96bfo-3ab2cc60b5.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    user_ref = db.collection('users').document(data['email'])
    
    if user_ref.get().exists:
        return jsonify({"error": "User already exists"}), 400
    
    user_ref.set({
        'name': data['name'],
        'email': data['email'],
        'birthdate': data['birthdate'],
        'interests': data['interests'],
        'difficulty': data['difficulty'],
        'created_at': firestore.SERVER_TIMESTAMP
    })
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['GET'])
def login():
    email = request.args.get('email')
    user_ref = db.collection('users').document(email)
    return str(user_ref.get().exists)

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():


@app.route('/content', methods=['GET'])
def get_personalized_content():
    user_email = request.args.get('user_email')
    user_doc = db.collection('users').document(user_email).get()
    
    if not user_doc.exists:
        return jsonify({"error": "User not found"}), 404
    
    user_data = user_doc.to_dict()
    
    content_query = db.collection('content').where('tags', 'array_contains_any', user_data['interests']).limit(5)
    content = [doc.to_dict() for doc in content_query.stream()]
    
    return jsonify(content), 200

@app.route('/progress', methods=['POST'])
def update_progress():
    data = request.json
    progress_ref = db.collection('user_progress').document(f"{data['user_email']}_{data['content_id']}")
    
    progress_ref.set({
        'user_email': data['user_email'],
        'content_id': data['content_id'],
        'completed': data['completed'],
        'score': data.get('score'),
        'last_accessed': firestore.SERVER_TIMESTAMP
    }, merge=True)
    
    return jsonify({"message": "Progress updated successfully"}), 200

@app.route('/user/<string:user_email>/stats', methods=['GET'])
def get_user_stats(user_email):
    user_doc = db.collection('users').document(user_email).get()
    if not user_doc.exists:
        return jsonify({"error": "User not found"}), 404
    
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

if __name__ == '__main__':
    app.run(debug=True)