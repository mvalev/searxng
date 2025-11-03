from flask import request, jsonify, make_response
import os

def init_app(app):
    @app.before_request
    def authenticate_api():
        required_key = os.getenv('SEARXNG_API_KEY')
        if not required_key:
            return None
        
        # Block UI
        if request.path == '/' or request.path == '/index.html':
            return make_response(('Web UI disabled. API access only.', 403))
        
        # Check API key for search
        if request.path.startswith('/search'):
            provided_key = request.args.get('api_key') or request.headers.get('X-API-Key')
            
            if not provided_key or provided_key != required_key:
                return make_response((jsonify({"error": "Invalid or missing API key"}), 401))
        
        return None
