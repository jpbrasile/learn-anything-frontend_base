# LearnAnything

LearnAnything is an interactive learning platform that provides personalized courses and quizzes.

## Quick Start

1. Connect your local repository to GitHub
**from local repository :**
- Go to GitHub and log in to your account.
- Create an empy repository on your GitHub account named learn-anything
- Navigate to the local repository you created (learn-anything).

```
git init
git add .
git commit -m "Initial commit"
git remote set-url origin https://github.com/jpbrasile/learn-anything.git
#ou git remote add origin https://github.com/jpbrasile/learn-anything.git si le repository vide n'a pas été créé sur GitHub
git branch -M main
git push -u origin main
``` 


**from GitHub repository :**
- Clone the repository:
- git clone https://github.com/jpbrasile/learn-anything.git
- cd learn-anything

2. Set up a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate

3. Install the required packages:
pip install -r requirements.txt

4. Set up the environment variables:
Create a `.env` file in the root directory and add the following:
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db

5. Initialize the database: (will create and populate migrations)
$env:FLASK_APP = "run.py"
flask db init
flask db migrate
flask db upgrade

6. Populate the database with sample data:
python populate_db.py

7. Run the application:
python run.py

8. Open a web browser and go to `http://localhost:5000`

## Project Structure

Project Structure:

app/

init.py: Flask app initialization, blueprint registration
models.py: Database models (User, Session, UserPreferences)
routes.py: API endpoints and view functions
static/: CSS and images
templates/: HTML templates


migrations/: Database migration files
tests/: Unit tests
config.py: Configuration classes (Config, TestConfig)
run.py: Script to run the application
requirements.txt: Project dependencies


Key Files and Their Roles:

main.py: Renamed to run.py, creates and runs the Flask app
models.py: Defines database models using SQLAlchemy
routes.py: Defines API endpoints and view functions
config.py: Contains configuration classes for different environments
init.py: Initializes Flask app, extensions, and registers blueprints
test_routes.py: Contains unit tests for routes


Authentication Implementation:

User registration and login routes in routes.py
Password hashing in User model
Flask-Login for session management


Frontend:

inscription.html: Combined registration and login page
preferences.html: User preferences page
interactive_session.html: Learning session page
Base template with Tailwind CSS for styling


Testing:

TestConfig class in config.py for test environment
test_routes.py for route testing



## Features

- User authentication
- Interactive course structure
- Quizzes with immediate feedback
- Progress tracking

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.