import os
import json
import time

from dotenv import load_dotenv

try:
    from google import genai
except ImportError as e:
    raise ImportError(
        "The google-genai package is required. Install it with `pip install google-genai`."
    ) from e

# Load environment variables
load_dotenv("api.env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in api.env")

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"


def safe_generate(prompt, retries=3):
    """
    Retry Gemini requests to handle temporary 503 errors.
    """

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            return response.text.strip()

        except Exception as e:
            print(f"Gemini Error (Attempt {attempt + 1}/{retries}):", e)

            if attempt < retries - 1:
                time.sleep(2)

    return None


def analyze_mood(text):
    """
    Returns:
    {
        "mood": "...",
        "message": "..."
    }
    """

    prompt = f"""
    Analyze the journal entry below.

    Return ONLY valid JSON.

    {{
      "mood": "Happy|Sad|Stressed|Neutral|Anxious|Excited",
      "message": "A short motivational message"
    }}

    Journal Entry:
    {text}
    """

    try:
        result = safe_generate(prompt)

        if not result:
            return {
                "mood": "Neutral",
                "message": "AI service is busy right now. Keep going and try again later."
            }

        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

        return json.loads(result)

    except Exception as e:
        print("Mood Parsing Error:", e)

        return {
            "mood": "Neutral",
            "message": "Keep moving forward one step at a time."
        }


def generate_insights(text):
    """
    Returns concise emotional insights.
    """

    prompt = f"""
    Analyze this journal entry.

    Return:

    1. Emotion Summary (1 sentence)
    2. Main Trigger (1 sentence)
    3. Advice (1 sentence)

    Maximum 100 words.

    Journal Entry:
    {text}
    """

    result = safe_generate(prompt)

    if not result:
        return (
            "The AI service is currently busy. "
            "Take a moment to reflect on what is causing stress and focus on one small next step."
        )

    return result


def generate_recommendations(mood):
    """
    Returns short personalized recommendations.
    """

    prompt = f"""
    User Mood: {mood}

    Provide:

    - 3 practical recommendations
    - concise bullet points
    - maximum 80 words
    """

    result = safe_generate(prompt)

    if not result:
        return (
            "- Take a short break\n"
            "- Focus on one task at a time\n"
            "- Reach out to someone supportive if needed"
        )

    return result


def analyze_journal_complete(text):
    """
    Complete one-shot analysis.
    """

    prompt = f"""
    Analyze the following journal entry.

    Return ONLY valid JSON.

    {{
      "mood": "",
      "message": "",
      "insights": "",
      "recommendations": ""
    }}

    Journal Entry:
    {text}
    """

    try:
        result = safe_generate(prompt)

        if not result:
            return {
                "mood": "Neutral",
                "message": "AI service is temporarily unavailable.",
                "insights": "Unable to generate insights.",
                "recommendations": "Try again later."
            }

        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

        return json.loads(result)

    except Exception as e:
        print("Complete Analysis Error:", e)

        return {
            "mood": "Neutral",
            "message": "Keep moving forward.",
            "insights": "Unable to analyze journal entry.",
            "recommendations": "Try again later."
        }