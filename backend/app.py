from flask import Flask
from api.posts import posts_bp
from api.prompts import prompts_bp  # Import the prompts blueprint
from flask_cors import CORS
from config import Config

app = Flask(__name__, static_folder='../frontend/build')
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Register blueprints
app.register_blueprint(posts_bp, url_prefix='/api/posts')  # Posts-related endpoints
app.register_blueprint(prompts_bp, url_prefix='/api/prompts')  # Prompts-related endpoints

if __name__ == '__main__':
    app.run(use_reloader=True, port=8181, threaded=True)
