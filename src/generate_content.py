import google.generativeai as genai 
from google.generativeai.types import SafetySettingDict

# Configure the Gemini API
genai.configure(api_key='YOUR_API_KEY')

# Set up the model
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    SafetySettingDict(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_MEDIUM_AND_ABOVE"),
    SafetySettingDict(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
    SafetySettingDict(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
]

model = genai.GenerativeModel('gemini-pro', 
                              generation_config=generation_config,
                              safety_settings=safety_settings)

def generate_quiz_question(topic, difficulty):
    prompt = f"Generate a multiple-choice question about {topic} for a {difficulty} difficulty level. Provide the question, four answer options, and indicate the correct answer."
    
    response = model.generate_content(prompt)
    
    if response.candidates:
        return response.text
    else:
        return "Unable to generate question. Please try again."

# Example usage
topic = "Human reproductive system"
difficulty = "intermediate"
question = generate_quiz_question(topic, difficulty)
print(question)