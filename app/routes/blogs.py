from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Blog
from app.services.crew_service import generate_blog_content
from app.routes.auth import cipher_suite  # Import the cipher_suite from auth.py

bp = Blueprint('blogs', __name__, url_prefix='/api/blogs')

@bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_blog():
    print("Generate blog endpoint called")
    
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))  # Convert string ID to integer
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not user.api_key:
        return jsonify({"error": "API key not set"}), 400
    
    try:
        # Decrypt the API key
        decrypted_api_key = cipher_suite.decrypt(user.api_key).decode()
        
        data = request.json
        if not data or not data.get('topic'):
            return jsonify({"error": "Blog topic required"}), 400
        
        blog_content = generate_blog_content(data['topic'], decrypted_api_key)
        
        if not blog_content:
            return jsonify({"error": "Failed to generate blog content"}), 500
        
        new_blog = Blog(
            topic=data['topic'],
            content=blog_content,
            user_id=user_id
        )
        db.session.add(new_blog)
        db.session.commit()
        
        return jsonify({
            "message": "Blog generated successfully",
            "blog": new_blog.to_dict()
        }), 201
        
    except Exception as e:
        print(f"Error generating blog: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def get_blogs():
    user_id = get_jwt_identity()
    print(f"Getting blogs for user ID: {user_id}")
    
    user = User.query.get(user_id)
    if not user:
        print(f"User with ID {user_id} not found in database")
        return jsonify({"error": "User not found"}), 404
        
    print(f"Found user: {user.username}")
    
    blogs = Blog.query.filter_by(user_id=user_id).order_by(Blog.created_at.desc()).all()
    print(f"Found {len(blogs)} blogs for user")
    
    blogs_list = [{
        "id": blog.id,
        "topic": blog.topic,
        "content": blog.content,
        "created_at": blog.created_at.isoformat() if hasattr(blog.created_at, 'isoformat') else str(blog.created_at)
    } for blog in blogs]
    
    return jsonify({"blogs": blogs_list}), 200

@bp.route('/<int:blog_id>', methods=['GET'])
@jwt_required()
def get_blog(blog_id):
    user_id = get_jwt_identity()
    
    blog = Blog.query.filter_by(id=blog_id, user_id=user_id).first()
    
    if not blog:
        return jsonify({"error": "Blog not found"}), 404
    
    return jsonify({
        "blog": {
            "id": blog.id,
            "topic": blog.topic,
            "content": blog.content,
            "created_at": blog.created_at
        }
    }), 200 