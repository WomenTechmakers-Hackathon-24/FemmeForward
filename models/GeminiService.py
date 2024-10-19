from enum import Enum
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from datetime import datetime
import json
import asyncio

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ContentTag(Enum):
    REPRODUCTIVE_HEALTH = "reproductive_health"
    MENSTRUAL_HEALTH = "menstrual_health"
    MENTAL_HEALTH = "mental_health"
    NUTRITION = "nutrition"
    FITNESS = "fitness"
    HORMONAL_HEALTH = "hormonal_health"
    SEXUAL_HEALTH = "sexual_health"
    PREVENTIVE_CARE = "preventive_care"
    PREGNANCY = "pregnancy"
    TEEN_HEALTH = "teen_health"
    BODY_IMAGE = "body_image"
    GENERAL_WELLNESS = "general_wellness"

class AgeGroup(Enum):
    TEEN = "13-19"
    YOUNG_ADULT = "20-35"
    ADULT = "36-50"
    MATURE = "50+"

class WomensHealthEducation:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self._cache = {}
        
    async def generate_quiz(
        self,
        topic: str,
        difficulty: DifficultyLevel,
        age_group: AgeGroup,
        tags: List[ContentTag],
        num_questions: int = 5
    ) -> Dict[str, Any]:
        """
        Generate an age-appropriate, difficulty-adjusted quiz on women's health topics
        """
        prompt = self._create_quiz_prompt(topic, difficulty, age_group, num_questions)
        
        safety_check = self._validate_content_appropriateness(topic, age_group)
        if not safety_check['is_appropriate']:
            return {"error": safety_check['message']}

        response = await self.model.generate_content_async(prompt)
        
        quiz = self._format_quiz_response(response.text)
        quiz['metadata'] = {
            'difficulty': difficulty.value,
            'age_group': age_group.value,
            'tags': [tag.value for tag in tags],
            'created_at': datetime.now().isoformat()
        }
        
        return quiz

    def _create_quiz_prompt(
        self,
        topic: str,
        difficulty: DifficultyLevel,
        age_group: AgeGroup,
        num_questions: int
    ) -> str:
        prompts = {
            DifficultyLevel.BEGINNER: {
                AgeGroup.TEEN: "Create a friendly, easy-to-understand quiz suitable for teenagers.",
                AgeGroup.YOUNG_ADULT: "Create a straightforward, informative quiz with basic concepts.",
            },
            DifficultyLevel.INTERMEDIATE: {
                AgeGroup.TEEN: "Create an engaging quiz with moderate complexity, suitable for informed teens.",
                AgeGroup.YOUNG_ADULT: "Create a comprehensive quiz with practical examples and scenarios.",
            },
            DifficultyLevel.ADVANCED: {
                AgeGroup.TEEN: "Create a detailed quiz covering complex topics in an accessible way.",
                AgeGroup.YOUNG_ADULT: "Create an in-depth quiz with technical terms and detailed explanations.",
            }
        }

        base_prompt = prompts.get(difficulty, {}).get(age_group, "Create a general health quiz")
        
        return f"""{base_prompt}
        Topic: {topic}
        Number of questions: {num_questions}

        Requirements:
        1. Each question should be multiple choice with 4 options
        2. Provide a detailed explanation for each answer
        3. Include real-world examples or scenarios where applicable
        4. Use age-appropriate language and examples
        5. Focus on practical, actionable knowledge
        6. Include evidence-based information
        7. Avoid triggering or sensitive content
        8. Include positive, empowering messaging

        Format each question as:
        {{
            "question": "Question text",
            "options": ["A) option", "B) option", "C) option", "D) option"],
            "correct_answer": "B",
            "explanation": "Detailed explanation",
            "learning_point": "Key takeaway"
        }}
        """

    async def generate_interactive_lesson(
        self,
        topic: str,
        difficulty: DifficultyLevel,
        age_group: AgeGroup,
        tags: List[ContentTag]
    ) -> Dict[str, Any]:
        """
        Generate an interactive lesson with explanations, examples, and check-in questions
        """
        prompt = f"""
        Create an interactive lesson about {topic} suitable for {age_group.value} age group 
        at {difficulty.value} level.

        Include:
        1. Introduction to the topic
        2. Key concepts explained simply
        3. Real-life examples and scenarios
        4. 2-3 check-in questions throughout
        5. Summary of main points
        6. Action items or practical tips
        7. Resources for learning more

        Make sure the content is:
        - Age-appropriate
        - Scientifically accurate
        - Empowering and positive
        - Practical and applicable
        - Culturally sensitive
        """

        response = await self.model.generate_content_async(prompt)
        return self._format_lesson_response(response.text)

    def _validate_content_appropriateness(
        self,
        topic: str,
        age_group: AgeGroup
    ) -> Dict[str, Any]:
        """
        Validate if the topic is appropriate for the age group
        """
        # Add your validation logic here
        return {"is_appropriate": True, "message": "Content appropriate for age group"}

    def _format_quiz_response(self, response: str) -> Dict[str, Any]:
        """
        Format the raw quiz response into a structured format
        """
        try:
            # Add your formatting logic here
            questions = json.loads(response)
            return {
                "questions": questions,
                "total_questions": len(questions),
                "passing_score": 0.7 * len(questions)
            }
        except json.JSONDecodeError:
            return {"error": "Failed to parse quiz response"}

    def _format_lesson_response(self, response: str) -> Dict[str, Any]:
        """
        Format the lesson response into a structured format
        """
        # Add your formatting logic here
        return {
            "content": response,
            "sections": self._extract_lesson_sections(response)
        }

async def main():
    api_key = "YOUR_API_KEY"
    health_ed = WomensHealthEducation(api_key)
    
    # Generate a teen-focused quiz about menstrual health
    quiz = await health_ed.generate_quiz(
        topic="Understanding Your Menstrual Cycle",
        difficulty=DifficultyLevel.BEGINNER,
        age_group=AgeGroup.TEEN,
        tags=[ContentTag.MENSTRUAL_HEALTH, ContentTag.TEEN_HEALTH],
        num_questions=5
    )
    
    # Generate an interactive lesson
    lesson = await health_ed.generate_interactive_lesson(
        topic="Body Image and Self-Confidence",
        difficulty=DifficultyLevel.INTERMEDIATE,
        age_group=AgeGroup.TEEN,
        tags=[ContentTag.BODY_IMAGE, ContentTag.MENTAL_HEALTH]
    )

if __name__ == "__main__":
    asyncio.run(main())