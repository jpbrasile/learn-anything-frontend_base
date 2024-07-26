from app import create_app, db
from app.models import User, Session, UserPreferences
from datetime import datetime
from app.course_data import astronomy_course_data

app = create_app()

def populate_database():
    with app.app_context():
        # Check if user exists
        user = User.query.filter_by(email='test@example.com').first()
        if not user:
            user = User(username='testuser', email='test@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()  # Commit to get the user ID

        # Now we're sure user exists and has an ID
        prefs = UserPreferences.query.filter_by(user_id=user.id).first()
        if not prefs:
            prefs = UserPreferences(user=user, communication_style='informal', learning_pace='moderate', learning_style='visual')
            db.session.add(prefs)


        # Create a session with astronomy course data
        session = Session.query.filter_by(user_id=user.id).first()
        if not session:
            session = Session(
                user_id=user.id,
                course_data=astronomy_course_data,
                completed=False,
                correct_answers=0,
                total_answers=0,
                start_time=datetime.utcnow()
            )
            db.session.add(session)

        # Add a completed session for demonstration
        completed_session = Session(
            user_id=user.id,
            course_data=astronomy_course_data,
            completed=True,
            correct_answers=8,
            total_answers=10,
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        db.session.add(completed_session)

        db.session.commit()

    print("Database populated successfully!")

if __name__ == '__main__':
    populate_database()







