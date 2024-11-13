from dataclasses import dataclass
import json
import logging
import uuid
from typing import List, Dict, Any
from PromptGenerator import PromptGenerator, ContentTag
from firebase_admin import firestore, credentials
import firebase_admin
from datetime import timedelta, datetime, timezone
import google.generativeai as genai

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
@dataclass
class QuizQuestion:
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    learning_point: str
    difficulty_level: str
    topic_tag: str

@dataclass
class QuizMetadata:
    topic: str
    difficulty: str
    adaptive_elements: Dict[str, Any]

@dataclass
class ParsedQuiz:
    questions: List[QuizQuestion]
    metadata: QuizMetadata
    total_points: int
    learning_objectives: List[str]

class QuizParsingError(Exception):
    """Custom exception for quiz parsing errors"""
    pass

class ContentGenerator:
    def __init__(self):
        # Configure safety settings
        self.generation_config = {
            'temperature': 0.7,
            'top_p': 0.8,
            'top_k': 40,
            'safety_settings': [
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ]
        }
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.prompt_generator = PromptGenerator()
        self.db = firestore.client()

    def list_content_tags(self):
        return [tag.value for tag in ContentTag]
        
    def _parse_quiz_response(self, response, topic, difficulty) -> ParsedQuiz:
        parsed_questions = []
        question_data = json.loads(response)
        for question in question_data['questions']:            
            try:
                quiz_question = QuizQuestion(
                    question=question['question'],
                    options=question['options'],
                    correct_answer=question['correct_answer'],
                    explanation=question['explanation'],
                    learning_point=question['learning_point'],
                    difficulty_level=question['difficulty_level'],
                    topic_tag=question['topic_tag']
                )

                parsed_questions.append(quiz_question)

            except json.JSONDecodeError as e:
                print(f"Error parsing question JSON: {e}")
                continue

        metadata = self._parse_quiz_metadata(question_data, topic, difficulty)
        learning_objectives = self._extract_learning_objectives(question_data)

        return ParsedQuiz(
            questions=parsed_questions,
            metadata=metadata,
            total_points=len(parsed_questions),
            learning_objectives=learning_objectives
        )
    
    def _parse_quiz_metadata(
        self, 
        quiz_data: Dict, 
        topic: str, 
        difficulty: str
    ) -> QuizMetadata:
        """Parse and validate quiz metadata."""
        
        return QuizMetadata(
            topic=topic,
            difficulty=difficulty,
            adaptive_elements=quiz_data.get('adaptive_elements', {})
        )

    def _extract_learning_objectives(self, quiz_data: Dict) -> List[str]:
        """Extract learning objectives from quiz data."""
        objectives = []
        
        # Collect unique learning points from questions
        if 'questions' in quiz_data:
            for question in quiz_data['questions']:
                if 'learning_point' in question:
                    objectives.append(question['learning_point'])
                    
        # Remove duplicates while preserving order
        return list(dict.fromkeys(objectives))

    def generate_quiz(
        self,
        topic: str,
        tags: List[str],
        age_group: str,
        difficulty: str,
        user_id: str,
        num_questions: int
    ) -> ParsedQuiz:
        """Generate and parse a quiz in one step."""
        prompt = self.prompt_generator.generate_adaptive_content(
            topic=topic,
            tags=tags,
            age_group=age_group,
            difficulty=difficulty,
            user_id=user_id,
            num_questions=num_questions
        )
        response = self.model.generate_content(prompt, generation_config = {"response_mime_type": 
                                                                           "application/json"})
        return self._parse_quiz_response(response.text, topic, difficulty)

    def store_quiz(self, quiz_data, expiration_seconds=3600):
        quiz_id = str(uuid.uuid4())  # Generate a unique quiz ID
        quiz_ref = self.db.collection('content').document(quiz_id)
        expiration_time = datetime.now(timezone.utc) + timedelta(seconds=expiration_seconds)

        # Set quiz-level metadata
        quiz_ref.set({
            'quiz_id': quiz_id,
            'expires_at': expiration_time
        })

        # Store each question as a sub-document in the 'questions' sub-collection
        for question in quiz_data:
            question_dict = question.__dict__
            question_dict['expires_at'] = expiration_time
            question_id = str(uuid.uuid4())  # Unique ID for each question

            # Store each question under 'content/{quiz_id}/questions/{question_id}'
            question_ref = quiz_ref.collection('questions').document(question_id)
            question_ref.set(question_dict)

        return quiz_id

    def get_quiz(self, quiz_id):
        quiz_ref = self.db.collection('content').document(quiz_id)
        quiz_doc = quiz_ref.get()

        if quiz_doc.exists:
            quiz_data = quiz_doc.to_dict()
            if 'expires_at' in quiz_data and quiz_data['expires_at'] > datetime.now(timezone.utc):
                return quiz_data  
            else:
                # Quiz expired, delete it from Firestore
                quiz_ref.delete()
                return None
        else:
            return None
        
if __name__ == "__main__":
    genai.configure(api_key='AIzaSyA1cVBZoZmq8dm3qCQuzu5_k6iVOWbr-5Q')
    firebase_admin.initialize_app(credentials.Certificate("empowerwomen-fbbda-firebase-adminsdk-96bfo-3ab2cc60b5.json"))
    content_generator = ContentGenerator()
    quiz_data = content_generator.generate_quiz(
        topic="Mental Health",
        tags=["mental health", "general wellness"],
        age_group="13-19",
        difficulty="INTERMEDIATE",
        user_id="annmargaret.silva@gmail.com",
        num_questions=5
    )

    quiz_id = content_generator.store_quiz(quiz_data.questions)
    print(f"Quiz ID: {quiz_id}")

    retrieved_quiz = content_generator.get_quiz(quiz_id)
    if retrieved_quiz:
        print(f"Retrieved quiz: {retrieved_quiz}")
    else:
        print("Quiz not found or expired.")