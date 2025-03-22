from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from .models import db
import os
from config import config as app_config

def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Add CORS support
    CORS(app)
    
    # Determine configuration to use
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    # Load the configuration
    app.config.from_object(app_config[config_name])
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
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
        
    @app.route('/')
    def index():
        return jsonify({"message": "Blog Generator API is running"}), 200
        
    return app 