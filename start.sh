#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Run Flask shell commands to create all tables (initial migration)
python -c "from app import app, db; with app.app_context(): db.create_all()"

# Start the Gunicorn WSGI server
gunicorn app:app
