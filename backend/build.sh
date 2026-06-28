#!/bin/bash

# Run migrations
python manage.py migrate

# Seed demo data
python manage.py seed_demo_data
