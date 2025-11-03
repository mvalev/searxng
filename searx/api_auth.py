from flask import request, Response
import os

def init_app(app):
    
    # Store reference to original search route
    original_search = None
    for rule in app.url_map.iter_rules():
        if rule.endpoint == 'search':
            original_search = app.view_functions['search']
            break
    
    if not original_search:
        return  # No search route found, skip auth
    
    def authenticated_search():
        """Wrapper that checks API key before calling search"""
        required_key = os.getenv('SEARXNG_API_KEY')
        
        # If no key configured, allow all
        if not required_key:
            return original_search()
        
        # Check API key
        provided_key = request.args.get('api_key') or request.headers.get('X-API-Key')
        
        if not provided_key or provided_key != required_key:
            return Response(
                '{"error": "Invalid or missing API key"}',
                status=401,
                mimetype='application/json'
            )
        
        # Valid key - proceed with search
        return original_search()
    
    # Replace the search route
    app.view_functions['search'] = authenticated_search
    
    # Block UI homepage
    @app.before_request
    def block_ui():
        required_key = os.getenv('SEARXNG_API_KEY')
        if required_key and request.path == '/':
            return Response('API only. UI disabled.', status=403)
