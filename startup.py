#!/usr/bin/env python3
"""
Production startup script with validation and monitoring
"""

import os
import sys
import logging
from app import app, db, User
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/startup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def validate_environment():
    """Validate critical environment variables"""
    critical_vars = {
        'SECRET_KEY': 'Flask secret key for session security',
        'DATABASE_URL': 'Database connection string',
    }
    
    missing_vars = []
    weak_vars = []
    
    for var, description in critical_vars.items():
        value = os.environ.get(var)
        
        if not value:
            missing_vars.append(f"{var}: {description}")
        elif var == 'SECRET_KEY':
            # Check for weak secret keys
            weak_secrets = [
                'dev-secret-key',
                'your-secret-key-change-in-production',
                'please-change-this-in-production'
            ]
            if value in weak_secrets or len(value) < 32:
                weak_vars.append(f"{var}: Using weak or default secret key")
    
    if missing_vars:
        logger.error("Missing critical environment variables:")
        for var in missing_vars:
            logger.error(f"  - {var}")
        return False
    
    if weak_vars:
        logger.warning("Weak security configuration detected:")
        for var in weak_vars:
            logger.warning(f"  - {var}")
        
        # In production, fail if weak secrets are detected
        if os.environ.get('FLASK_ENV') == 'production':
            logger.error("Weak security configuration not allowed in production")
            return False
    
    # Check database password strength
    db_url = os.environ.get('DATABASE_URL', '')
    if 'password@' in db_url or 'changeme' in db_url:
        logger.warning("Database appears to use weak password")
        if os.environ.get('FLASK_ENV') == 'production':
            logger.error("Weak database password not allowed in production")
            return False
    
    logger.info("Environment validation passed")
    return True

def init_database():
    """Initialize database with proper error handling"""
    try:
        with app.app_context():
            logger.info(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
            logger.info("Creating database tables...")
            db.create_all()
            
            # Create default admin user if none exists
            if not User.query.first():
                logger.info("Creating default admin user...")
                default_user = User(
                    username='admin',
                    password_hash=generate_password_hash('admin'),
                    must_change_password=True
                )
                db.session.add(default_user)
                db.session.commit()
                logger.info("Default admin user created (admin/admin)")
                logger.warning("SECURITY: Please change the default password immediately!")
            else:
                admin_user = User.query.filter_by(username='admin').first()
                if admin_user:
                    logger.info(f"Admin user exists, must_change_password: {admin_user.must_change_password}")
                else:
                    logger.info("Users exist but no admin user found")
            
            logger.info("Database initialization complete")
            return True
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def check_security_config():
    """Check security configuration"""
    security_checks = []
    
    # Check if running in debug mode
    if app.debug:
        security_checks.append("CRITICAL: Debug mode is enabled")
    
    # Check session configuration
    if not app.config.get('SESSION_COOKIE_SECURE') and os.environ.get('FLASK_ENV') == 'production':
        security_checks.append("WARNING: SESSION_COOKIE_SECURE should be True in production")
    
    # Check secret key strength
    secret_key = app.config.get('SECRET_KEY', '')
    if len(secret_key) < 32:
        security_checks.append("WARNING: SECRET_KEY should be at least 32 characters")
    
    if security_checks:
        logger.warning("Security configuration issues:")
        for check in security_checks:
            logger.warning(f"  - {check}")
        
        # Fail on critical issues in production
        critical_issues = [check for check in security_checks if check.startswith("CRITICAL")]
        if critical_issues and os.environ.get('FLASK_ENV') == 'production':
            return False
    
    logger.info("Security configuration validated")
    return True

def ensure_directories():
    """Ensure required directories exist"""
    directories = ['/app/data', '/app/logs']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, mode=0o755)
            logger.info(f"Created directory: {directory}")
    
    return True

def main():
    """Main startup function"""
    logger.info("Starting Tautulli History Exporter...")
    
    # Validate environment
    if not validate_environment():
        logger.error("Environment validation failed - aborting startup")
        sys.exit(1)
    
    # Ensure directories exist
    if not ensure_directories():
        logger.error("Directory creation failed - aborting startup")
        sys.exit(1)
    
    # Check security configuration
    if not check_security_config():
        logger.error("Security validation failed - aborting startup")
        sys.exit(1)
    
    # Initialize database
    if not init_database():
        logger.error("Database initialization failed - aborting startup")
        sys.exit(1)
    
    logger.info("Startup validation complete - application ready")
    return True

if __name__ == '__main__':
    main()