"""
AI Helper - Gemini API Integration
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def get_ai_response(character, chat_history, user_message, user_name='', target_language='en'):
    """
    Get AI response from Gemini 2.5 Flash
    
    Args:
        character: Character model instance
        chat_history: List of previous ChatHistory model instances
        user_message: Current user message (string)
        user_name: Display name of the logged-in user (string)
        target_language: Language code to respond in
    
    Returns:
        str: AI response text
    """
    try:
        # Use Gemini system_instruction so the character rules apply for every turn.
        system_prompt = character.get_system_prompt()
        if user_name:
            system_prompt += f"\nThe user you are chatting with is named: {user_name}."
            system_prompt += "\nIf the user refers to themself, respond using the user's name when appropriate."

        if target_language != 'en':
            system_prompt += f"\nIMPORTANT: Always respond in the language with code '{target_language}'. The user prefers this language."

        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
        
        # Build conversation history
        history = []
        for msg in chat_history[-20:]:  # Last 20 messages for context
            if msg.message_type == 'text':
                role = 'user' if msg.role == 'user' else 'model'
                history.append({
                    'role': role,
                    'parts': [msg.content]
                })
        
        # Start chat (system_instruction will already be applied)
        chat = model.start_chat(history=history)
        response = chat.send_message(user_message)
        
        return response.text
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        return f"I'm having a bit of trouble right now. Could you try again? 🙏"


def get_sticker_response(character, chat_history, sticker_filename, user_name=''):
    """
    Get AI text response when user sends a sticker
    """
    try:
        system_prompt = character.get_system_prompt()
        if user_name:
            system_prompt += f"\nThe user you are chatting with is named: {user_name}."

        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
        
        prompt = f"""
The user just sent you a sticker/emoji image called '{sticker_filename}'. 
Respond naturally to this sticker as if you can see it. Keep it short and fun (1-2 sentences max).
React to what the sticker likely depicts based on its name."""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"Gemini sticker response error: {e}")
        return "Haha, love the sticker! 😄"


def translate_text(text, target_language):
    """
    Translate text to target language using Gemini
    """
    if target_language == 'en' or not target_language:
        return text
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"Translate the following text to {target_language}. Return ONLY the translated text, nothing else:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text


def detect_language(text):
    """
    Detect the language of text using Gemini
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"Detect the language of this text and return ONLY the ISO 639-1 language code (e.g., 'en', 'es', 'fr', 'hi', etc.). Text: '{text}'"
        response = model.generate_content(prompt)
        return response.text.strip().lower()[:5]
    except Exception as e:
        print(f"Language detection error: {e}")
        return 'en'
