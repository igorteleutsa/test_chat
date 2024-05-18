# Simple Chat Application

## Requirements

- Python 3.10
- Django
- Django REST Framework
- Simple JWT
- SQLite
- python-dotenv
# optional
- Docker

## Setup

### Using Docker

1. Create a `.env` file based on the `.env.template` file and fill in the required values:
    ```sh
    cp .env.template .env
    ```

2. Build the Docker image:
    ```sh
    docker build -t simple-chat-app .
    ```

3. Run the Docker container:
    ```sh
    docker run -p 8000:8000 simple-chat-app
    ```

### Without Docker

1. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

2. Apply migrations:
    ```sh
    python manage.py migrate
    ```

3. Load initial data from the dump:
    ```sh
    python manage.py loaddata db.json
    ```

4. Create a superuser:
    ```sh
    python manage.py create_superuser
    ```

5. Run the server:
    ```sh
    python manage.py runserver
    ```

## API Endpoints

- `POST /api/threads/` - Get all threads for the user given as param/or for authorized user if no param is given
- `DELETE /api/threads/{id}/` - Remove a thread
- `GET /api/threads/` - List threads for the authenticated user
- `POST /api/messages/` - Create a new message
- `GET /api/messages/` - List messages in a thread
- `POST /api/messages/{id}/mark_as_read/` - Mark a message as read
- `GET /api/messages/unread_count/` - Get unread messages count for the authenticated user(and not sent by him)
- `POST /api/users/` - Register a new user
- `GET /api/users/` - List all users
## Authentication

Use JWT for authentication. Obtain a token via:
```sh
curl -X POST -d "username=user1&password=password" http://127.0.0.1:8000/api/token/
