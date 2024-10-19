from enums import DifficultyLevel, AgeGroup, ContentTag
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Set, Optional, Any


@dataclass
class UserProgress:
    user_id: str
    completed_quizzes: List[str]
    completed_lessons: List[str]
    topic_scores: Dict[str, float]
    streak_days: int
    last_activity: datetime
    badges: Set[str]
    total_points: int
    difficulty_levels: Dict[str, int]  # Topic to max difficulty level mapping


class ProgressTracker:
    def __init__(self):
        self.user_progress: Dict[str, UserProgress] = {}
        self.badges = {
            "QUICK_LEARNER": "Complete 5 quizzes with >80% score",
            "CONSISTENT_LEARNER": "7-day streak",
            "TOPIC_MASTER": "Complete all difficulty levels in a topic",
            "KNOWLEDGE_SEEKER": "Complete 10 lessons",
            "QUIZ_CHAMPION": "Perfect score in advanced quiz"
        }

    def update_progress(
        self, 
        user_id: str, 
        activity_type: str, 
        content_id: str, 
        score: Optional[float] = None
    ) -> Dict[str, Any]:
        if user_id not in self.user_progress:
            self.user_progress[user_id] = UserProgress(
                user_id=user_id,
                completed_quizzes=[],
                completed_lessons=[],
                topic_scores={},
                streak_days=0,
                last_activity=datetime.now(),
                badges=set(),
                total_points=0,
                difficulty_levels=defaultdict(int)
            )

        progress = self.user_progress[user_id]
        
        # Update activity records
        if activity_type == "quiz":
            progress.completed_quizzes.append(content_id)
            if score is not None:
                progress.topic_scores[content_id] = score
                progress.total_points += int(score * 100)
        elif activity_type == "lesson":
            progress.completed_lessons.append(content_id)
            progress.total_points += 50

        # Update streak
        last_activity = progress.last_activity
        if datetime.now() - last_activity <= timedelta(days=1):
            progress.streak_days += 1
        else:
            progress.streak_days = 1
        progress.last_activity = datetime.now()

        # Check and award badges
        new_badges = self._check_badges(progress)
        
        return {
            "updated_progress": progress,
            "new_badges": new_badges,
            "total_points": progress.total_points,
            "streak_days": progress.streak_days
        }

    def _check_badges(self, progress: UserProgress) -> Set[str]:
        new_badges = set()
        
        if len([s for s in progress.topic_scores.values() if s > 0.8]) >= 5:
            new_badges.add("QUICK_LEARNER")
        
        if progress.streak_days >= 7:
            new_badges.add("CONSISTENT_LEARNER")
        
        if len(progress.completed_lessons) >= 10:
            new_badges.add("KNOWLEDGE_SEEKER")
        
        if any(score == 1.0 for score in progress.topic_scores.values()):
            new_badges.add("QUIZ_CHAMPION")
        
        progress.badges.update(new_badges)
        return new_badges