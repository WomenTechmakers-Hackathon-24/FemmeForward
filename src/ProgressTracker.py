from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Set, Optional, Any
from firebase_admin import firestore
from PromptGenerator import DifficultyLevel, ContentTag
@dataclass
class UserProgress:
    quiz_scores: List[float]
    completed_topics: List[str]
    current_difficulty: DifficultyLevel

class ProgressTracker:
    def __init__(self):
        self.firestore = firestore.client()
        self.topic_prerequisites = {
            ContentTag.REPRODUCTIVE_HEALTH: [ContentTag.GENERAL_WELLNESS],
            ContentTag.MENSTRUAL_HEALTH: [ContentTag.REPRODUCTIVE_HEALTH],
            ContentTag.HORMONAL_HEALTH: [ContentTag.REPRODUCTIVE_HEALTH],
            ContentTag.SEXUAL_HEALTH: [ContentTag.REPRODUCTIVE_HEALTH],
            ContentTag.PREGNANCY: [ContentTag.REPRODUCTIVE_HEALTH, ContentTag.HORMONAL_HEALTH],
        }
        
        self.difficulty_thresholds = {
            DifficultyLevel.BEGINNER: 70,
            DifficultyLevel.INTERMEDIATE: 80,
            DifficultyLevel.ADVANCED: 90
        }

    def get_user_progress(self, user_id: str) -> Optional[UserProgress]:
        """Retrieve user progress from Firestore."""
        user_ref = self.firestore.collection('users').document(user_id)
        user_data = user_ref.get().to_dict()
        
        if user_data:
            return UserProgress(
                quiz_scores=user_data.get('quiz_scores', []),
                completed_topics=user_data.get('completed_topics', []),
                current_difficulty=DifficultyLevel(user_data.get('current_difficulty', 'beginner'))
            )
        else:
            return None

    def analyze_user_progress(self, user_progress: UserProgress) -> Dict:
        """Analyze user progress to determine content adjustments."""
        avg_score = sum(user_progress.quiz_scores[-3:]) / len(user_progress.quiz_scores[-3:]) \
            if user_progress.quiz_scores else 0
        
        content_adjustments = {
            'depth_level': self._calculate_depth_level(avg_score),
            'recommended_tags': self._get_recommended_tags(user_progress),
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

    def _get_recommended_tags(self, user_progress: UserProgress) -> List[ContentTag]:
        """Get recommended tags based on completed topics and prerequisites."""
        available_tags = set(ContentTag)
        for completed in user_progress.completed_topics:
            prereqs = self.topic_prerequisites.get(ContentTag(completed), [])
            if all(prereq in user_progress.completed_topics for prereq in prereqs):
                available_tags.add(ContentTag(completed))
        return list(available_tags)

    def _determine_complexity(self, avg_score: float, current_difficulty: DifficultyLevel) -> Dict:
        """Determine content complexity adjustments."""
        threshold = self.difficulty_thresholds[current_difficulty]
        
        return {
            'should_increase': avg_score > threshold,
            'should_decrease': avg_score < threshold - 15,
            'adjustment_factor': (avg_score - threshold) / 100
        }