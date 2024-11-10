from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
from firebase_admin import firestore

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
            return AgeGroup.MATURE
        elif age >= 36:
            return AgeGroup.ADULT
        elif age >= 20:
            return AgeGroup.YOUNG_ADULT
        else:
            return AgeGroup.TEEN

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
                'current_difficulty': self._update_difficulty_level(quiz_scores)
            }, merge=True)

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