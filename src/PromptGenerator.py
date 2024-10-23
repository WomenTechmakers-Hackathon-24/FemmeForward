from enum import Enum
from typing import List

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

class PromptGenerator:

    def __init__(self):
        self.safe_prefixes = {
            ContentTag.REPRODUCTIVE_HEALTH: {
                'educational': "Generate evidence-based educational content about reproductive system health, focusing on ",
                'quiz': "Create medical education questions about reproductive system wellness, specifically covering ",
                'article': "Provide scientific information about reproductive system health and wellness, explaining "
            },
            
            ContentTag.MENSTRUAL_HEALTH: {
                'educational': "Create educational content about menstrual health and cycle awareness, discussing ",
                'quiz': "Generate health education questions about menstrual wellness, covering ",
                'article': "Provide medical information about menstrual health and cycle patterns, focusing on "
            },
            
            ContentTag.MENTAL_HEALTH: {
                'educational': "Develop wellness education content about emotional and mental well-being, addressing ",
                'quiz': "Create psychological wellness questions about mental health awareness, covering ",
                'article': "Share professional mental health information and coping strategies, focusing on "
            },
            
            ContentTag.NUTRITION: {
                'educational': "Create dietary wellness content about balanced nutrition and healthy eating, explaining ",
                'quiz': "Generate nutritional education questions about healthy eating habits, covering ",
                'article': "Provide evidence-based nutrition information and dietary guidelines, focusing on "
            },
            
            ContentTag.FITNESS: {
                'educational': "Develop physical wellness content about exercise and movement, discussing ",
                'quiz': "Create fitness education questions about physical activity and exercise, covering ",
                'article': "Share professional guidance about physical fitness and exercise safety, explaining "
            },
            
            ContentTag.HORMONAL_HEALTH: {
                'educational': "Generate medical education content about endocrine system health, focusing on ",
                'quiz': "Create endocrine wellness questions about hormonal balance, covering ",
                'article': "Provide scientific information about hormonal health and balance, explaining "
            },
            
            ContentTag.SEXUAL_HEALTH: {
                'educational': "Create medical education content about reproductive wellness and health, covering ",
                'quiz': "Generate clinical questions about reproductive system health, focusing on ",
                'article': "Provide healthcare information about reproductive system wellness, discussing "
            },
            
            ContentTag.PREVENTIVE_CARE: {
                'educational': "Develop preventive healthcare content about wellness maintenance, explaining ",
                'quiz': "Create health maintenance questions about preventive care practices, covering ",
                'article': "Share professional guidance about preventive healthcare measures, focusing on "
            },
            
            ContentTag.PREGNANCY: {
                'educational': "Generate prenatal health education content about pregnancy wellness, discussing ",
                'quiz': "Create maternal health questions about pregnancy and prenatal care, covering ",
                'article': "Provide evidence-based information about pregnancy and prenatal health, focusing on "
            },
            
            ContentTag.TEEN_HEALTH: {
                'educational': "Create adolescent wellness content about youth health education, discussing ",
                'quiz': "Generate teen health education questions about adolescent wellness, covering ",
                'article': "Share age-appropriate health information for adolescent wellness, focusing on "
            },
            
            ContentTag.BODY_IMAGE: {
                'educational': "Develop positive wellness content about body acceptance and health, addressing ",
                'quiz': "Create body wellness education questions about healthy self-image, covering ",
                'article': "Share professional guidance about body acceptance and wellness, focusing on "
            },
            
            ContentTag.GENERAL_WELLNESS: {
                'educational': "Create comprehensive wellness content about overall health maintenance, discussing ",
                'quiz': "Generate general health education questions about wellness practices, covering ",
                'article': "Provide evidence-based information about overall health and wellness, focusing on "
            }
        }
        
        self.safe_suffixes = {
            'educational': """
            Ensure content:
            - Uses medical terminology
            - Maintains professional tone
            - Includes scientific context
            - Focuses on health education
            - Provides evidence-based information
            """,
            
            'quiz': """
            Format questions to be:
            - Scientifically accurate
            - Education-focused
            - Professional in language
            - Evidence-based
            - Health-oriented
            """,
            
            'article': """
            Content should be:
            - Medically accurate
            - Educational in nature
            - Professional in tone
            - Research-supported
            - Wellness-focused
            """
        }

    def generate_prompt(
        self,
        topic: str,
        tags: List[ContentTag],
        age_group: AgeGroup,
        difficulty: DifficultyLevel,
        content_type: str = "quiz"
    ) -> str:
        return self._generate_generic_prompt(topic, tags, age_group, difficulty, content_type)

    def get_safe_prompt(self, tags: List[ContentTag], content_type: str, topic: str) -> str:
        prefix = ""
        for tag in tags:
            if tag in self.safe_prefixes:
                prefix += f"\n{self.safe_prefixes[tag][content_type]}"
        suffix = self.safe_suffixes[content_type]
        
        return f"{prefix}{topic}."

    def _generate_generic_prompt(
        self,
        topic: str,
        tags: List[ContentTag],
        age_group: AgeGroup,
        difficulty: DifficultyLevel,
        content_type: str
    ) -> str:
        age_appropriate_language = {
            AgeGroup.TEEN: "Use friendly, clear language with relatable examples.",
            AgeGroup.YOUNG_ADULT: "Use straightforward language with practical examples.",
            AgeGroup.ADULT: "Use comprehensive language with detailed examples.",
            AgeGroup.MATURE: "Use respectful, thorough language with relevant examples."
        }

        difficulty_adjustments = {
            DifficultyLevel.BEGINNER: "Focus on basic concepts and everyday applications.",
            DifficultyLevel.INTERMEDIATE: "Include more detailed explanations and specific scenarios.",
            DifficultyLevel.ADVANCED: "Cover complex topics and their interconnections."
        }

        return f"""
        Create a {difficulty.value}-level {content_type} about {topic}
        for {age_group.value} age group.

        Content Guidelines:
        {age_appropriate_language.get(age_group, "Use clear, appropriate language.")}
        {difficulty_adjustments.get(difficulty, "Adjust complexity appropriately.")}
        {self.get_safe_prompt(tags, content_type, topic)}

        Topic Tags: {', '.join(tag.value for tag in tags)}

        Required Elements:
        1. Age-appropriate examples and scenarios
        2. Evidence-based information
        3. Empowering and positive messaging
        4. Practical, actionable advice
        5. Cultural sensitivity
        6. Clear explanations of medical terms
        7. Resources for additional support
        8. Educational value and scientific
        9. Focused on health and well-being
        

        Format: {self._get_format_instructions(content_type)}
        """

    def _get_format_instructions(self, content_type: str) -> str:
        formats = {
            "quiz": """
            Please format each question as a JSON object with the following structure:
            {
                "question": "Provide the question text here.",
                "options": [
                    "A) Provide the first option here.",
                    "B) Provide the second option here.",
                    "C) Provide the third option here.",
                    "D) Provide the fourth option here."
                ],
                "correct_answer": "Specify the correct answer (e.g., 'B').",
                "explanation": "Provide a detailed explanation of the correct answer.",
                "learning_point": "State the key takeaway from this question."
            }
            Ensure that the JSON structure is valid and all strings are properly quoted.
            """,
            "lesson": """
            Format the lesson with:
            1. Introduction
            2. Key concepts
            3. Examples
            4. Check-in questions
            5. Summary
            6. Action items
            7. Resources
            """
        }
        return formats.get(content_type, "Use clear, structured formatting.")