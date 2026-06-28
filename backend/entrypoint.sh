#!/bin/bash

# Run migrations
python manage.py migrate --noinput

# Seed demo data (only if no users exist)
USER_COUNT=$(python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.count())")

if [ "$USER_COUNT" -eq "0" ]; then
    echo "No users found. Seeding demo data..."
    python manage.py seed_demo_data
else
    echo "Users already exist. Skipping seed."
fi

# Start the server
exec gunicorn school_monitoring_system.wsgi:application
