from enum import Enum
from typing import List
from ProgressTracker import ProgressTracker, AgeGroup

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ContentTag(Enum):
    REPRODUCTIVE_HEALTH = "reproductive health"
    MENSTRUAL_HEALTH = "menstrual health"
    MENTAL_HEALTH = "mental health"
    PHYSICAL_HEALTH = "physical health"
    GENERAL_WELLNESS = "general wellness"
    EMOTIONAL_HEALTH = "emotional health"

class PromptGenerator:
    def __init__(self):
        self.progress_tracker = ProgressTracker()

    def generate_adaptive_content(
        self,
        topic: str,
        tags: List[str],
        age_group: str,
        difficulty: str,
        user_id: str,
        num_questions: int
    ) -> str:
        user_progress = self.progress_tracker.get_user_progress(user_id)
        adjustments = self.progress_tracker.analyze_user_progress(user_progress)
        age_appropriate_language = {
            AgeGroup.TEEN: "Use friendly, clear language with relatable examples and social media references.",
            AgeGroup.YOUNG_ADULT: "Use straightforward language with practical examples and contemporary references.",
            AgeGroup.ADULT: "Use comprehensive language with detailed examples and professional context.",
            AgeGroup.MATURE: "Use respectful, thorough language with age-appropriate health considerations."
        }

        depth_instructions = {
            "deep_dive": "Include advanced concepts, recent research, and detailed analysis.",
            "comprehensive": "Provide thorough explanations with practical applications.",
            "foundational": "Focus on core concepts with additional support and examples."
        }

        return f"""
        Create a personalized {difficulty}-level quiz about {topic} with {num_questions} questions
        for {age_group} age group.

        Content Personalization:
        {age_appropriate_language.get(AgeGroup(age_group), "Use clear, appropriate language.")}
        {depth_instructions.get(adjustments['depth_level'], "Adjust depth appropriately.")}
        
        Complexity Adjustment: {adjustments['complexity_adjustment']['adjustment_factor']}

        Content Guidelines:
        1. Adapt explanations based on previous performance
        2. Incorporate personalized examples
        3. Address specific knowledge gaps
        4. Build upon demonstrated strengths
        5. Include scaffolded learning elements
        6. Provide targeted feedback opportunities
        7. Integrate real-world applications
        8. Include motivational elements
        9. Reference related completed topics
        10. Prepare for upcoming concepts

        Topic Tags: {', '.join(tag for tag in tags)}

        Required Elements:
        1. Personalized learning objectives
        2. Knowledge check points
        3. Real-time feedback mechanisms
        4. Progress indicators
        5. Achievement milestones
        6. Adaptive challenge levels
        7. Contextual help resources
        8. Performance-based recommendations
        9. Confidence-building elements
        10. Next steps guidance

        Format: {self._get_enhanced_format_instructions('quiz')}
        """

    def _get_enhanced_format_instructions(self, content_type: str) -> str:
        formats = {
            "quiz": """
            Please format as a JSON object with:
            {
                "questions": [
                    {
                        "id": "unique_identifier",
                        "question": "Question text",
                        "difficulty_level": "current_difficulty",
                        "topic_tag": "relevant_tag",
                        "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
                        "correct_answer": "correct_option",
                        "explanation": "detailed_explanation",
                        "learning_point": "key_takeaway"
                    }
                ],
                "adaptive_elements": {
                    "difficulty_progression": "progression_path",
                    "topic_relationships": ["related_topics"],
                    "reinforcement_points": ["points_to_reinforce"]
                }
            }
            """,
            "lesson": """
            Format the adaptive lesson with:
            1. Personalized Introduction
               - Prior knowledge activation
               - Learning path context
               - Personal relevance
            
            2. Core Content
               - Scaffolded concepts
               - Progressive complexity
               - Adaptive examples
            
            3. Interactive Elements
               - Knowledge checks
               - Reflection points
               - Application exercises
            
            4. Support Resources
               - Targeted help
               - Extension materials
               - Review suggestions
            
            5. Progress Tracking
               - Achievement markers
               - Mastery indicators
               - Next steps preview
            
            6. Personalized Summary
               - Key takeaways
               - Individual focus points
               - Connection to goals
            """
        }
        return formats.get(content_type, "Use adaptive, structured formatting.")