# MealMate - Online Food Delivery System

MealMate is a modern full-stack web application for ordering food, browsing restaurants, and managing orders.

## Tech Stack
- **Frontend**: React, Vite, React-Bootstrap, Axios
- **Backend**: Python, Django, Django REST Framework, SimpleJWT
- **Database**: SQLite (Development) / MySQL (Production)

## Setup Instructions

### 1. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Activate the virtual environment (Windows):
   ```bash
   .\venv\Scripts\activate
   ```
3. Run the migrations:
   ```bash
   python manage.py migrate
   ```
4. Start the Django development server:
   ```bash
   python manage.py runserver
   ```
The backend API will be running on `http://localhost:8000/api/`.

### 2. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies (if not already done):
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```

## Production Deployment
- **Frontend (Vercel)**: Connect your GitHub repository to Vercel and set the build command to `npm run build` and output directory to `dist`.
- **Backend (Render)**: Connect your repository to Render, use a Python environment, run `pip install -r requirements.txt`, and use `gunicorn mealmate.wsgi` as the start command. Make sure to configure environment variables for the database URL and `SECRET_KEY`.

## Features
- JWT Authentication
- Responsive UI with Dark Mode
- Cart & Order Management
- Admin Analytics Dashboard
- Dynamic SEO Tags
