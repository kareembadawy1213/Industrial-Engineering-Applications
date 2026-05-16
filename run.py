"""
IE Platform - Industrial Engineering Web Application
Entry point: run this file to start the development server.
"""
import os
from app import create_app
from app.extensions import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✓ Database tables created.")
    print("Starting IE Platform on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
