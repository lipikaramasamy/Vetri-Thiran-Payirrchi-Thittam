# FitBuddy

FitBuddy is an AI-powered fitness plan generator built using:

- Python
- FastAPI
- Jinja2
- SQLite
- SQLAlchemy
- Google Gemini
- HTML
- CSS

## Features

1. User profile input
2. AI-generated 7-day workout plan
3. AI-generated nutrition/recovery tip
4. Feedback-based workout plan regeneration
5. SQLite database
6. Admin user dashboard
7. REST API
8. Swagger API documentation

---

# Project Structure

```text
FitBuddy/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── schemas.py
│   ├── routes.py
│   │
│   └── ai/
│       ├── __init__.py
│       ├── gemini_client.py
│       ├── gemini_generator.py
│       ├── gemini_flash_generator.py
│       └── updated_plan.py
│
├── templates/
│   ├── index.html
│   ├── result.html
│   └── all_users.html
│
├── static/
│   └── style.css
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md