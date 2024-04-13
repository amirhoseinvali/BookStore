# #!/bin/bash
# echo "Creating Migrations..."
# python manage.py makemigrations bookstore
# echo "===================================="
# echo "Starting Migrations..."
# python manage.py migrate
# echo "===================================="
# echo "Create Preview Dir..."
# mkdir -p preview
# echo "===================================="
echo "Starting Server..."
python manage.py runserver 0.0.0.0:8000