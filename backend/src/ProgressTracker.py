from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
from firebase_admin import firestore, credentials
import firebase_admin

class UserDifficulty(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
@dataclass
class UserProgress:
    quiz_scores: List[float]
    completed_topics: List[str]
    current_difficulty: UserDifficulty

class AgeGroup(Enum):
    TEEN = "13-19"
    YOUNG_ADULT = "20-35"
    ADULT = "36-50"
    MATURE = "50+"

class Topic(Enum):
    fertility = "Fertility"
    contraception = "Contraception"
    period_care = "Period Care"
    pms = "PMS Relief"
    mental_health = "Mental Health"
    balanced_diet = "Balanced Diet"
    superfoods = "Superfoods"
    workouts = "Workouts"
    hormonal_health = "Hormonal Health"
    sleep = "Sleep Hygiene"
    stress_management = "Stress Management"
    mindfulness = "Mindfulness Practices"
    self_care = "Self-Care"
    skincare = "Skincare"
    haircare = "Haircare"
    bodycare = "Bodycare"
    preventive_care = "Preventive Care"
    pregnancy = "Pregnancy"
    puberty = "Puberty"
    habits = "Healthy Habits"
    self_esteem = "Self-Esteem"
    acceptance = "Body Acceptance"

class ProgressTracker:
    def __init__(self):
        self.firestore = firestore.client()   
        self.difficulty_thresholds = {
            UserDifficulty.BEGINNER: 70,
            UserDifficulty.INTERMEDIATE: 80,
            UserDifficulty.ADVANCED: 90
        }

    def determine_age_group(self, age: int) -> AgeGroup:
        if age >= 50:
            return AgeGroup.MATURE.value
        elif age >= 36:
            return AgeGroup.ADULT.value
        elif age >= 20:
            return AgeGroup.YOUNG_ADULT.value
        else:
            return AgeGroup.TEEN.value

    def get_user_progress(self, user_id: str) -> Optional[UserProgress]:
        """Retrieve user progress from Firestore."""
        user_ref = self.firestore.collection('users').document(user_id)
        user_data = user_ref.get().to_dict()
        
        if user_data:
            return UserProgress(
                quiz_scores=user_data.get('quiz_scores', []),
                completed_topics=user_data.get('completed_topics', []),
                current_difficulty=UserDifficulty(user_data.get('difficulty_level', 'beginner'))
            )
        else:
            return None

    def analyze_user_progress(self, user_progress: UserProgress) -> Dict:
        """Analyze user progress to determine content adjustments."""
        avg_score = sum(user_progress.quiz_scores[-3:]) / len(user_progress.quiz_scores[-3:]) \
            if user_progress.quiz_scores else 0
        
        content_adjustments = {
            'depth_level': self._calculate_depth_level(avg_score),
            'complexity_adjustment': self._determine_complexity(avg_score, user_progress.current_difficulty)
        }
        
        return content_adjustments
    
    def update_user_progress(self, user_id: str, quiz_score: float, completed_topic: str) -> None:
        """Update user progress in Firestore."""
        user_ref = self.firestore.collection('users').document(user_id)
        user_data = user_ref.get().to_dict()
        
        if user_data:
            quiz_scores = user_data.get('quiz_scores', [])
            completed_topics = user_data.get('completed_topics', [])
            
            quiz_scores.append(quiz_score)
            completed_topics.append(completed_topic)
            
            user_ref.set({
                'quiz_scores': quiz_scores[-10:],  # Keep only the last 10 scores
                'completed_topics': list(set(completed_topics)),  # Remove duplicates
                'difficulty_level': self._update_difficulty_level(quiz_scores)
            }, merge=True)

    def get_user_topics(self, user_id: str) -> List[str]:
        """Get personalized topics based on user interests and profile."""
        user_ref = self.firestore.collection('users').document(user_id)
        user_data = user_ref.get().to_dict()
        
        if not user_data:
            return []

        # Get user interests and age group
        interests = user_data.get('interests', [])
        age_group = user_data.get('age_group')
        
        # Define topic mapping based on interests
        interest_topic_mapping = {
            'reproductive health': [Topic.fertility, Topic.contraception],
            'menstrual health': [Topic.period_care, Topic.pms, Topic.hormonal_health],
            'mental health': [Topic.mental_health, Topic.mindfulness, Topic.stress_management],
            'physical health': [Topic.workouts, Topic.balanced_diet, Topic.habits],
            'general wellness': [Topic.self_care, Topic.skincare, Topic.bodycare],
            'emotional health': [Topic.self_esteem, Topic.acceptance, Topic.mindfulness]
        }

        # Age group specific restrictions
        age_restricted_topics = {
            'TEEN': {
                'allowed': [Topic.puberty, Topic.self_esteem, Topic.acceptance, Topic.period_care],
                'restricted': [Topic.fertility, Topic.contraception]
            },
            'YOUNG_ADULT': {
                'allowed': list(Topic),  # All topics allowed
                'restricted': []
            },
            'ADULT': {
                'allowed': list(Topic),
                'restricted': [Topic.puberty]
            }
        }
        # Collect relevant topics based on interests
        relevant_topics = set()
        for interest in interests:
            if interest in interest_topic_mapping:
                relevant_topics.update(topic.value for topic in interest_topic_mapping[interest])

        # Apply age group restrictions
        if age_group in age_restricted_topics:
            allowed_topics = {topic.value for topic in age_restricted_topics[age_group]['allowed']}
            restricted_topics = {topic.value for topic in age_restricted_topics[age_group]['restricted']}
            relevant_topics = relevant_topics.intersection(allowed_topics)
            relevant_topics = relevant_topics - restricted_topics

        return list(relevant_topics)

    def _calculate_depth_level(self, avg_score: float) -> str:
        if avg_score >= 90:
            return "deep_dive"
        elif avg_score >= 75:
            return "comprehensive"
        else:
            return "foundational"

    def _determine_complexity(self, avg_score: float, current_difficulty: UserDifficulty) -> Dict:
        """Determine content complexity adjustments."""
        threshold = self.difficulty_thresholds[current_difficulty]
        
        return {
            'should_increase': avg_score > threshold,
            'should_decrease': avg_score < threshold - 15,
            'adjustment_factor': (avg_score - threshold) / 100
        }
    
    def _update_difficulty_level(self, quiz_scores: List[float]) -> UserDifficulty:
        """Update user difficulty level based on recent quiz scores."""
        MIN_QUIZZES = 5 # Minimum number of quizzes to consider for difficulty level
        
        if not quiz_scores:
            return UserDifficulty.BEGINNER.value
        
        # If less than 5 quizzes taken, cap at INTERMEDIATE
        if len(quiz_scores) < MIN_QUIZZES:
            avg_score = sum(quiz_scores) / len(quiz_scores)
            if avg_score >= 60:
                return UserDifficulty.INTERMEDIATE.value
            return UserDifficulty.BEGINNER.value

        avg_score = sum(quiz_scores) / len(quiz_scores)
        
        if avg_score >= 80:
            return UserDifficulty.ADVANCED.value
        elif avg_score >= 60:
            return UserDifficulty.INTERMEDIATE.value
        else:
            return UserDifficulty.BEGINNER.value    