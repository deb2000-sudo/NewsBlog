from app import create_app
from dotenv import load_dotenv
import os

load_dotenv()

# Create the application instance
app = create_app()

if __name__ == "__main__":
    # Use environment variable for port, defaulting to 5000
    port = int(os.environ.get("PORT", 5000))
    # In production, listen on all interfaces
    host = '0.0.0.0' if os.environ.get('FLASK_ENV') == 'production' else '127.0.0.1'
    app.run(host=host, port=port, debug=os.environ.get('FLASK_ENV') != 'production') 