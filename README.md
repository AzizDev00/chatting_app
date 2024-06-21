# Chatting App

This is a simple real-time chatting application built with Django and Django Channels. It allows users to create groups, add members, and communicate in real-time.

## Features

- Real-time messaging with Django Channels
- Create and manage chat groups
- Add and manage group members
- User authentication
- User-friendly interface

## Requirements

- Python 3.x
- Django
- Django Channels
- Channels Redis
- Redis

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AzizDev00/chatting_app.git
   cd chatting_app


2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt

5. **Apply the migrations:**
   ```bash
   python manage.py migrate

## Running the Application

1. **Run the Django development server:**
   ```bash
   python manage.py runserver


## Usage

**Open your web browser and go to http://127.0.0.1:8000.**
**Register a new account or log in with an existing account.**
**Create a new group and add members.**
**Start chatting in real-time with other members in the group.**
