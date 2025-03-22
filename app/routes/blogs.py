from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, Blog
from ..services.crew_service import generate_blog_content

bp = Blueprint('blogs', __name__, url_prefix='/api/blogs')

@bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_blog():
    print("Generate blog endpoint called")
    # Log the authorization header to check format
    auth_header = request.headers.get('Authorization', '')
    print(f"Authorization header: {auth_header}")
    
    user_id = get_jwt_identity()
    print(f"User ID from JWT: {user_id}")
    
    # Convert user_id to integer if it's a string
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    
    user = User.query.get(user_id)
    
    if not user:
        print(f"User with ID {user_id} not found in database")
        return jsonify({"error": "User not found"}), 404
    
    if not user.api_key:
        print(f"User {user.username} has no OpenAI API key set")
        return jsonify({"error": "OpenAI API key not set"}), 400
        
    if not user.serper_api_key:
        print(f"User {user.username} has no Serper API key set")
        return jsonify({"error": "Serper API key not set"}), 400
    
    data = request.json
    if not data or not data.get('topic'):
        print(f"Invalid request data: {data}")
        return jsonify({"error": "Blog topic required"}), 400
    
    try:
        print(f"Attempting to generate blog about: {data['topic']}")
        # Generate blog using CrewAI service - pass both API keys
        blog_content = generate_blog_content(data['topic'], user.api_key, user.serper_api_key)
        
        # Ensure blog content is not empty
        if not blog_content:
            print("No blog content was generated")
            return jsonify({"error": "Failed to generate blog content"}), 500
        
        print("Blog content generated successfully, saving to database")
        # Save blog to database
        new_blog = Blog(
            topic=data['topic'],
            content=blog_content,
            user_id=user_id
        )
        db.session.add(new_blog)
        db.session.commit()
        
        print(f"New blog saved with ID: {new_blog.id}")
        return jsonify({
            "message": "Blog generated successfully",
            "blog": {
                "id": new_blog.id,
                "topic": new_blog.topic,
                "content": blog_content,
                "created_at": new_blog.created_at.isoformat() if hasattr(new_blog.created_at, 'isoformat') else str(new_blog.created_at)
            }
        }), 201
    
    except Exception as e:
        import traceback
        print(f"Error generating blog: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def get_blogs():
    user_id = get_jwt_identity()
    print(f"Getting blogs for user ID: {user_id}")
    
    # Convert user_id to integer if it's a string (from the JWT token)
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    
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
    
    # Convert user_id to integer if it's a string
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    
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