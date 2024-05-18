# Use the official Python image from the Docker Hub with Python 3.10
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Copy the db.json file to the working directory
COPY db.json db.json

# Copy the .env file to the working directory
COPY .env .env

# Apply database migrations
RUN python manage.py migrate

# Load initial data from the dump
RUN python manage.py loaddata db.json

# Expose port 8000 to the outside world
EXPOSE 8000

# Command to run the application and create superuser
CMD ["sh", "-c", " python manage.py create_superuser & sleep 5 &&  python manage.py runserver 0.0.0.0:8000"]
