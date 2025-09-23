# 📚 Tautulli History Exporter - Technical Documentation

## 🏗️ Architecture Overview

This application is built with a modern Flask stack designed for production deployment and security:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend        │    │   External      │
│   (Templates)   │◄──►│   (Flask App)    │◄──►│   (Tautulli)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
│                       │                       │
├─ Bootstrap 5.3.2      ├─ Flask 2.3.3         └─ REST API
├─ Dark/Light Theme     ├─ SQLAlchemy          
├─ Responsive Design    ├─ PostgreSQL/SQLite   
└─ JavaScript (ES6)     ├─ Redis (Sessions)    
                        ├─ Rate Limiting       
                        ├─ CSRF Protection     
                        └─ Security Headers    
```

## 🗄️ Database Schema

### User Model
```python
class User(db.Model):
    id: int                      # Primary key
    username: str                # Unique username
    password_hash: str           # Bcrypt hashed password
    role: str                    # 'admin' or 'user'
    is_active: bool              # Account active status
    must_change_password: bool   # Force password change
    allowed_tautulli_users: str  # JSON array of allowed usernames
    created_at: datetime         # Account creation timestamp
    updated_at: datetime         # Last modification timestamp
```

### Configuration Model
```python
class Configuration(db.Model):
    id: int                     # Primary key
    tautulli_url: str          # Tautulli server URL
    api_key: str               # Tautulli API key
    created_at: datetime       # Configuration creation
    updated_at: datetime       # Last modification
```

## 🔐 Security Features

### Authentication & Authorization
- **Session-based authentication** with secure cookie settings
- **Role-based access control** (Admin/User roles)
- **Password hashing** using Werkzeug's secure methods
- **Forced password changes** on first login
- **Multi-user system** with permission isolation

### Security Headers & Protection
- **CSRF Protection** via Flask-WTF
- **Rate Limiting** via Flask-Limiter (300 requests/hour)
- **Security Headers** via Flask-Talisman
- **Content Security Policy** (CSP)
- **HTTP Strict Transport Security** (HSTS)
- **X-Content-Type-Options** and **X-Frame-Options**

### Data Protection
- **Environment-based secrets** (SECRET_KEY, database passwords)
- **Input validation** and sanitization
- **SQL injection protection** via SQLAlchemy ORM
- **XSS protection** via template escaping

## 🛠️ Core Functions

### Authentication Functions

#### `is_logged_in() -> bool`
Checks if a user is currently authenticated by verifying session data.

#### `require_admin(f) -> function`
Decorator that restricts route access to admin users only. Redirects non-admins to dashboard.

#### `get_current_user() -> User | None`
Retrieves the currently logged-in user object from the database.

### Tautulli Integration Functions

#### `test_tautulli_connection(url: str, api_key: str) -> tuple[bool, str]`
Tests connectivity to Tautulli API and validates credentials.

#### `get_tautulli_users(url: str, api_key: str) -> list`
Fetches all Plex users from Tautulli for filtering and permission assignment.

#### `get_user_history(url: str, api_key: str, user_id: str, **filters) -> dict`
Retrieves watch history with support for date, media type, and completion filtering.

### User Management Functions

#### `user_management() -> Response`
Admin-only route that displays the user management interface.

#### `add_user() -> Response`
Creates new users with role assignment and Tautulli user permissions.

#### `edit_user() -> Response`
Modifies existing users while enforcing business rules (e.g., last admin protection).

#### `delete_user() -> Response`
Removes users with safeguards to prevent deleting the last admin.

## 📊 Data Flow

### Export Process
1. **User selects filters** (date range, users, media type)
2. **Frontend validates inputs** and sends AJAX request
3. **Backend authenticates** and checks permissions
4. **Tautulli API called** with user's allowed filters
5. **Data processed** and formatted for CSV
6. **Response streamed** to client as downloadable file

### Permission Filtering
```python
# Admin users see all Tautulli users
if current_user.is_admin():
    return all_tautulli_users

# Regular users only see their assigned users
else:
    allowed = current_user.get_allowed_users()
    return [user for user in all_users if user.name in allowed]
