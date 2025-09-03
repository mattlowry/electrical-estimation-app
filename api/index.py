"""
Vercel serverless function entry point for Flask app
"""
import os
import sys
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from flask import Flask, jsonify, request
from flask_cors import CORS
import json

# Create Flask app for Vercel
app = Flask(__name__)

# Configure CORS for Vercel
CORS(app, origins=['*'])  # In production, restrict this

# Basic configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'vercel-demo-key')

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'platform': 'vercel'}), 200

# Mock estimates endpoint for demo
@app.route('/api/estimates', methods=['GET', 'POST'])
def estimates():
    if request.method == 'GET':
        # Return mock estimates
        mock_estimates = [
            {
                'id': '1',
                'project_name': 'Office Building Renovation',
                'description': 'Complete electrical system upgrade',
                'total_cost': 15500.00,
                'status': 'pending',
                'created_at': '2024-01-15T10:30:00Z'
            },
            {
                'id': '2', 
                'project_name': 'Residential Wiring',
                'description': 'New home electrical installation',
                'total_cost': 8750.00,
                'status': 'completed',
                'created_at': '2024-01-10T14:20:00Z'
            }
        ]
        return jsonify(mock_estimates), 200
    
    elif request.method == 'POST':
        # Create new estimate
        data = request.get_json()
        
        # Mock response
        new_estimate = {
            'id': '3',
            'project_name': data.get('project_name', 'New Project'),
            'description': data.get('description', ''),
            'total_cost': 0.00,
            'status': 'draft',
            'created_at': '2024-01-20T09:15:00Z'
        }
        
        return jsonify(new_estimate), 201

# AI analysis endpoint (mock for demo)
@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    # Mock AI analysis response
    analysis_result = {
        'materials_detected': [
            {'name': 'Electrical Wire (14 AWG)', 'quantity': 250, 'unit': 'feet'},
            {'name': 'Outlet Box', 'quantity': 12, 'unit': 'pieces'},
            {'name': 'Circuit Breaker (20A)', 'quantity': 3, 'unit': 'pieces'}
        ],
        'estimated_cost': 450.00,
        'confidence': 0.85,
        'analysis_time': 2.3
    }
    
    return jsonify(analysis_result), 200

# Upload endpoint (mock for demo)
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Mock response
    return jsonify({
        'success': True,
        'filename': file.filename,
        'message': 'File uploaded successfully (demo mode)'
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Export for Vercel
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)