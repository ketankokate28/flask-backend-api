# app.py (updated for CORS to allow Authorization header)
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
import auth, users, cctv, suspect, notification, permission, role
from flask_migrate import Migrate

#, face_match

# create JWTManager instance and force identity to strings
jwt = JWTManager()

@jwt.user_identity_loader
def user_identity_lookup(identity):
    # Ensure the 'sub' claim is always a string
    return str(identity)


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.config['UPLOAD_FOLDER'] = 'suspects'

    # Enable CORS for Angular UI, including Authorization header
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config['CORS_ORIGINS'],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True
            }
        }
    )

    # Initialize database and JWT
    db.init_app(app)
    jwt.init_app(app)
    migrate = Migrate(app, db)  # NEW

    # Register blueprints
    app.register_blueprint(auth.auth_bp,       url_prefix='/api/auth')
    app.register_blueprint(users.users_bp,     url_prefix='/api/users')
    app.register_blueprint(cctv.cctv_bp,       url_prefix='/api/cctv')
    app.register_blueprint(suspect.suspect_bp,       url_prefix='/api/suspect')
    app.register_blueprint(notification.notification_bp,       url_prefix='/api/notification')
    app.register_blueprint(permission.permission_bp,       url_prefix='/api/permissions')
    app.register_blueprint(role.role_bp,     url_prefix='/api/roles')
    #app.register_blueprint(face_match.face_match_bp, url_prefix='/api/face-match')

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
# Add this line outside the function
app = create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(port=3000, debug=True)
