#!/bin/bash
# Simple start script for deployment

echo "🚀 Starting MindCare deployment..."

# Set environment variables if not set
export DEBUG=${DEBUG:-False}
export SECRET_KEY=${SECRET_KEY:-"django-insecure-e8%q@h1rxa8tp7r)m91u(7it5wwhe3(e-8uz00!*-d1st7drl%"}

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🗄️ Running database migrations..."
python manage.py migrate

echo "🌐 Starting server..."
gunicorn project.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
