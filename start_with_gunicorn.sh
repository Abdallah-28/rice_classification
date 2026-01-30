#!/bin/bash


echo "🚀 Demarrage de l'API avec Gunicorn..."

gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    api.api:app