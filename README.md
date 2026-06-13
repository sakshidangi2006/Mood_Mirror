# 🪞 Mood Mirror

> An AI-powered mood tracking and reflection web app built with Flask.

---

## About

**Mood Mirror** is a web application that helps users track, understand, and reflect on their emotional well-being over time. Powered by AI, it analyzes mood entries and offers personalized insights — acting as a mirror for your inner emotional state.

---

## Features

- 📝 **Log your moods** — Record how you're feeling with journal-style entries
- 🤖 **AI-powered analysis** — Get intelligent feedback and reflections on your mood patterns
- 📊 **Mood history** — View and track your emotional trends over time
- 🗄️ **Persistent storage** — SQLite database to store all your entries securely
- 🎨 **Clean UI** — Intuitive interface built with Flask templates

---

## Tech Stack

| Layer      | Technology        |
|------------|-------------------|
| Backend    | Python, Flask     |
| AI         | Anthropic / OpenAI API (`ai.py`) |
| Database   | SQLite (`db.py`, `models.py`) |
| Frontend   | HTML, CSS, JS (`templates/`, `static/`) |

---

## Project Structure

```
Mood_Mirror/
├── app.py               # Main Flask application & routes
├── ai.py                # AI integration for mood analysis
├── models.py            # Database models
├── db.py                # Database connection setup
├── create_db.py         # Script to initialize the database
├── create_tables.py     # Script to create database tables
├── migrate_db.py        # Database migration utility
├── message_column.py    # Helper for message/column operations
├── static/              # CSS, JS, and static assets
├── templates/           # HTML Jinja2 templates
└── .gitignore
```

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sakshidangi2006/Mood_Mirror.git
   cd Mood_Mirror
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**
   ```bash
   python create_db.py
   python create_tables.py
   ```

4. **Configure environment variables**

   Create a `.env` file in the root directory:
   ```
   SECRET_KEY=your_secret_key
   AI_API_KEY=your_api_key_here
   ```

5. **Run the app**
   ```bash
   python app.py
   ```

6. Open your browser and visit `http://127.0.0.1:5000`

---

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to open a pull request or issue.

---

## Author

**Sakshi Dangi** — [@sakshidangi2006](https://github.com/sakshidangi2006)

---

## License

This project is open source and available under the [MIT License](LICENSE).
