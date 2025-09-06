# Quiz App

A Flask-based web application for taking interactive quizzes.

## Features

- User registration and authentication
- Interactive quiz taking
- Score tracking and results
- SQLite database for data persistence
- Responsive web interface

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Installation

1. Clone or download the project to your local machine

2. Navigate to the project directory:
   ```bash
   cd alx-quiz_app
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

4. Activate the virtual environment:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

5. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

6. Set up environment variables (optional):
   ```bash
   cp .env.example .env
   # Edit .env file with your preferred settings
   ```

7. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

8. Populate the database with sample questions:
   ```bash
   python misc.py
   ```

9. Run the application:
   ```bash
   python run.py
   ```

The application will be available at `http://localhost:5000`

## Recent Fixes Applied

### Critical Issues Fixed
1. **Configuration Typo**: Fixed `SQLALCHEMY_TRACK_MODIFCATIONS` → `SQLALCHEMY_TRACK_MODIFICATIONS`
2. **Quiz Scoring Logic**: Fixed database query handling in `quiz_service.py`
3. **Missing Dependencies**: Added `flask-login` to requirements.txt
4. **User Service**: Removed unnecessary app context creation and fixed password handling
5. **CSRF Token Error**: Fixed 'csrf_token' is undefined error in timed quiz template
6. **Timezone Issues**: Implemented comprehensive timezone utilities for datetime handling

### Security Improvements
1. **Debug Mode**: Changed from hardcoded `True` to environment variable
2. **Password Handling**: Fixed double password setting in user registration

### Code Structure Improvements
1. **Import Cleanup**: Removed unused imports throughout the codebase
2. **Error Handling**: Added proper try-catch blocks and user feedback
3. **Input Validation**: Added form validation for registration and login
4. **Route Protection**: Added `@login_required` decorators where needed

### New Features Added
1. **Home Page**: Created welcoming home page with navigation
2. **Authentication Routes**: Added logout functionality
3. **Flash Messages**: Added user feedback for all operations
4. **Better Error Messages**: Improved user experience with descriptive error messages
5. **Time Limits Implementation**: Complete timed quiz functionality with countdown timers
6. **Session Management**: QuizSession model with automatic timeout handling
7. **Real-time API**: Live session monitoring with heartbeat endpoints
8. **Enhanced Templates**: Interactive timed quiz interface with auto-submit

## Usage

1. Visit the home page at `http://localhost:5000`
2. Register a new account or login with existing credentials
3. Take the quiz by answering all questions
4. View your results after completion
5. Logout when finished

## Project Structure

```
alx-quiz_app/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # URL routes and view functions
│   ├── services/        # Business logic
│   ├── templates/       # HTML templates
│   └── __init__.py      # App factory
├── migrations/          # Database migrations
├── instance/           # Instance-specific files
├── .venv/              # Virtual environment
├── requirements.txt    # Python dependencies
├── run.py             # Application entry point
└── misc.py            # Database seeding script
```

## Testing

### Route Testing

A route testing script is provided to verify all links and routes work correctly:

```bash
# Start the Flask application first
python run.py

# In another terminal, run the route tester
python test_routes.py
```

The test script will:
- Test all application routes
- Verify template links are working
- Check authentication redirects
- Test form submissions
- Provide detailed success/failure reports

### Manual Testing

You can also manually test the application flow:
1. Start at home page (`/`)
2. Navigate to register page
3. Create a new account
4. Login with the new account
5. Take the quiz
6. View results
7. Test logout functionality

## Template Links Verified

All template links have been checked and confirmed working:
- ✅ Home page navigation
- ✅ Login/Register cross-links
- ✅ Back to home links
- ✅ Quiz navigation and logout
- ✅ Results page navigation
- ✅ All url_for() references point to valid routes
- ✅ Timed quiz template with JavaScript timer
- ✅ CSRF token issues resolved

## Contributing

1. Ensure all tests pass before submitting changes
2. Follow PEP 8 style guidelines
3. Add appropriate error handling and input validation
4. Update documentation as needed
5. Run the route testing script to verify link integrity
6. Test timed quiz functionality: `python test_timed_quiz.py`

## License

This project is for educational purposes.