# School Management System API

A FastAPI-based backend for managing school data such as users, students, teachers, classrooms, attendance, fees, and results.

## Features

- User authentication
- Student management
- Teacher management
- Classroom management
- Attendance tracking
- Fees management
- Results management
- SQLite database using SQLAlchemy

## Project Structure

```text
school-management/
├── app/
│   ├── auth/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── database.py
│   ├── main.py
│   └── security.py
├── requirements.txt
├── school.db
└── README.md
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
ALGORITHM=HS256
DATABASE_URL=sqlite:///./school.db
```

## Run the App

```bash
uvicorn app.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

## API Docs

FastAPI automatically provides API documentation:

```text
http://127.0.0.1:8000/docs
```

Alternative docs:

```text
http://127.0.0.1:8000/redoc
```

## Notes

- The virtual environment folder `venv/` is ignored by Git.
- `.env` is ignored by Git because it can contain secrets.
- Python cache files and local database files are ignored by Git.
