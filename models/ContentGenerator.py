from dataclasses import dataclass
from typing import List
import google.generativeai as genai
from PromptGenerator import PromptGenerator, DifficultyLevel, ContentTag, AgeGroup
import firebase_admin
from firebase_admin import firestore, credentials
from datetime import timedelta, datetime

# Initialize the Gemini API
genai.configure(api_key='AIzaSyCu0WWVaqRtadJqmrf8GqBbA6UUVgLIeao')

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

    def generate_quiz(
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
        
        response = self.model.generate_content(prompt)
        
        print('Generated quiz:', response.text)

        return self._parse_quiz_response(response)
    
    def _parse_quiz_response(self, response):
        questions = []
        for question in response['questions']:
            question_text = question['question']
            options = question['options']
            correct_answer = question['correct_answer']
            explanation = question['explanation']
            learning_point = question['learning_point']
            
            quiz_question = QuizQuestion(
                question=question_text,
                options=options,
                correct_answer=correct_answer,
                explanation=explanation,
                learning_point=learning_point
            )
            
            questions.append(quiz_question)

        return questions

    def _generate_quiz_id(self):
        # hash the current timestamp to generate a unique ID
        return str(hash(datetime.now()))

    def store_quiz(self, quiz_data, expiration_seconds=3600):
        quiz_id = self._generate_quiz_id()
        quiz_ref = self.db.collection('temporary_quizzes').document(quiz_id)
        quiz_ref.set(quiz_data)

        # Set TTL using a server timestamp and expiration duration
        expiration_time = datetime.now() + timedelta(seconds=expiration_seconds)
        quiz_ref.set({'expires_at': expiration_time}, merge=True) 
        return quiz_id

    def get_quiz(self, quiz_id):
        quiz_ref = self.db.collection('temporary_quizzes').document(quiz_id)
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

        
def main():

    cred = credentials.Certificate("empowerwomen-fbbda-firebase-adminsdk-96bfo-3ab2cc60b5.json")
    firebase_admin.initialize_app(cred)

    content_generator = ContentGenerator()
    topic = "Understanding Your Menstrual Cycle"
    tags = [ContentTag.MENSTRUAL_HEALTH]
    age_group = AgeGroup.TEEN
    difficulty = DifficultyLevel.BEGINNER
    num_questions = 5

    quiz = content_generator.generate_quiz(
        topic=topic,
        tags=tags,
        age_group=age_group,
        difficulty=difficulty,
        num_questions=num_questions
    )

    quiz_id = content_generator.store_quiz(quiz)
    print(f"Quiz stored with ID: {quiz_id}")

    retrieved_quiz = content_generator.get_quiz(quiz_id)
    if retrieved_quiz:
        print("Retrieved quiz:", retrieved_quiz)
    else:
        print("Quiz not found or expired.")

if __name__ == "__main__":
    main()