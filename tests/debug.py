from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app and extensions
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(150), nullable=False)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_data = db.Column(db.JSON, nullable=False, default={})
    correct_answers = db.Column(db.Integer, default=0)
    incorrect_answers = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return jsonify({"success": True, "redirect": url_for('dashboard')})
        else:
            return jsonify({"success": False, "error": "Invalid email or password."})

    return 'Login page - Use POST to log in.'

@app.route('/dashboard')
@login_required
def dashboard():
    completed_sessions = Session.query.filter_by(user_id=current_user.id).count()
    return render_template('dashboard.html', name=current_user.username, completed_sessions=completed_sessions)

@app.route('/interactive_session/<int:session_id>')
@login_required
def interactive_session(session_id):
    session = Session.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(403)
    course_data = session.course_data
    return render_template('interactive_session.html', session_id=session_id, course_data=course_data)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Debugging Utility Functions
def create_test_user():
    user = User(username='testuser', email='test@example.com', password_hash=generate_password_hash('password123'))
    db.session.add(user)
    db.session.commit()

def create_test_session():
    user = User.query.filter_by(email='test@example.com').first()
    session = Session(user_id=user.id, course_data={"content": "This is a test course."})
    db.session.add(session)
    db.session.commit()

def init_db():
    db.drop_all()
    db.create_all()
    create_test_user()
    create_test_session()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
