import unittest
import sys
import os
from flask import url_for
# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app, db
from app.models import User, Session, UserPreferences
from flask_login import current_user, login_user
from werkzeug.security import generate_password_hash
from config import TestConfig



class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create a test user
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()

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
        response = self.client.post('/auth/login', json={
            'email': email,
            'password': password
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        redirect_url = data['redirect']
        session_id = int(redirect_url.split('/')[-1])

        # Ensure the user is logged in by setting up the session
        with self.client.session_transaction() as sess:
            sess['_user_id'] = self.user.id
            sess['_fresh'] = True

        return session_id

    def logout(self):
        response = self.client.get('/auth/logout', follow_redirects=True)
        return response

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        response = self.register('newuser', 'new@example.com', 'password123')
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
        session_id = self.login('test@example.com', 'password123')

        # Verify user is logged in
        with self.client as c:
            with c.session_transaction() as sess:
                self.assertEqual(sess['_user_id'], self.user.id)

        response = self.logout()
        self.assertEqual(response.status_code, 200)
        
        # Verify user is logged out
        with self.client as c:
            with c.session_transaction() as sess:
                self.assertIsNone(sess.get('_user_id'))

    def test_dashboard_access(self):
        self.register('testuser', 'test@example.com', 'password123')
        session_id = self.login('test@example.com', 'password123')
        response = self.client.get(f'/interactive_session/{session_id}')
        self.assertEqual(response.status_code, 200)

    def test_preferences(self):
        self.register('testuser', 'test@example.com', 'password123')
        self.login('test@example.com', 'password123')
        response = self.client.get('/preferences')
        self.assertEqual(response.status_code, 200)

    def test_interactive_session(self):
        self.register('testuser', 'test@example.com', 'password123')
        session_id = self.login('test@example.com', 'password123')
        response = self.client.get(f'/interactive_session/{session_id}')
        self.assertEqual(response.status_code, 200)

    def test_get_session_content(self):
        self.register('testuser', 'test@example.com', 'password123')
        session_id = self.login('test@example.com', 'password123')

        # Create a test session
        user = User.query.filter_by(email='test@example.com').first()
        session = Session(user_id=user.id, course_data={"data": "test"}, correct_answers=5, incorrect_answers=2)
        db.session.add(session)
        db.session.commit()

        response = self.client.get(f'/get_session_content/{session.id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['course_data'], {"data": "test"})
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

        # Ensure the session table is empty before creating new sessions
        Session.query.delete()
        db.session.commit()

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
