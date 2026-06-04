from flask import (
    Flask,
    request,
    redirect,
    render_template,
    session,
    url_for,
    jsonify
)

from db import Base, engine, SessionLocal
from models import User, JournalEntry
from ai import (
    analyze_mood,
    generate_insights,
    generate_recommendations
)

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # ⚠️ Replace with a secure random key

Base.metadata.create_all(bind=engine)


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        with SessionLocal() as db:
            user = db.query(User).filter_by(email=email).first()

        if user and user.password == password:
            session["user_id"] = user.id
            session["user_email"] = user.email
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        with SessionLocal() as db:
            existing = db.query(User).filter_by(email=email).first()
            if existing:
                return render_template("signup.html", error="User already exists")

            user = User(
                email=email,
                password=password
            )
            db.add(user)
            db.commit()

        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    message = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if email:
            message = "If that email exists in our system, password reset instructions have been sent."
    return render_template("forget_password.html", message=message)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    latest_mood = latest_message = latest_insights = latest_recommendations = None

    with SessionLocal() as db:
        if request.method == "POST":
            text = request.form.get("entry", "").strip()
            if text:
                mood_result = analyze_mood(text)
                latest_mood = mood_result.get("mood", "Neutral")
                latest_message = mood_result.get("message", "Keep moving forward one step at a time.")
                latest_insights = generate_insights(text)
                latest_recommendations = generate_recommendations(latest_mood)

                entry = JournalEntry(
                    user_id=session["user_id"],
                    text=text,
                    mood=latest_mood,
                    message=latest_message,
                    insights=latest_insights,
                    recommendations=latest_recommendations
                )
                db.add(entry)
                db.commit()

        # Fetch all user entries for calculation & timeline stream
        entries = db.query(JournalEntry).filter_by(user_id=session["user_id"]).all()

        # Calculate live analytics metrics for the integrated scoreboard with case-insensitivity checks
        happy = sad = stressed = neutral = 0
        for entry in entries:
            mood = entry.mood.lower() if entry.mood else "neutral"
            
            if "happy" in mood or "excited" in mood:
                happy += 1
            elif "sad" in mood:
                sad += 1
            elif "stress" in mood or "anxious" in mood:
                stressed += 1
            else:
                neutral += 1

        total = len(entries)
        wellbeing_score = 0 if total == 0 else round(
            ((happy * 100) + (neutral * 70) + (stressed * 40) + (sad * 20)) / total
        )

    return render_template(
        "dashboard.html",
        user=session.get("user_email", ""),
        entries=entries,
        latest_mood=latest_mood,
        latest_message=latest_message,
        latest_insights=latest_insights,
        latest_recommendations=latest_recommendations,
        wellbeing_score=wellbeing_score,
        total=total,
        happy=happy,
        neutral=neutral,
        stressed=stressed,
        sad=sad
    )


@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    with SessionLocal() as db:
        entries = db.query(JournalEntry).filter_by(user_id=session["user_id"]).all()

    return render_template("history.html", entries=entries)


@app.route("/delete_entry/<int:entry_id>", methods=["POST"])
def delete_entry(entry_id):
    """Delete a single journal entry."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    with SessionLocal() as db:
        entry = db.query(JournalEntry).filter_by(id=entry_id, user_id=session["user_id"]).first()
        if entry:
            db.delete(entry)
            db.commit()

    return redirect(url_for("history"))


@app.route("/delete_history", methods=["POST"])
def delete_history():
    """Delete all journal entries for the logged-in user."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    with SessionLocal() as db:
        db.query(JournalEntry).filter_by(user_id=session["user_id"]).delete()
        db.commit()

    return redirect(url_for("history"))


@app.route("/score")
def score():
    if "user_id" not in session:
        return redirect(url_for("login"))

    with SessionLocal() as db:
        entries = db.query(JournalEntry).filter_by(user_id=session["user_id"]).all()

    happy = sad = stressed = neutral = 0
    for entry in entries:
        mood = entry.mood.lower() if entry.mood else "neutral"
        if "happy" in mood:
            happy += 1
        elif "sad" in mood:
            sad += 1
        elif "stress" in mood or "anxious" in mood:
            stressed += 1
        else:
            neutral += 1

    total = len(entries)
    wellbeing_score = 0 if total == 0 else round(
        ((happy * 100) + (neutral * 70) + (stressed * 40) + (sad * 20)) / total
    )

    return render_template(
        "score.html",
        total=total,
        happy=happy,
        sad=sad,
        stressed=stressed,
        neutral=neutral,
        wellbeing_score=wellbeing_score
    )


