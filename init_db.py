#!/usr/bin/env python3
"""
Initialization script for Tautulli History Exporter
"""

import os
import sys
from app import app, db, User
from werkzeug.security import generate_password_hash

def init_app():
    """Initialize the application database and create default user"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Create default admin user if none exists
        if not User.query.first():
            print("Creating default admin user...")
            default_user = User(
                username='admin',
                password_hash=generate_password_hash('admin'),
                must_change_password=True
            )
            db.session.add(default_user)
            db.session.commit()
            print("Default user created: admin/admin")
        else:
            print("Admin user already exists")
        
        print("Initialization complete!")

if __name__ == '__main__':
    init_app()