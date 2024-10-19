from enum import Enum
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from datetime import datetime
import json
import asyncio
from enums import DifficultyLevel, AgeGroup, ContentTag
from PromptGenerator import PromptGenerator
from ContentValidator import ContentValidator

class GeminiAPI:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self._cache = {}
        
# Example usage
async def main():
    progress_tracker = ProgressTracker()
    content_validator = ContentValidator()
    prompt_generator = PromptGenerator()
    genai = GeminiAPI()
    
    # Track user progress
    user_id = "user123"
    progress = progress_tracker.update_progress(
        user_id=user_id,
        activity_type="quiz",
        content_id="menstrual_health_101",
        score=0.85
    )
    
    # Validate content
    content = "Sample content about menstrual health..."
    validation = await content_validator.validate_content(
        content=content,
        age_group=AgeGroup.TEEN,
        tags=[ContentTag.MENSTRUAL_HEALTH]
    )
    
    # Generate specialized prompt
    prompt = prompt_generator.generate_prompt(
        topic="Understanding Your Menstrual Cycle",
        tags=[ContentTag.MENSTRUAL_HEALTH],
        age_group=AgeGroup.TEEN,
        difficulty=DifficultyLevel.BEGINNER
    )
    
    print("Progress:", progress)
    print("Validation:", validation)
    print("Prompt:", prompt)

    

if __name__ == "__main__":
    asyncio.run(main())