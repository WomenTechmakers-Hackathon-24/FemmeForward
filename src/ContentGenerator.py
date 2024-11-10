from dataclasses import dataclass
import json
import logging
from typing import List, Dict, Any
from PromptGenerator import PromptGenerator, DifficultyLevel, ContentTag, AgeGroup
from firebase_admin import firestore
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
        difficulty: DifficultyLevel
    ) -> QuizMetadata:
        """Parse and validate quiz metadata."""
        
        return QuizMetadata(
            topic=topic,
            difficulty=difficulty.value,
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
        tags: List[ContentTag],
        age_group: AgeGroup,
        difficulty: DifficultyLevel,
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

    def _generate_quiz_id(self):
        # hash the current timestamp to generate a unique ID
        return str(hash(datetime.now()))

    def store_quiz(self, quiz_data, expiration_seconds=3600):
        quiz_list = []
        for question in quiz_data:
            question = question.__dict__
            quiz_id = self._generate_quiz_id()
            quiz_ref = self.db.collection('content').document(quiz_id)
            # Set TTL using a server timestamp and expiration duration
            expiration_time = datetime.now(timezone.utc) + timedelta(seconds=expiration_seconds)
            question['expires_at'] = expiration_time
            quiz_ref.set(question, merge=True)
            quiz_list.append(quiz_id)
        return quiz_list

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