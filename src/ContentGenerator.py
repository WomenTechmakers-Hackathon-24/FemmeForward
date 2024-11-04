from dataclasses import dataclass
import json
from typing import List, Dict, Any
from PromptGenerator import PromptGenerator, DifficultyLevel, ContentTag, AgeGroup
from firebase_admin import firestore
from datetime import timedelta, datetime, timezone
import google.generativeai as genai
from ProgressTracker import ProgressTracker, UserProgress

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
    target_understanding_level: str
    minimum_passing_score: float
    mastery_criteria: str
    adaptive_elements: Dict[str, Any]

@dataclass
class ParsedQuiz:
    questions: List[QuizQuestion]
    metadata: QuizMetadata
    total_points: int
    estimated_duration: int
    prerequisites: List[str]
    learning_objectives: List[str]

class QuizParsingError(Exception):
    """Custom exception for quiz parsing errors"""
    pass

class ContentGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.prompt_generator = PromptGenerator()
        self.db = firestore.client()
        self.progress_tracker = ProgressTracker()


    def _parse_quiz_response(self, response: str, topic: str) -> ParsedQuiz:
        """
        Parse and validate the quiz response from Gemini.
        """
        try:
            # Parse the JSON response
            quiz_data = json.loads(response)
            
            # Validate overall structure
            if not isinstance(quiz_data, dict) or 'questions' not in quiz_data:
                raise QuizParsingError("Invalid quiz format: missing 'questions' array")
                
            parsed_questions = []
            question_difficulties = []
            
            # Process each question
            for idx, question in enumerate(quiz_data['questions'], 1):
                try:
                    # Validate required fields
                    required_fields = ['question', 'options', 'correct_answer', 
                                    'explanation', 'learning_point', 'difficulty_level', 
                                    'topic_tag']
                    
                    missing_fields = [field for field in required_fields 
                                    if field not in question or not question[field]]
                    
                    if missing_fields:
                        raise QuizParsingError(
                            f"Question {idx}: Missing required fields: {', '.join(missing_fields)}"
                        )
                    
                    # Validate options format
                    if not isinstance(question['options'], list) or len(question['options']) < 2:
                        raise QuizParsingError(
                            f"Question {idx}: Invalid options format"
                        )
                    
                    # Validate correct answer is in options
                    if question['correct_answer'] not in question['options']:
                        raise QuizParsingError(
                            f"Question {idx}: Correct answer not in options"
                        )
                    
                    # Create QuizQuestion object with optional fields
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
                    question_difficulties.append(question['difficulty_level'])
                    
                except KeyError as e:
                    raise QuizParsingError(f"Question {idx}: Missing required field {e}")
                    
            # Parse metadata
            metadata = self._parse_quiz_metadata(quiz_data, topic, question_difficulties)
            
            # Calculate quiz metrics
            total_points = len(parsed_questions)
            estimated_duration = self._calculate_estimated_duration(parsed_questions)
            
            # Extract prerequisites and learning objectives
            prerequisites = self._extract_prerequisites(quiz_data)
            learning_objectives = self._extract_learning_objectives(quiz_data)
            
            return ParsedQuiz(
                questions=parsed_questions,
                metadata=metadata,
                total_points=total_points,
                estimated_duration=estimated_duration,
                prerequisites=prerequisites,
                learning_objectives=learning_objectives
            )
            
        except json.JSONDecodeError as e:
            raise QuizParsingError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise QuizParsingError(f"Error parsing quiz: {e}")

    def _parse_quiz_metadata(
        self, 
        quiz_data: Dict, 
        topic: str, 
        question_difficulties: List[str]
    ) -> QuizMetadata:
        """Parse and validate quiz metadata."""
        metadata = quiz_data.get('performance_metrics', {})
        adaptive_elements = quiz_data.get('adaptive_elements', {})
        
        # Determine overall difficulty based on question difficulties
        difficulty = max(set(question_difficulties), key=question_difficulties.count)
        
        return QuizMetadata(
            topic=topic,
            difficulty=difficulty,
            target_understanding_level=metadata.get('target_understanding_level', 'proficient'),
            minimum_passing_score=float(metadata.get('minimum_passing_score', 70)),
            mastery_criteria=metadata.get('mastery_criteria', 'standard'),
            adaptive_elements=adaptive_elements
        )

    def _calculate_estimated_duration(self, questions: List[QuizQuestion]) -> int:
        """Calculate estimated duration in minutes based on question complexity."""
        base_time_per_question = 2  # minutes
        total_time = 0
        
        for question in questions:
            # Adjust time based on difficulty
            difficulty_multiplier = {
                'beginner': 0.8,
                'intermediate': 1.0,
                'advanced': 1.2
            }.get(question.difficulty_level.lower(), 1.0)
            
            # Add time for additional elements
            additional_time = (
                (len(question.hints or []) * 0.5) +  # 30 seconds per hint
                (len(question.follow_up_questions or []) * 1) +  # 1 minute per follow-up
                (2 if question.misconception_address else 0)  # 2 minutes for misconception
            )
            
            question_time = (base_time_per_question * difficulty_multiplier) + additional_time
            total_time += question_time
            
        return round(total_time)

    def _extract_prerequisites(self, quiz_data: Dict) -> List[str]:
        """Extract prerequisites from quiz data."""
        prereqs = quiz_data.get('adaptive_elements', {}).get('prerequisite_concepts', [])
        return [str(prereq) for prereq in prereqs]

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

    async def generate_quiz(
        self,
        topic: str,
        tags: List[ContentTag],
        age_group: AgeGroup,
        difficulty: DifficultyLevel,
        user_progress: UserProgress
    ) -> ParsedQuiz:
        """Generate and parse a quiz in one step."""
        content = await self.prompt_generator.generate_adaptive_content(
            topic=topic,
            tags=tags,
            age_group=age_group,
            difficulty=difficulty,
            content_type="quiz",
            user_progress=user_progress
        )
        
        return self._parse_quiz_response(json.dumps(content['content']), topic)

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