@app.route("/mood_compare")
def mood_compare():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        limit = max(2, min(20, int(request.args.get("limit", 5))))
    except (ValueError, TypeError):
        limit = 5

    with SessionLocal() as db:
        recent_entries = (
            db.query(JournalEntry)
            .filter_by(user_id=session["user_id"])
            .order_by(JournalEntry.id.desc())
            .limit(limit)
            .all()
        )

    if not recent_entries:
        return jsonify({
            "current_mood": None,
            "previous_moods": [],
            "trend": "insufficient_data",
            "mood_history": [],
            "ai_suggestions": "Start journalling to unlock mood trend insights!",
            "comparison_summary": "No entries yet — write your first journal entry to get started."
        })

    mood_history = [
        {"mood": e.mood, "entry_id": e.id}
        for e in recent_entries
    ]

    current_mood = mood_history[0]["mood"]
    previous_moods = [item["mood"] for item in mood_history[1:]]

    MOOD_SCORE = {
        "happy": 5,
        "excited": 5,
        "calm": 4,
        "neutral": 3,
        "sad": 2,
        "anxious": 2,
        "stressed": 1,
        "angry": 1,
    }

    def score_mood(mood_label: str) -> int:
        label = mood_label.lower() if mood_label else "neutral"
        for key, val in MOOD_SCORE.items():
            if key in label:
                return val
        return 3 

    current_score = score_mood(current_mood)

    if previous_moods:
        avg_previous = sum(score_mood(m) for m in previous_moods) / len(previous_moods)
        delta = current_score - avg_previous
        if delta >= 1:
            trend = "improving"
        elif delta <= -1:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    TREND_SUMMARY = {
        "improving": f"Your mood has improved — you were mostly {', '.join(set(previous_moods)) or 'neutral'} before and are now feeling {current_mood}. Keep it up!",
        "declining": f"Your mood has dipped — you were feeling {', '.join(set(previous_moods)) or 'neutral'} before but are now {current_mood}. Let's work on this.",
        "stable":    f"Your mood has been consistently {current_mood} across your recent entries.",
        "insufficient_data": "Only one entry so far — add more to see your trend.",
    }
    comparison_summary = TREND_SUMMARY.get(trend, "")

    trend_context_mood = f"{current_mood} (trend: {trend})"
    ai_suggestions = generate_recommendations(trend_context_mood)

    return jsonify({
        "current_mood": current_mood,
        "previous_moods": previous_moods,
        "trend": trend,
        "mood_history": mood_history,
        "ai_suggestions": ai_suggestions,
        "comparison_summary": comparison_summary,
    })


@app.route("/coach/proactive")
def coach_proactive():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    mood = request.args.get("mood", "Neutral").strip()
    if not mood:
        mood = "Neutral"

    MOOD_SCORE = {
        "happy": 5, "excited": 5, "calm": 4, "neutral": 3,
        "sad": 2, "anxious": 2, "stressed": 1, "angry": 1,
    }

    def score_mood(label: str) -> int:
        label = label.lower() if label else "neutral"
        for key, val in MOOD_SCORE.items():
            if key in label:
                return val
        return 3

    with SessionLocal() as db:
        recent = (
            db.query(JournalEntry)
            .filter_by(user_id=session["user_id"])
            .order_by(JournalEntry.id.desc())
            .limit(5)
            .all()
        )

    trend = "insufficient_data"
    if len(recent) >= 2:
        previous_scores = [score_mood(e.mood) for e in recent[1:]]
        avg_prev = sum(previous_scores) / len(previous_scores)
        delta = score_mood(mood) - avg_prev
        if delta >= 1:
            trend = "improving"
        elif delta <= -1:
            trend = "declining"
        else:
            trend = "stable"

    coach_prompt = (
        f"current mood: {mood}, trend: {trend}. "
        "Give a single warm, empathetic 2-3 sentence opening message as a "
        "personal wellness coach — no bullet points, no headers, just speak "
        "directly to the user and end with one gentle actionable suggestion."
    )
    coach_message = generate_recommendations(coach_prompt)

    return jsonify({
        "coach_message": coach_message,
        "mood": mood,
        "trend": trend,
    })


@app.route("/coach/message", methods=["POST"])
def coach_message():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    body = request.get_json(silent=True) or {}
    user_message = (body.get("message") or "").strip()
    history = body.get("history") or []

    if not user_message:
        return jsonify({"error": "message is required"}), 400

    with SessionLocal() as db:
        recent = (
            db.query(JournalEntry)
            .filter_by(user_id=session["user_id"])
            .order_by(JournalEntry.id.desc())
            .limit(3)
            .all()
        )

    current_mood = recent[0].mood if recent else "Unknown"
    mood_summary = ", ".join(e.mood for e in recent) if recent else "no entries yet"

    MAX_HISTORY_TURNS = 6
    trimmed_history = history[-MAX_HISTORY_TURNS:] if len(history) > MAX_HISTORY_TURNS else history
    history_text = ""
    for turn in trimmed_history:
        role = "User" if turn.get("role") == "user" else "Coach"
        history_text += f"{role}: {turn.get('text', '')}\n"

    full_prompt = (
        f"[Coach context: the user's recent moods are — {mood_summary}. "
        f"Current mood: {current_mood}. "
        "You are a warm, professional wellness coach. "
        "Keep replies concise (2-4 sentences), empathetic, and actionable. "
        "Never use bullet points. Speak directly to the user.]\n\n"
        f"{history_text}"
        f"User: {user_message}\n"
        "Coach:"
    )

    reply = generate_recommendations(full_prompt)

    return jsonify({
        "reply": reply,
        "current_mood": current_mood,
    })


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)