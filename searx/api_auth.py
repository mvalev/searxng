"""
API Authentication Middleware for SearXNG
Protects the instance with API key authentication
"""

from flask import request, jsonify, abort
import os
import logging

logger = logging.getLogger('searx.api_auth')


def init_app(app):
    """Initialize API key authentication for the Flask app"""
    
    @app.before_request
    def authenticate_api():
        # Get the required API key from environment
        required_key = os.getenv('SEARXNG_API_KEY')
        
        # If no API key is set in environment, allow all requests (dev mode)
        if not required_key:
            logger.warning("SEARXNG_API_KEY not set - authentication disabled!")
            return
        
        # Block access to the root page (UI)
        if request.path == '/' or request.path == '/index.html':
            logger.info(f"Blocked UI access from {request.remote_addr}")
            abort(403, description="Web UI is disabled. API access only.")
        
        # For the search endpoint, require API key
        if request.path.startswith('/search'):
            # Check for API key in query parameter or header
            provided_key = request.args.get('api_key') or request.headers.get('X-API-Key')
            
            if not provided_key:
                logger.warning(f"Missing API key from {request.remote_addr}")
                return jsonify({
                    "error": "Missing API key",
                    "message": "Provide 'api_key' query parameter or 'X-API-Key' header"
                }), 401
            
            if provided_key != required_key:
                logger.warning(f"Invalid API key attempt from {request.remote_addr}")
                return jsonify({
                    "error": "Invalid API key",
                    "message": "The provided API key is incorrect"
                }), 401
            
            # Valid API key - allow the request
            logger.debug(f"Valid API key from {request.remote_addr}")
