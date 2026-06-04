import os

from dotenv import load_dotenv
from flask import Blueprint, jsonify, render_template, request

try:
    from google import genai
except ImportError as e:
    raise ImportError(
        "The google-genai package is required. Install it with `pip install google-genai`."
    ) from e

load_dotenv("api.env")

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in api.env")

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash"

coach_bp = Blueprint("coach", __name__)

ARIA_SYSTEM_PROMPT = """You are ARIA, an empathetic AI Wellness Coach inside a mental health journaling app called Mood Mirror.
You have access to the user's emotional journal history and mood patterns.
Be warm, supportive, and insightful. Keep responses concise (2-4 sentences).
Never give medical advice. If someone seems in crisis, gently suggest professional help."""

ARIA_INTRO = "Hello. I'm ARIA — your AI Wellness Coach. I've been observing your emotional patterns. What's on your mind today?"

QUICK_PROMPTS = [
    "How am I doing emotionally?",
    "Help me manage stress",
    "I need motivation",
    "What patterns do you see in me?",
]


@coach_bp.route("/coach")
def coach():
    """Render the ARIA Coach chat page."""
    return render_template("coach.html", intro=ARIA_INTRO, quick_prompts=QUICK_PROMPTS)


@coach_bp.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    """
    Accepts JSON: { "message": str, "history": [{"role": "user"|"model", "content": str}] }
    Returns JSON: { "reply": str }
    """
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    try:
        # Build conversation history
        chat_history = []
        for entry in history:
            role = entry.get("role", "user")  # "user" or "model"
            content = entry.get("content", "")
            if role in ("user", "model") and content:
                chat_history.append({"role": role, "parts": [content]})

        # Use the global client to send message
        chat = client.start_chat(
            history=chat_history,
            system_instruction=ARIA_SYSTEM_PROMPT
        )
        response = chat.send_message(user_message)
        reply = response.text.strip() if response and response.text else "I'm having trouble responding. Please try again."

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"[ARIA] Gemini error: {e}")
        return jsonify({"reply": "ARIA is temporarily unavailable. Please try again shortly."}), 500
