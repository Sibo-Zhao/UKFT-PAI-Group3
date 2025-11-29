# University Wellbeing API - Flask Backend

A **Flask** backend application built using **Test-Driven Development (TDD)** to serve university student wellbeing survey data with MySQL database.

## 🎯 Project Overview

This API provides endpoints to access and analyze weekly survey data from university students, including:
- Stress levels (1-5 scale)
- Sleep hours
- Social connection scores (1-5 scale)
- Student comments and feedback

## 🧪 Test-Driven Development Approach

This project follows TDD principles:

1. **RED** 🔴 - Write tests first (they will fail)
2. **GREEN** 🟢 - Write minimal code to make tests pass
3. **REFACTOR** 🔵 - Improve code while keeping tests green

## 📁 Project Structure

```
uni-wellbeing-api/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration settings
│   ├── models.py            # Flask-SQLAlchemy models
│   ├── schemas.py           # Marshmallow schemas
│   └── routes/
│       ├── __init__.py
│       └── surveys.py       # Survey endpoints
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   └── test_surveys.py      # Survey endpoint tests
├── requirements.txt         # Python dependencies
├── pytest.ini              # Pytest configuration
├── run.py                  # Application entry point
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- MySQL server running locally
- Database `uni_wellbeing_db` created with schema from `uni_wellbeing.sql`

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd c:\Users\sanat\Documents\PAI\uni-wellbeing-api
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```bash
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables:**
   ```bash
   # Copy the example file
   copy .env.example .env
   
   # Edit .env and update database credentials
   # DATABASE_URL=mysql+pymysql://username:password@localhost:3306/uni_wellbeing_db
   ```

## 🧪 Running Tests (TDD Workflow)

### Run all tests:
```bash
pytest -v
```

### Run tests with coverage:
```bash
pytest --cov=app --cov-report=term-missing
```

### Run specific test file:
```bash
pytest tests/test_surveys.py -v
```

### Expected output:
All tests should pass ✅ if the Flask application is correctly implemented.

## 🏃 Running the API

### Method 1: Using run.py
```bash
python run.py
```

### Method 2: Using Flask CLI
```bash
# Set Flask app
set FLASK_APP=app
set FLASK_ENV=development

# Run the server
flask run
```

The API will be available at: `http://localhost:5000`

## 📡 API Endpoints

### Health Check
```bash
GET /
GET /health
```

**Response:**
```json
{
  "message": "University Wellbeing API",
  "status": "running",
  "version": "1.0.0",
  "framework": "Flask"
}
```

### Get All Weekly Surveys
```bash
GET /api/surveys
```

**Example using curl:**
```bash
curl http://localhost:5000/api/surveys
```

**Response Example:**
```json
[
  {
    "survey_id": 1,
    "registration_id": 1,
    "week_number": 1,
    "submitted_at": "2025-01-15T10:30:00",
    "stress_level": 2,
    "sleep_hours": 7.5,
    "social_connection_score": 4,
    "comments": "Feeling motivated, enjoying the module."
  }
]
```

## 🧪 TDD Development Workflow

When adding new features:

1. **Write the test first** (in `tests/`)
   ```python
   def test_new_feature(client):
       response = client.get("/api/new-endpoint")
       assert response.status_code == 200
   ```

2. **Run the test** (it should fail - RED 🔴)
   ```bash
   pytest tests/test_new_feature.py -v
   ```

3. **Implement the feature** (in `app/`)
   ```python
   @bp.route("/new-endpoint")
   def new_endpoint():
       return jsonify({"message": "success"})
   ```

4. **Run the test again** (it should pass - GREEN 🟢)
   ```bash
   pytest tests/test_new_feature.py -v
   ```

5. **Refactor if needed** (REFACTOR 🔵)
   - Improve code quality
   - Keep tests passing

## 🗄️ Database Schema

The API connects to a MySQL database with the following key tables:
- `courses` - Course information
- `modules` - Module details
- `students` - Student records
- `module_registrations` - Student-module enrollments
- `weekly_surveys` - Weekly wellbeing survey responses

## 🔧 Technology Stack

- **Flask** - Lightweight web framework
- **Flask-SQLAlchemy** - SQLAlchemy integration for Flask
- **Flask-Marshmallow** - Object serialization/deserialization
- **PyMySQL** - MySQL database driver
- **Pytest** - Testing framework
- **pytest-flask** - Flask testing utilities

## 📝 Environment Variables

Create a `.env` file with:

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/uni_wellbeing_db
SECRET_KEY=your-secret-key-here
```

## 🤝 Contributing

When contributing, always follow TDD:
1. Write tests first
2. Implement features
3. Ensure all tests pass
4. Maintain high test coverage (>80%)

## 📄 License

This project is for educational purposes.
