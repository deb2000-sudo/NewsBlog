from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from .models import db
import os

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key'),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'blog_app.sqlite')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwt_dev_key'),
        JWT_ACCESS_TOKEN_EXPIRES=86400
    )
    
    if test_config:
        app.config.update(test_config)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Add JWT error handler
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"Invalid token error: {error}")
        return jsonify({
            'error': 'Invalid token',
            'message': 'The token is invalid, please log in again'
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token has expired',
            'message': 'Your session has expired, please log in again'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Authorization Required',
            'message': 'Request does not contain an access token'
        }), 401
    
    @jwt.token_in_blocklist_loader
    def token_revoked_callback(jwt_header, jwt_payload):
        # Debug logging
        print(f"Checking if token is blocklisted: {jwt_payload.get('sub', 'no-sub')}")
        return False  # No tokens are blocklisted
    
    # Register blueprints
    from .routes import auth, blogs
    app.register_blueprint(auth.bp)
    app.register_blueprint(blogs.bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
    return app 