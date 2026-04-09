"""
AI Helper - Groq API Integration
"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Configure Groq
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def _chat_completion(messages, temperature=0.7, max_tokens=512):
    """Wrapper for Groq chat completions with safe fallbacks."""
    if not client:
        raise RuntimeError("Missing GROQ_API_KEY in environment.")

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return (response.choices[0].message.content or "").strip()

def get_ai_response(character, chat_history, user_message, user_name='', target_language='en'):
    """
    Get AI response from Groq chat model
    
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
        system_prompt = character.get_system_prompt()
        if user_name:
            system_prompt += f"\nThe user you are chatting with is named: {user_name}."
            system_prompt += "\nIf the user refers to themself, respond using the user's name when appropriate."

        if target_language != 'en':
            system_prompt += f"\nIMPORTANT: Always respond in the language with code '{target_language}'. The user prefers this language."

        # Build messages list for Groq Chat Completions API
        messages = [{"role": "system", "content": system_prompt}]
        for msg in chat_history[-20:]:  # Last 20 messages for context
            if msg.message_type == 'text':
                role = 'user' if msg.role == 'user' else 'assistant'
                messages.append({"role": role, "content": msg.content})

        messages.append({"role": "user", "content": user_message})
        return _chat_completion(messages, temperature=0.7, max_tokens=700)
        
    except Exception as e:
        print(f"Groq API error: {e}")
        return f"I'm having a bit of trouble right now. Could you try again? 🙏"


def get_sticker_response(character, chat_history, sticker_filename, user_name=''):
    """
    Get AI text response when user sends a sticker
    """
    try:
        system_prompt = character.get_system_prompt()
        if user_name:
            system_prompt += f"\nThe user you are chatting with is named: {user_name}."
        sticker_prompt = (
            f"The user just sent you a sticker/emoji image called '{sticker_filename}'. "
            "Respond naturally to this sticker as if you can see it. "
            "Keep it short and fun (1-2 sentences max). "
            "React to what the sticker likely depicts based on its name."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": sticker_prompt}
        ]
        return _chat_completion(messages, temperature=0.8, max_tokens=120)
        
    except Exception as e:
        print(f"Groq sticker response error: {e}")
        return "Haha, love the sticker! 😄"


def translate_text(text, target_language):
    """
    Translate text to target language using Groq
    """
    if target_language == 'en' or not target_language:
        return text
    
    try:
        prompt = f"Translate the following text to {target_language}. Return ONLY the translated text, nothing else:\n\n{text}"
        messages = [
            {"role": "system", "content": "You are a precise translation assistant."},
            {"role": "user", "content": prompt}
        ]
        return _chat_completion(messages, temperature=0.2, max_tokens=400)
    except Exception as e:
        print(f"Translation error: {e}")
        return text


def detect_language(text):
    """
    Detect the language of text using Groq
    """
    try:
        prompt = f"Detect the language of this text and return ONLY the ISO 639-1 language code (e.g., 'en', 'es', 'fr', 'hi', etc.). Text: '{text}'"
        messages = [
            {"role": "system", "content": "Return only ISO 639-1 language code."},
            {"role": "user", "content": prompt}
        ]
        return _chat_completion(messages, temperature=0.0, max_tokens=10).lower()[:5]
    except Exception as e:
        print(f"Language detection error: {e}")
        return 'en'