```

## 🎨 Frontend Architecture

### Template Structure
```
templates/
├── base.html           # Base template with navigation and common elements
├── dashboard.html      # Main interface with filters and export controls
├── login.html          # Authentication form
├── change_password.html # Password change interface
├── configuration.html  # Admin-only Tautulli configuration
├── user_management.html # Admin-only user CRUD operations
└── error.html          # Error page template
```

### JavaScript Components
- **Theme Toggle**: Persistent dark/light mode with localStorage
- **Data Filtering**: Real-time filter application with AJAX
- **User Management**: Modal-based CRUD operations with form validation
- **Toast Notifications**: User feedback for actions and errors

### CSS Architecture
- **CSS Custom Properties**: Theme variables for easy customization
- **Bootstrap 5.3.2**: Component framework with custom overrides
- **Responsive Design**: Mobile-first approach with flexbox/grid
- **Accessibility**: ARIA labels, keyboard navigation, color contrast

## 🐳 Deployment Architecture

### Docker Services
```yaml
services:
  web:           # Flask application server
  db:            # PostgreSQL database
  redis:         # Session storage and caching
```

### Environment Configuration
```bash
# Security
SECRET_KEY=<64-char-hex>              # Flask session encryption
POSTGRES_PASSWORD=<20-char-random>     # Database password

# Database
DATABASE_URL=postgresql://...          # PostgreSQL connection string

# Application
FLASK_ENV=production                   # Production optimizations
HOST=0.0.0.0                          # Bind to all interfaces
PORT=5000                             # Application port
REDIS_URL=redis://redis:6379/0        # Session storage
```

### File Structure
```
/app/
├── app.py              # Main Flask application
├── startup.py          # Production startup script
├── init_db.py          # Database initialization utility
├── requirements.txt    # Python dependencies
├── templates/          # Jinja2 templates
├── static/            # CSS, JS, images (if any)
├── data/              # SQLite database (development)
└── logs/              # Application logs
```

## 🧪 Testing & Debugging

### Health Check Endpoint
```
GET /health
```
Returns application status and database connectivity for monitoring.

### Logging Configuration
- **Startup logs**: `/app/logs/startup.log`
- **Application logs**: Console output (captured by Docker)
- **Error tracking**: Flask's built-in error handling with stack traces

### Common Debugging Commands
```bash
# View logs
docker-compose logs web

# Database inspection
docker-compose exec db psql -U tautulli_user -d tautulli_exporter

# Container status
docker-compose ps

# Restart application
docker-compose restart web
```

## 🔧 Configuration Management

### Environment Variables
All sensitive configuration is handled via environment variables:
- `SECRET_KEY`: Flask session encryption (required)
- `DATABASE_URL`: Database connection string (required)
- `REDIS_URL`: Session storage connection (optional, defaults to file-based sessions)
- `FLASK_ENV`: Environment mode (development/production)

### Database Configuration
The application automatically:
- **Creates tables** on first startup
- **Creates default admin user** (admin/admin)
- **Handles migrations** for schema changes

### Tautulli Configuration
Admin users configure Tautulli connection through the web interface:
- **URL validation**: Ensures proper format and connectivity
- **API key testing**: Validates permissions and access
- **Connection persistence**: Stored securely in database

## 🚀 Performance Considerations

### Database Optimization
- **Connection pooling** via SQLAlchemy
- **Query optimization** with proper indexes
- **Minimal data storage** (configuration only, not watch history)

### Caching Strategy
- **Redis sessions** for better performance
- **Static asset caching** via browser headers
- **API response optimization** with streaming for large exports

### Security vs Performance Balance
- **Rate limiting** prevents abuse while allowing normal usage
- **Security headers** add minimal overhead
- **Password hashing** uses secure but reasonable iteration counts

## 📈 Monitoring & Maintenance

### Application Monitoring
- **Health check endpoint** for uptime monitoring
- **Error logging** with detailed stack traces
- **Performance metrics** via Flask built-in profiling

### Security Monitoring
- **Failed login tracking** via rate limiter
- **Admin action logging** for audit trails
- **Configuration change tracking** via database timestamps

### Backup Considerations
- **Database backup**: Regular PostgreSQL dumps
- **Configuration export**: Admin can export settings
- **No watch history storage**: Data lives in Tautulli (backup there)

## 🔄 Update Process

### Application Updates
1. **Pull new code**: `git pull origin main`
2. **Rebuild containers**: `docker-compose up -d --build`
3. **Verify health**: Check `/health` endpoint
4. **Test functionality**: Verify exports and user management

### Database Migrations
- **Automatic schema updates** on container restart
- **Backup before major updates** recommended
- **Rollback strategy**: Restore from backup if needed

---

## 🔧 Development Notes

### Code Style
- **PEP 8 compliance** for Python code
- **Type hints** for function signatures
- **Docstrings** for all public functions
- **Comments** for complex business logic

### Security Guidelines
- **Never commit secrets** to version control
- **Validate all inputs** from users and external APIs
- **Use parameterized queries** to prevent SQL injection
- **Follow OWASP guidelines** for web application security

This documentation covers the technical implementation details. For user-facing documentation, see the main [README.md](README.md).