from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from werkzeug.security import generate_password_hash
from ..models import db, User
import secrets
import os

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    
    # Validate input
    if not data or not data.get('username') or not data.get('email') or not data.get('password') or not data.get('api_key'):
        return jsonify({"error": "Missing required fields. Username, email, password, and OpenAI API key are required."}), 400
    
    # Check if user exists
    if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Username or email already exists"}), 409
    
    # Add salt to API key for additional security
    api_key_salt = os.environ.get('API_KEY_SALT', 'default_salt_value')
    salted_api_key = data['api_key'] + api_key_salt
    
    # Create new user
    new_user = User(
        username=data['username'],
        email=data['email'],
        api_key=salted_api_key
    )
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        "message": "User created successfully"
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    print(f"Login attempt for user: {data.get('username', 'unknown')}")
    
    if not data or not data.get('username') or not data.get('password'):
        print("Missing username or password in login request")
        return jsonify({"error": "Missing username or password"}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user:
        print(f"User not found: {data.get('username')}")
        return jsonify({"error": "Invalid credentials"}), 401
        
    if not user.check_password(data['password']):
        print(f"Invalid password for user: {data.get('username')}")
        return jsonify({"error": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=user.id)
    print(f"Login successful for user: {user.username} (ID: {user.id})")
    
    return jsonify({
        "access_token": access_token,
        "user": {
            "username": user.username,
            "email": user.email,
            "api_key": user.api_key
        }
    }), 200

@bp.route('/update-api-key', methods=['PUT'])
@jwt_required()
def update_api_key():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.json
    if not data or not data.get('api_key'):
        return jsonify({"error": "API key required"}), 400
    
    # Add salt to API key for additional security
    api_key_salt = os.environ.get('API_KEY_SALT', 'default_salt_value')
    salted_api_key = data['api_key'] + api_key_salt
    
    user.api_key = salted_api_key
    db.session.commit()
    
    return jsonify({"message": "API key updated successfully"}), 200

@bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_token():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'access_token': new_access_token
    }), 200

@bp.route('/check-token', methods=['GET'])
@jwt_required()
def check_token():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify({
        "valid": True,
        "user_id": user_id,
        "username": user.username
    }), 200 