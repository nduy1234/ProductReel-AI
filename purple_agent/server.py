"""Simple HTTP server for Purple Agent A2A endpoint.

This provides a minimal A2A-compatible endpoint for the purple agent.
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

from .purple_agent import PurpleAgent, A2ATask


class A2ARequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for A2A protocol."""
    
    def __init__(self, *args, agent: PurpleAgent, **kwargs):
        self.agent = agent
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests (A2A task submissions)."""
        if self.path == '/a2a/task':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                task_data = json.loads(post_data.decode('utf-8'))
                task = A2ATask.from_dict(task_data)
                response = self.agent.process_task(task)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response.to_dict()).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {'error': str(e)}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        """Handle GET requests (health check)."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            health = {'status': 'healthy', 'agent': 'purple'}
            self.wfile.write(json.dumps(health).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Override to use Python logging."""
        logging.info(f"{self.address_string()} - {format % args}")


def create_handler_class(agent: PurpleAgent):
    """Create a request handler class with agent bound."""
    def handler(*args, **kwargs):
        return A2ARequestHandler(*args, agent=agent, **kwargs)
    return handler


def run_server(port: int = 8000, use_green_agent: bool = True):
    """Run the purple agent server.
    
    Args:
        port: Port to listen on
        use_green_agent: Whether to delegate to Green Agent
    """
    agent = PurpleAgent(use_green_agent=use_green_agent)
    handler_class = create_handler_class(agent)
    
    server = HTTPServer(('0.0.0.0', port), handler_class)
    logging.info(f"Purple Agent server running on http://0.0.0.0:{port}")
    logging.info(f"A2A endpoint: http://0.0.0.0:{port}/a2a/task")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down server")
        server.shutdown()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_server(port=8000)
