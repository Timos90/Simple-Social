# Simple Social

Simple Social is a full-stack web application that allows users to register, log in, and share posts with images and captions. It features a modern Python backend built with FastAPI and a simple, reactive frontend built with Streamlit.

## Features

- **User Authentication**: Secure user registration and login using JWT tokens, powered by `fastapi-users`.
- **Image Uploads**: Seamless image uploads and transformations handled by ImageKit.io.
- **Dynamic Feed**: A live feed of posts from all users.
- **Post Management**: Users can create and delete their own posts.
- **Asynchronous Backend**: Built with `asyncio`, `SQLAlchemy 2.0` and `aiosqlite` for high performance.

## Tech Stack

- **Backend**: FastAPI, Uvicorn, SQLAlchemy, Pydantic
- **Frontend**: Streamlit
- **Database**: SQLite (via `aiosqlite`)
- **Authentication**: `fastapi-users`
- **Image Service**: ImageKit.io
- **Package Management**: `uv`

---

## Setup and Installation

Follow these steps to set up and run the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/Timos90/Simple-Social.git
cd Simple-Social
```

### 2. Create and Activate Virtual Environment

This project uses `uv` for package management.

```bash
# Create a virtual environment
python -m venv .venv

# Activate the environment
source .venv/bin/activate
```

### 3. Install Dependencies

This project uses `uv` to manage dependencies defined in `pyproject.toml`. Use `uv sync` to install them.

```bash
uv sync
```

### 4. Configure Environment Variables

Create a `.env` file in the project root and add your credentials. This file is ignored by Git for security.

```shell
# .env

# Your ImageKit.io credentials
IMAGEKIT_PUBLIC_KEY="your_public_key_here"
IMAGEKIT_PRIVATE_KEY="your_private_key_here"
IMAGEKIT_URL="your_url_endpoint_here"

# Your secret key for JWT
JWT_SECRET="a_strong_and_random_secret_key"
```

---

## How to Run the Application

This project consists of two separate services that must be run simultaneously in two different terminals.

### Terminal 1: Start the FastAPI Backend

Make sure your virtual environment is activated, then run:

```bash
uv run main.py
```

Your backend API will be running at `http://localhost:8000`.

### Terminal 2: Start the Streamlit Frontend

In a new terminal, activate the virtual environment again, then run:

```bash
streamlit run frontend.py
```

Your frontend application will open in your browser, usually at `http://localhost:8501`.

Now you can register, log in and start sharing posts!