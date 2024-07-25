from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Session, UserPreferences
from app import db

bp = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@auth.route('/register', methods=['POST'])
def register():
    data = request.json
    user = User.query.filter((User.username == data['username']) | (User.email == data['email'])).first()
    if user:
        if user.username == data['username']:
            return jsonify({"success": False, "error": "Ce nom d'utilisateur existe déjà."})
        else:
            return jsonify({"success": False, "error": "Cette adresse email est déjà utilisée."})
    new_user = User(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"success": True})

@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Email ou mot de passe incorrect."})

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    if request.method == 'POST':
        data = request.json
        prefs = UserPreferences.query.filter_by(user_id=current_user.id).first()
        if not prefs:
            prefs = UserPreferences(user_id=current_user.id)
        prefs.communication_style = data['communicationStyle']
        prefs.learning_pace = data['learningPace']
        prefs.learning_style = data['learningStyle']
        prefs.custom_preferences = data['customPreferences']
        db.session.add(prefs)
        db.session.commit()
        return jsonify({"success": True})
    prefs = UserPreferences.query.filter_by(user_id=current_user.id).first()
    return render_template('preferences.html', preferences=prefs)

@bp.route('/interactive_session/<int:session_id>')
@login_required
def interactive_session(session_id):
    session = Session.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(403)
    return render_template('interactive_session.html', session_id=session_id)

@bp.route('/get_session_content/<int:session_id>')
@login_required
def get_session_content(session_id):
    session = Session.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(403)
    return jsonify({
        'course_data': session.course_data,
        'correct_answers': session.correct_answers,
        'incorrect_answers': session.incorrect_answers
    })

@bp.route('/update_score/<int:session_id>', methods=['POST'])
@login_required
def update_score(session_id):
    session = Session.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(403)
    
    data = request.json
    session.correct_answers = data.get('correct', 0)
    session.incorrect_answers = data.get('incorrect', 0)
    db.session.commit()
    
    return jsonify({"success": True})

@bp.route('/update_user_progress/<int:session_id>', methods=['POST'])
@login_required
def update_user_progress(session_id):
    session = Session.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(403)
    progress_data = request.json
    if session.user_progress:
        session.user_progress.update(progress_data)
    else:
        session.user_progress = progress_data
    db.session.commit()
    return jsonify({"success": True})

@bp.route('/start_new_session', methods=['POST'])
@login_required
def start_new_session():
    new_session = Session(user_id=current_user.id, course_data={})  # Initialize with empty course data
    db.session.add(new_session)
    db.session.commit()
    return jsonify({"success": True, "session_id": new_session.id})

@bp.route('/get_user_sessions')
@login_required
def get_user_sessions():
    sessions = Session.query.filter_by(user_id=current_user.id).all()
    return jsonify([{"id": s.id, "start_time": s.start_time} for s in sessions])