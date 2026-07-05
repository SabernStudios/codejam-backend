# CodeJam Backend

Backend API for the CodeJam app.

## Setup

Create a virtual environment:

py -m venv .venv

Activate it on Windows PowerShell:

.\.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Run the server:

python -m uvicorn app.main:app --reload

Open the API docs:

http://127.0.0.1:8000/docs

## Current Routes

GET /
GET /health