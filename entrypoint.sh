#!/bin/bash

# Exit immediately if any command fails
set -e

# Check if FLASK_ENV is set to development
if [ "$FLASK_ENV" = "development" ]; then
    echo "Running in development mode"
    # Run Flask development server
    flask run --host=0.0.0.0 --port=5000
else
    echo "Running in production mode"
    # Run Gunicorn
    gunicorn --bind 0.0.0.0:5000 "app:create_app()"
fi

