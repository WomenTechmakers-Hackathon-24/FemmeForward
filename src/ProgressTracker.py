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
    strengths: List[ContentTag]
    areas_for_improvement: List[ContentTag]
    engagement_metrics: Dict[ContentTag, float]

class ProgressTracker:
    def __init__(self):
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

    def analyze_user_progress(self, user_progress: UserProgress) -> Dict:
        """Analyze user progress to determine content adjustments."""
        avg_score = sum(user_progress.quiz_scores[-3:]) / len(user_progress.quiz_scores[-3:]) \
            if user_progress.quiz_scores else 0
        
        content_adjustments = {
            'depth_level': self._calculate_depth_level(avg_score),
            'focus_areas': self._identify_focus_areas(user_progress),
            'recommended_tags': self._get_recommended_tags(user_progress),
            'complexity_adjustment': self._determine_complexity(avg_score, user_progress.current_difficulty)
        }
        
        return content_adjustments

    def _calculate_depth_level(self, avg_score: float) -> str:
        if avg_score >= 90:
            return "deep_dive"
        elif avg_score >= 75:
            return "comprehensive"
        else:
            return "foundational"

    def _identify_focus_areas(self, user_progress: UserProgress) -> List[str]:
        """Identify areas needing more focus based on engagement and performance."""
        focus_areas = []
        for tag, engagement in user_progress.engagement_metrics.items():
            if tag in user_progress.areas_for_improvement or engagement < 0.6:
                focus_areas.append(tag)
        return focus_areas

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