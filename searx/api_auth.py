from flask import request, jsonify, abort
import os
from timeit import default_timer

def init_app(app):
    @app.before_request
    def authenticate_api():
        # Initialize start_time for all requests to avoid AttributeError
        if not hasattr(request, 'start_time'):
            request.start_time = default_timer()
        
        required_key = os.getenv('SEARXNG_API_KEY')
        if not required_key:
            return
        
        if request.path == '/' or request.path == '/index.html':
            abort(403)
        
        if request.path.startswith('/search'):
            provided_key = request.args.get('api_key') or request.headers.get('X-API-Key')
            
            if not provided_key or provided_key != required_key:
                return jsonify({"error": "Invalid or missing API key"}), 401
