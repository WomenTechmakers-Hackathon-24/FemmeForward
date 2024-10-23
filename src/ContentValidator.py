from enums import AgeGroup, ContentTag
from typing import List
from dataclasses import dataclass

@dataclass
class ContentValidation:
    age_appropriate: bool
    scientific_accuracy: float
    sensitivity_score: float
    empowerment_score: float
    trigger_warnings: List[str]
    citations_needed: List[str]
    readability_score: float
    message: str

class ContentValidator:
    def __init__(self):
        self.age_appropriate_keywords = {
            AgeGroup.TEEN: {
                'allowed': {'puberty', 'menstruation', 'hygiene', 'self-esteem'},
                'restricted': {'fertility', 'intimate', 'conception'},
                'forbidden': {'explicit', 'graphic', 'intimate relationships'}
            },
            AgeGroup.YOUNG_ADULT: {
                'allowed': {'fertility', 'pregnancy', 'contraception'},
                'restricted': {'complications', 'disorders'},
                'forbidden': {'graphic content', 'explicit details'}
            }
        }

        self.sensitivity_topics = {
            'body_image': ['weight', 'appearance', 'size'],
            'mental_health': ['depression', 'anxiety', 'disorder'],
            'medical_conditions': ['disease', 'syndrome', 'condition']
        }

    async def validate_content(
        self,
        content: str,
        age_group: AgeGroup,
        tags: List[ContentTag]
    ) -> ContentValidation:
        # Check age-appropriateness
        age_appropriate = self._check_age_appropriate(content, age_group)
        
        # Calculate various scores
        sensitivity_score = self._calculate_sensitivity_score(content, tags)
        empowerment_score = self._calculate_empowerment_score(content)
        readability_score = self._calculate_readability_score(content, age_group)
        
        # Identify potential trigger warnings
        trigger_warnings = self._identify_trigger_warnings(content)
        
        # Check for scientific accuracy markers
        scientific_accuracy = self._check_scientific_accuracy(content)
        
        # Identify statements needing citations
        citations_needed = self._identify_citations_needed(content)
        
        return ContentValidation(
            age_appropriate=age_appropriate,
            scientific_accuracy=scientific_accuracy,
            sensitivity_score=sensitivity_score,
            empowerment_score=empowerment_score,
            trigger_warnings=trigger_warnings,
            citations_needed=citations_needed,
            readability_score=readability_score,
            message=self._generate_validation_message(age_appropriate, sensitivity_score, 
                                                   empowerment_score, readability_score)
        )

    def _check_age_appropriate(self, content: str, age_group: AgeGroup) -> bool:
        content_lower = content.lower()
        keywords = self.age_appropriate_keywords.get(age_group, {})
        
        # Check for forbidden keywords
        for forbidden in keywords.get('forbidden', []):
            if forbidden.lower() in content_lower:
                return False
                
        # Check for restricted keywords context
        restricted_count = sum(1 for word in keywords.get('restricted', [])
                             if word.lower() in content_lower)
        
        return restricted_count <= 2

    def _calculate_readability_score(self, content: str, age_group: AgeGroup) -> float:
        # Simplified Flesch-Kincaid Grade Level calculation
        words = content.split()
        sentences = content.split('.')
        syllables = sum(self._count_syllables(word) for word in words)
        
        if not sentences or not words:
            return 0.0
            
        score = 0.39 * (len(words) / len(sentences)) + 11.8 * (syllables / len(words)) - 15.59
        
        # Adjust score based on age group
        target_scores = {
            AgeGroup.TEEN: (6.0, 8.0),
            AgeGroup.YOUNG_ADULT: (8.0, 10.0),
            AgeGroup.ADULT: (10.0, 12.0),
            AgeGroup.MATURE: (10.0, 14.0)
        }
        
        target_range = target_scores.get(age_group, (8.0, 12.0))
        if target_range[0] <= score <= target_range[1]:
            return 1.0
        return max(0.0, 1.0 - abs(score - sum(target_range) / 2) / 5.0)

    def _count_syllables(self, word: str) -> int:
        # Simplified syllable counting
        count = 0
        vowels = 'aeiouy'
        word = word.lower()
        if word.endswith('e'):
            word = word[:-1]
        previous_was_vowel = False
        for letter in word:
            is_vowel = letter in vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel
        return max(count, 1)

    def _generate_validation_message(self, age_appropriate: bool, 
                                  sensitivity_score: float,
                                  empowerment_score: float,
                                  readability_score: float) -> str:
        messages = []
        if not age_appropriate:
            messages.append("Content may not be age-appropriate")
        if sensitivity_score < 0.7:
            messages.append("Content may need more sensitive handling")
        if empowerment_score < 0.7:
            messages.append("Content could be more empowering")
        if readability_score < 0.7:
            messages.append("Readability may need adjustment")
        
        return "; ".join(messages) if messages else "Content meets all validation criteria"