# LearnAnything

LearnAnything is an interactive learning platform that provides personalized courses and quizzes.

## Quick Start

1. Connect your local repository to GitHub
**from local repository :**
- Go to GitHub and log in to your account.
- Create an empy repository on your GitHub account named learn-anything
- Navigate to the local repository you created (learn-anything).

```
git remote add origin https://github.com/jpbrasile/learn-anything.git
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

5. Initialize the database:
flask db init
flask db migrate
flask db upgrade

6. Populate the database with sample data:
python populate_db.py

7. Run the application:
python run.py

8. Open a web browser and go to `http://localhost:5000`

## Project Structure

- `app/`: Contains the main application code
- `__init__.py`: Initializes the Flask application
- `models.py`: Defines the database models
- `routes.py`: Contains the application routes
- `static/`: Static files (CSS, JS, images)
- `templates/`: HTML templates
- `migrations/`: Database migration files
- `tests/`: Test files
- `config.py`: Configuration settings
- `populate_db.py`: Script to populate the database with sample data
- `run.py`: Script to run the application

## Features

- User authentication
- Interactive course structure
- Quizzes with immediate feedback
- Progress tracking

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.