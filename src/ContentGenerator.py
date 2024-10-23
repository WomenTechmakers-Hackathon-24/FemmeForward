from dataclasses import dataclass
import json
from typing import List
from PromptGenerator import PromptGenerator, DifficultyLevel, ContentTag, AgeGroup
from firebase_admin import firestore
from datetime import timedelta, datetime, timezone
import google.generativeai as genai

@dataclass
class QuizQuestion:
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    learning_point: str

class ContentGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
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
        prompt += (
            f"\nPlease generate {num_questions} educational quiz questions following this exact format." 
            "Avoid any inappropriate content, ensuring that the questions are safe and suitable for all audiences."
        )
        response = self.model.generate_content(prompt, generation_config={'response_mime_type': 
                                                                          'application/json', })

        return self._parse_quiz_response(response.text)

    def _parse_quiz_response(self, response):
        parsed_questions = []
        question_data = json.loads(response)
        for question in question_data:            
            try:
                quiz_question = QuizQuestion(
                    question=question['question'],
                    options=question['options'],
                    correct_answer=question['correct_answer'],
                    explanation=question['explanation'],
                    learning_point=question['learning_point']
                )

                parsed_questions.append(quiz_question)
                    
            except json.JSONDecodeError as e:
                print(f"Error parsing question JSON: {e}")
                continue
            
        return parsed_questions

    def _generate_quiz_id(self):
        # hash the current timestamp to generate a unique ID
        return str(hash(datetime.now()))

    def store_quiz(self, quiz_data, expiration_seconds=3600):
        quiz_list = []
        for question in quiz_data:
            question = question.__dict__
            quiz_id = self._generate_quiz_id()
            quiz_ref = self.db.collection('temporary_quizzes').document(quiz_id)
            # Set TTL using a server timestamp and expiration duration
            expiration_time = datetime.now(timezone.utc) + timedelta(seconds=expiration_seconds)
            question['expires_at'] = expiration_time
            quiz_ref.set(question, merge=True)
            quiz_list.append(quiz_id)
        return quiz_list

    def get_quiz(self, quiz_id):
        quiz_ref = self.db.collection('temporary_quizzes').document(quiz_id)
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

# def main():
#     cred = credentials.Certificate("empowerwomen-fbbda-firebase-adminsdk-96bfo-3ab2cc60b5.json")
#     firebase_admin.initialize_app(cred)

#     content_generator = ContentGenerator()
#     topic = "Female Nutrition Basics"
#     tags = [ContentTag.NUTRITION]
#     age_group = AgeGroup.TEEN
#     difficulty = DifficultyLevel.BEGINNER
#     num_questions = 3

#     quiz = content_generator.generate_quiz(
#         topic=topic,
#         tags=tags,
#         age_group=age_group,
#         difficulty=difficulty,
#         num_questions=num_questions
#     )

#     quiz_list = content_generator.store_quiz(quiz)
#     print("Stored quizzes:", quiz_list)

#     for quiz_id in quiz_list:
#         quiz_data = content_generator.get_quiz(quiz_id)
#         if quiz_data:
#             print("Retrieved quiz:", quiz_data)
#         else:
#             print("Quiz not found or expired.")

# if __name__ == "__main__":
#     main()