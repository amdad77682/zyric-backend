# Zyric Backend API

FastAPI backend with Supabase integration for user authentication and management.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

3. Run migrations on your Supabase database:
   - Go to your Supabase project dashboard
   - Navigate to SQL Editor
   - Run the SQL scripts in `migrations/` folder in order

4. Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## API Endpoints

- `POST /api/v1/register` - Register a new user
- `POST /api/v1/login` - Login user
- `POST /api/v1/forgot-password` - Request password reset

## Project Structure

```
zyric-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   └── utils/
├── migrations/
├── requirements.txt
└── .env
```
