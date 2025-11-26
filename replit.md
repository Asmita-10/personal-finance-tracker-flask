# Expense Tracker - Flask Web Application

## Overview
A Flask web application for tracking personal expenses with user authentication and PostgreSQL database integration.

## Project Structure
```
├── app.py              # Flask app configuration and database setup
├── main.py             # Application entry point
├── models.py           # SQLAlchemy models (User, Expense)
├── forms.py            # WTForms for authentication and expenses
├── routes.py           # All application routes
├── templates/          # Jinja2 HTML templates
│   ├── base.html       # Base template with navigation
│   ├── index.html      # Landing page
│   ├── login.html      # Login form
│   ├── register.html   # Registration form
│   ├── dashboard.html  # User dashboard with stats
│   ├── expenses.html   # Expense list view
│   └── expense_form.html # Add/Edit expense form
├── static/             # Static assets (CSS, JS, images)
└── design_guidelines.md # Frontend design specifications
```

## Key Features
- **User Authentication**: Registration and login with Flask-Login
- **Expense Tracking**: CRUD operations for expenses
- **Dashboard**: Overview of spending with category breakdowns
- **Responsive Design**: Mobile-friendly with Tailwind CSS

## Database Models

### User
- id (Integer, Primary Key)
- username (String, Unique)
- email (String, Unique)
- password_hash (String)

### Expense
- id (Integer, Primary Key)
- amount (Float)
- category (String)
- date (Date)
- description (String, Optional)
- user_id (Foreign Key -> User)

## Technology Stack
- **Backend**: Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database**: PostgreSQL
- **Frontend**: Tailwind CSS, Jinja2 Templates
- **Server**: Gunicorn

## Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Flask session secret key

## Running the Application
The app runs on port 5000 using Gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## Recent Changes
- November 26, 2025: Initial project setup with user authentication and expense tracking
