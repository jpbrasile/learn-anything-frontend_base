
from app.course_data import astronomy_course_data


from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Session, UserPreferences
from app.extensions import db
from flask import render_template, jsonify
from datetime import datetime
bp = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
import traceback
import json
@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
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
    else:
        return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            
            new_session = Session(user_id=user.id, course_data={})
            db.session.add(new_session)
            db.session.commit()
            
            interactive_session_url = url_for('main.interactive_session', session_id=new_session.id)
            return jsonify({"success": True, "redirect": interactive_session_url})
        else:
            return jsonify({"success": False, "error": "Invalid email or password."})
    else:
        return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# @bp.route('/dashboard')
# @login_required
# def dashboard():
#     # Calculez ces valeurs en fonction de vos données réelles
#     completed_sessions = Session.query.filter_by(user_id=current_user.id, completed=True).count()
#     total_sessions = Session.query.filter_by(user_id=current_user.id).count()
    
#     # Assurez-vous que total_sessions n'est pas zéro pour éviter une division par zéro
#     completion_percentage = (completed_sessions / total_sessions) * 100 if total_sessions > 0 else 0
    
#     return render_template('dashboard.html', 
#                            name=current_user.username,
#                            completed_sessions=completed_sessions,
#                            total_sessions=total_sessions,
#                            completion_percentage=completion_percentage)





@bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch completed and total sessions
    completed_sessions = Session.query.filter_by(user_id=current_user.id, completed=True).count()
    total_sessions = Session.query.filter_by(user_id=current_user.id).count()
    
    # Calculate completion percentage
    completion_percentage = (completed_sessions / total_sessions) * 100 if total_sessions > 0 else 0
    
    # Fetch active (incomplete) sessions
    active_sessions = Session.query.filter_by(user_id=current_user.id, completed=False).all()
    
    # Calculate total correct and total answers across all sessions
    sessions = Session.query.filter_by(user_id=current_user.id).all()
    total_correct_answers = sum(session.correct_answers for session in sessions)
    total_answers = sum(session.total_answers for session in sessions)
    
    # Fetch recent activities (using the last 5 sessions as activities)
    recent_activities = Session.query.filter_by(user_id=current_user.id).order_by(Session.start_time.desc()).limit(5).all()

    return render_template('dashboard.html', 
                           name=current_user.username,
                           completed_sessions=completed_sessions,
                           total_sessions=total_sessions,
                           completion_percentage=completion_percentage,
                           active_sessions=active_sessions,
                           correct_answers=total_correct_answers,
                           total_answers=total_answers,
                           recent_activities=recent_activities)

@bp.route('/api/progress')
@login_required
def get_progress():
    sessions = Session.query.filter_by(user_id=current_user.id).all()
    correct_answers = sum(session.correct_answers for session in sessions)
    total_answers = sum(session.total_answers for session in sessions)
    return jsonify({
        'correct_answers': correct_answers,
        'total_answers': total_answers
    })


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






@bp.route('/get_session_content/<int:session_id>')
@login_required
def get_session_content(session_id):
    session = Session.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(403)
    return jsonify({
        'course_data': session.course_data,
        'correct_answers': session.correct_answers,
        'incorrect_answers': session.incorrect_answers ,
        'user_progress': session.user_progress
    })
from flask import render_template, jsonify, request, redirect, url_for

# app/routes.py


@bp.route('/start_new_session', methods=['GET', 'POST'])
@login_required
def start_new_session():
    # Find an incomplete session for the current user
    session = Session.query.filter_by(user_id=current_user.id, completed=False).first()
    
    if not session:
        # If no incomplete session exists, create a new one
        session = Session(
            user_id=current_user.id,
            course_data=astronomy_course_data,
            completed=False,
            correct_answers=0,
            total_answers=0,
            start_time=datetime.utcnow()
        )
        db.session.add(session)
        db.session.commit()
    
    print(f"Session found/created with id: {session.id}")  # Debugging line
    return redirect(url_for('main.interactive_session', session_id=session.id))

@bp.route('/interactive_session/<int:session_id>')
@login_required
def interactive_session(session_id):
    try:
        session = Session.query.get_or_404(session_id)
        if session.user_id != current_user.id:
            abort(403)
        
        # Debug print statements
        print("Debug: Session retrieved from database")
        print(f"Debug: Session ID: {session.id}")
        print(f"Debug: User ID: {session.user_id}")
        
        # Check if course_data exists and print it
        if session.course_data:
            print("Debug: Course data exists in the session")
            print(f"Debug: Course data: {json.dumps(session.course_data, indent=2)}")
        else:
            print("Debug: No course data in the session")
        
        print(f"Debug: Correct Answers: {session.correct_answers}")
        print(f"Debug: Total Answers: {session.total_answers}")
        
        # Pass debug information to the template
        debug_info = {
            'session_id': session.id,
            'user_id': session.user_id,
            'has_course_data': bool(session.course_data),
            'correct_answers': session.correct_answers,
            'total_answers': session.total_answers
        }
        
        return render_template('interactive_session.html', 
                               session=session,
                               course_data=session.course_data,
                               correct_answers=session.correct_answers,
                               total_answers=session.total_answers,
                               debug_info=debug_info)
    except Exception as e:
        # Print the error
        print(f"Error in interactive_session: {str(e)}")
        
        # Return an error response
        return jsonify({"error": "An error occurred processing your request"}), 500
# ... (other routes remain the same)
@bp.route('/debug_database')
def debug_database():
    users = User.query.all()
    user_data = []
    for user in users:
        user_info = {
            'id': user.id,
            'username': user.username,
            'sessions': []
        }
        sessions = Session.query.filter_by(user_id=user.id).all()
        for session in sessions:
            session_info = {
                'id': session.id,
                'course_data': session.course_data,
                'correct_answers': session.correct_answers,
                'total_answers': session.total_answers,
                'completed': session.completed,
                'start_time': str(session.start_time),
                'end_time': str(session.end_time) if session.end_time else None
            }
            user_info['sessions'].append(session_info)
        user_data.append(user_info)
    return jsonify(users=user_data)




@bp.route('/debug_session/<int:session_id>')
def debug_session(session_id):
    session = Session.query.get_or_404(session_id)
    session_data = {
        'id': session.id,
        'user_id': session.user_id,
        'course_data': session.course_data,
        'correct_answers': session.correct_answers,
        'total_answers': session.total_answers,
        'completed': session.completed,
        'start_time': session.start_time,
        'end_time': session.end_time
    }
    return jsonify(session_data)

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


@bp.route('/get_user_sessions')
@login_required
def get_user_sessions():
    sessions = Session.query.filter_by(user_id=current_user.id).all()
    return jsonify([{"id": s.id, "start_time": s.start_time} for s in sessions])

main = bp
