from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)


    # Set up login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

    # Import and register blueprints
    from app.routes import main as main_bp, auth as auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')



    # Import models to ensure they are known to Flask-Migrate
    from app import models

    # # User loader function for Flask-Login
    # @login_manager.user_loader
    # def load_user(user_id):
    #     return models.User.query.get(int(user_id))

    # # Create database tables
    with app.app_context():
        db.create_all()

    return app

