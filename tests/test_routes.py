import unittest
from app import create_app, db
from app.models import User, Session, UserPreferences
from flask_login import current_user
from werkzeug.security import generate_password_hash

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app('config.TestConfig')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register(self, username, email, password):
        return self.client.post('/auth/register', json={
            'username': username,
            'email': email,
            'password': password
        })

    def login(self, email, password):
        return self.client.post('/auth/login', json={
            'email': email,
            'password': password
        })

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        response = self.register('testuser', 'test@example.com', 'password123')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])

    def test_register_duplicate_username(self):
        self.register('testuser', 'test@example.com', 'password123')
        response = self.register('testuser', 'test2@example.com', 'password123')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json['success'])
        self.assertIn('nom d\'utilisateur existe déjà', response.json['error'])

    def test_register_duplicate_email(self):
        self.register('testuser', 'test@example.com', 'password123')
        response = self.register('testuser2', 'test@example.com', 'password123')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json['success'])
        self.assertIn('adresse email est déjà utilisée', response.json['error'])

    def test_login_logout(self):
        self.register('testuser', 'test@example.com', 'password123')
        response = self.login('test@example.com', 'password123')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])

        with self.client:
            self.client.get('/')
            self.assertTrue(current_user.is_authenticated)

        response = self.logout()
        self.assertEqual(response.status_code, 200)

        with self.client:
            self.client.get('/')
            self.assertFalse(current_user.is_authenticated)

    def test_login_invalid_credentials(self):
        response = self.login('test@example.com', 'wrongpassword')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json['success'])

    def test_dashboard_access(self):
        self.register('testuser', 'test@example.com', 'password123')
        self.login('test@example.com', 'password123')
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_no_login(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirect to login page

    def test_preferences(self):
        self.register('testuser', 'test@example.com', 'password123')
        self.login('test@example.com', 'password123')
        
        # Test GET
        response = self.client.get('/preferences')
        self.assertEqual(response.status_code, 200)

        # Test POST
        preferences_data = {
            'communicationStyle': 'formal',
            'learningPace': 'moderate',
            'learningStyle': 'visual',
            'customPreferences': 'Test custom preferences'
        }
        response = self.client.post('/preferences', json=preferences_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])

        # Verify preferences were saved
        user = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(user.preferences)
        self.assertEqual(user.preferences.communication_style, 'formal')
        self.assertEqual(user.preferences.learning_pace, 'moderate')
        self.assertEqual(user.preferences.learning_style, 'visual')
        self.assertEqual(user.preferences.custom_preferences, 'Test custom preferences')

    def test_interactive_session(self):
        self.register('testuser', 'test@example.com', 'password123')
        self.login('test@example.com', 'password123')

        # Create a test session
        user = User.query.filter_by(email='test@example.com').first()
        session = Session(user_id=user.id, course_data={'test': 'data'})
        db.session.add(session)
        db.session.commit()

        response = self.client.get(f'/interactive_session/{session.id}')
        self.assertEqual(response.status_code, 200)

    def test_get_session_content(self):
        self.register('testuser', 'test@example.com', 'password123')
        self.login('test@example.com', 'password123')

        # Create a test session
        user = User.query.filter_by(email='test@example.com').first()
        session = Session(user_id=user.id, course_data={'test': 'data'}, correct_answers=5, incorrect_answers=2)
        db.session.add(session)
        db.session.commit()

        response = self.client.get(f'/get_session_content/{session.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['course_data'], {'test': 'data'})
        self.assertEqual(data['correct_answers'], 5)
        self.assertEqual(data['incorrect_answers'], 2)

    def test_update_score(self):
        self.register('testuser', 'test@example.com', 'password123')
        self.login('test@example.com', 'password123')

        # Create a test session
        user = User.query.filter_by(email='test@example.com').first()
        session = Session(user_id=user.id)
        db.session.add(session)
        db.session.commit()

        response = self.client.post(f'/update_score/{session.id}', json={'correct': 3, 'incorrect': 1})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])

        # Verify score was updated
        updated_session = Session.query.get(session.id)
        self.assertEqual(updated_session.correct_answers, 3)
        self.assertEqual(updated_session.incorrect_answers, 1)

    def test_start_new_session(self):
        self.register('testuser', 'test@example.com', 'password123')
        self.login('test@example.com', 'password123')

        response = self.client.post('/start_new_session')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
        self.assertIsNotNone(response.json['session_id'])

    def test_get_user_sessions(self):
        self.register('testuser', 'test@example.com', 'password123')
        self.login('test@example.com', 'password123')

        # Create some test sessions
        user = User.query.filter_by(email='test@example.com').first()
        for _ in range(3):
            session = Session(user_id=user.id)
            db.session.add(session)
        db.session.commit()

        response = self.client.get('/get_user_sessions')
        self.assertEqual(response.status_code, 200)
        sessions = response.json
        self.assertEqual(len(sessions), 3)
        for session in sessions:
            self.assertIn('id', session)
            self.assertIn('start_time', session)

if __name__ == '__main__':
    unittest.main()