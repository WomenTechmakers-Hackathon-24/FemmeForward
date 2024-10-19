from enums import DifficultyLevel, AgeGroup, ContentTag

class PromptGenerator:
    def __init__(self):
        self.prompt_templates = {
            (ContentTag.MENSTRUAL_HEALTH, AgeGroup.TEEN): {
                DifficultyLevel.BEGINNER: """
                Create a friendly, conversational quiz about menstrual health for teens.
                Focus on:
                - Basic understanding of the menstrual cycle
                - Common experiences and what's normal
                - Self-care and hygiene tips
                - When to talk to a trusted adult
                
                Use relatable examples and positive, normalizing language.
                Avoid medical jargon and keep explanations simple.
                """,
                DifficultyLevel.INTERMEDIATE: """
                Create an educational quiz about menstrual health for informed teens.
                Include:
                - Cycle tracking and patterns
                - Common symptoms and management
                - Emotional and physical changes
                - Healthy lifestyle habits
                
                Balance medical accuracy with accessible language.
                Include practical tips and real-life scenarios.
                """
            },
            (ContentTag.BODY_IMAGE, AgeGroup.YOUNG_ADULT): {
                DifficultyLevel.BEGINNER: """
                Create an empowering quiz about body image and self-acceptance.
                Focus on:
                - Media literacy and critical thinking
                - Diverse body representations
                - Health vs. appearance
                - Self-care practices
                
                Use inclusive language and diverse examples.
                Emphasize health and wellbeing over appearance.
                """,
                DifficultyLevel.INTERMEDIATE: """
                Create a comprehensive quiz about body image and societal influences.
                Cover:
                - Cultural beauty standards
                - Social media impact
                - Psychological aspects
                - Building resilience
                
                Include research-based information and practical coping strategies.
                """
            }
        }

    def generate_prompt(
        self,
        topic: str,
        tags: List[ContentTag],
        age_group: AgeGroup,
        difficulty: DifficultyLevel,
        content_type: str = "quiz"
    ) -> str:
        # Get specific template if available
        for tag in tags:
            template = self.prompt_templates.get((tag, age_group), {}).get(difficulty)
            if template:
                return template.strip() + f"\n\nTopic: {topic}"

        # Fall back to generic template with customization
        return self._generate_generic_prompt(topic, tags, age_group, difficulty, content_type)

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

        Topic Tags: {', '.join(tag.value for tag in tags)}

        Required Elements:
        1. Age-appropriate examples and scenarios
        2. Evidence-based information
        3. Empowering and positive messaging
        4. Practical, actionable advice
        5. Cultural sensitivity
        6. Clear explanations of medical terms
        7. Resources for additional support

        Format: {self._get_format_instructions(content_type)}
        """

    def _get_format_instructions(self, content_type: str) -> str:
        formats = {
            "quiz": """
            Format each question as:
            {
                "question": "Question text",
                "options": ["A) option", "B) option", "C) option", "D) option"],
                "correct_answer": "B",
                "explanation": "Detailed explanation",
                "learning_point": "Key takeaway"
            }
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