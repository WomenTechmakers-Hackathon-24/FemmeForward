from dataclasses import dataclass
from typing import List
import google.generativeai as genai
from enums import DifficultyLevel, AgeGroup, ContentTag
from PromptGenerator import PromptGenerator
from ContentValidator import ContentValidator
import firebase_admin
from firebase_admin import firestore
from datetime import timedelta, datetime

# Initialize the Gemini API
genai.configure(api_key='YOUR_API_KEY')

@dataclass
class QuizQuestion:
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    learning_point: str

class ContentGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.prompt_generator = PromptGenerator()
        self.db = firestore.client()

    async def generate_quiz(
        self,
        topic: str,
        tags: List[ContentTag],
        age_group: AgeGroup,
        difficulty: DifficultyLevel,
        num_questions: int = 5
    ) -> List[QuizQuestion]:
        prompt = self.prompt_generator.generate_prompt(
            topic=topic,
            tags=tags,
            age_group=age_group,
            difficulty=difficulty,
            content_type="quiz"
        )
        
        # Add specific instructions for structured output
        prompt += f"\nPlease generate {num_questions} questions following this exact format."
        
        response = await self.model.generate_content_async(prompt)
        
        # Parse the response and convert to QuizQuestion objects
        # Note: You'll need to implement proper parsing based on Gemini's output
        questions = self._parse_quiz_response(response.text)
        return questions

    def _parse_quiz_response(self, response_text: str) -> List[QuizQuestion]:
        # Implement parsing logic based on the actual response format
        # This is a placeholder implementation
        questions = []
        # Add parsing logic here
        return questions

    def store_quiz(self, quiz_data, expiration_seconds=3600):
        quiz_id = generate_unique_id()  ## @TODO: Implement this function
        quiz_ref = db.collection('temporary_quizzes').document(quiz_id)
        quiz_ref.set(quiz_data)

        # Set TTL using a server timestamp and expiration duration
        expiration_time = datetime.now() + timedelta(seconds=expiration_seconds)
        quiz_ref.set({'expires_at': expiration_time}, merge=True) 
        return quiz_id

    def get_quiz(self, quiz_id):
        quiz_ref = db.collection('temporary_quizzes').document(quiz_id)
        quiz_doc = quiz_ref.get()

        if quiz_doc.exists:
            quiz_data = quiz_doc.to_dict()
            if 'expires_at' in quiz_data and quiz_data['expires_at'] > datetime.now():
                return quiz_data  
            else:
                # Quiz expired, delete it from Firestore
                quiz_ref.delete()
                return None
        else:
            return None

        