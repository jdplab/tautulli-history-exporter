# 🎬 Tautulli History Exporter

A modern, production-ready web application to export watch history from Tautulli with comprehensive security, beautiful UI, and advanced filtering capabilities.

## ✨ Features

### 🔐 **Security & Authentication**
- **Multi-layered Security**: Rate limiting, CSRF protection, secure headers
- **Secure Authentication**: Encrypted sessions with forced password changes
- **Production Hardening**: Security headers, input validation, error handling
- **Session Management**: Redis-backed sessions with proper expiration

### 🎨 **Modern User Interface**
- **Dark Mode Toggle**: Beautiful dark/light theme with smooth transitions
- **Responsive Design**: Bootstrap 5.3 with modern gradients and animations
- **Intuitive UX**: Clean, professional interface with visual feedback
- **Accessibility**: Proper contrast ratios and keyboard navigation

### 📊 **Advanced Data Management**
- **Smart Filtering**: Date range selection with server-side filtering
- **Watch Status**: Visual indicators for completed vs. partial watches
- **Flexible Export**: CSV export with customizable data fields
- **Real-time Validation**: Live connection testing and form validation

### 🚀 **Enterprise Features**
- **Production Ready**: Comprehensive security and deployment guides
- **Monitoring**: Health checks, logging, and error tracking
- **Scalability**: Redis caching and optimized database queries
- **Docker Support**: Complete containerized deployment with orchestration

## 🚀 Quick Start

### **Option 1: Docker Deployment (Recommended)**

1. **Clone and Configure**:
   ```bash
   git clone <repository-url>
   cd tautulli-history-exporter
   
   # Create environment file (see Environment Setup section for details)
   # For quick start, create .env with basic settings:
   echo "SECRET_KEY=dev-secret-change-for-production" > .env
   echo "DATABASE_URL=sqlite:///tautulli_exporter.db" >> .env
   echo "FLASK_ENV=development" >> .env
   ```

   📋 **For production deployment**: See the detailed [Environment Setup](#-environment-setup) section below for secure configuration.

2. **Deploy with Docker**:
   ```bash
   docker-compose up -d
   ```

3. **Access and Setup**:
   - Open **http://localhost:5000**
   - Login: `admin` / `admin` (change immediately!)
   - Configure Tautulli connection
   - Start exporting data!

### **Option 2: Production Deployment**

For production deployment with HTTPS, monitoring, and security hardening:

📖 **See `PRODUCTION.md`** for comprehensive deployment guides including:
- Cloud platform deployment (AWS, GCP, Azure)
- Reverse proxy setup (Nginx/Apache)
- SSL/TLS configuration
- Monitoring and logging setup

🔒 **Use `SECURITY-CHECKLIST.md`** to validate your security configuration before going live.

## ⚙️ Environment Setup

### **📋 Step-by-Step Environment Configuration**

Since `.env.example` files may not be available in some repositories, here's how to create your environment configuration from scratch:

#### **🔧 For Development Setup**

1. **Create `.env` file**:
   ```bash
   # Navigate to project directory
   cd tautulli-history-exporter
   
   # Create environment file
   touch .env  # Linux/Mac
   # or
   New-Item .env  # Windows PowerShell
   ```

2. **Add development configuration**:
   ```bash
   # Copy and paste this into your .env file:
   
   # Development Environment Configuration
   # ====================================
   
   # Flask secret key (generate new one for production!)
   SECRET_KEY=dev-secret-key-change-for-production-use
   
   # Development database (SQLite for simplicity)
   DATABASE_URL=sqlite:///tautulli_exporter.db
   
   # Development settings
   FLASK_ENV=development
   FLASK_DEBUG=true
   
   # Optional: Redis (leave empty to use in-memory sessions)
   REDIS_URL=
   
   # Development security (relaxed for testing)
   RATE_LIMIT=1000
   SESSION_TIMEOUT=480
   ```

3. **Run development server**:
   ```bash
   python app.py
   # Access at http://localhost:5000
   ```

#### **🚀 For Production Setup**

1. **Create production `.env` file**:
   ```bash
   # Create environment file
   touch .env  # Linux/Mac
   # or  
   New-Item .env  # Windows PowerShell
   ```

2. **Generate secure secrets**:
   ```bash
   # Generate SECRET_KEY (64 characters)
   python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
   
   # Generate secure database password
   python -c "import secrets, string; chars=string.ascii_letters+string.digits+'!@#$%^&*()'; print('POSTGRES_PASSWORD=' + ''.join(secrets.choice(chars) for i in range(20)))"
   ```

3. **Add production configuration**:
   ```bash
   # Copy the generated values above, then add this complete configuration:
   
   # Production Environment Configuration
   # ===================================
   
   # CRITICAL: Use the generated values from step 2
   SECRET_KEY=YOUR_GENERATED_64_CHAR_SECRET_HERE
   POSTGRES_PASSWORD=YOUR_GENERATED_SECURE_PASSWORD_HERE
   
   # Production database (auto-configured for Docker)
   DATABASE_URL=postgresql://tautulli_user:${POSTGRES_PASSWORD}@db:5432/tautulli_exporter
   
   # Redis session storage (auto-configured for Docker)
   REDIS_URL=redis://redis:6379/0
   
   # Production settings (CRITICAL - never change these)
   FLASK_ENV=production
   FLASK_DEBUG=false
   
   # Application settings
   HOST=0.0.0.0
   PORT=5000
   
   # Security settings
   RATE_LIMIT=100
   SESSION_TIMEOUT=60
   MAX_EXPORT_ITEMS=10000
   SECURITY_HEADERS=true
   
   # Reverse proxy settings (if using Nginx/Apache)
   REVERSE_PROXY=true
   FORCE_HTTPS=true
   ```

4. **Validate configuration**:
   ```bash
   # Test environment loading
   python -c "
   from dotenv import load_dotenv
   import os
   load_dotenv()
   
   # Check critical settings
   secret = os.getenv('SECRET_KEY', '')
   if len(secret) >= 32:
       print('✅ SECRET_KEY length OK')
   else:
       print('❌ SECRET_KEY too short (need 32+ chars)')
   
   if os.getenv('FLASK_DEBUG', '').lower() != 'true':
       print('✅ DEBUG disabled (production safe)')
   else:
       print('⚠️  DEBUG enabled (only for development)')
   
   if os.getenv('POSTGRES_PASSWORD'):
       print('✅ Database password set')
   else:
       print('❌ Database password missing')
   "
   ```

#### **🐳 For Docker Deployment**

1. **Create `.env` file** (same as production setup above)

2. **Deploy with Docker**:
   ```bash
   # Start all services
   docker-compose up -d
   
   # Check service health
   docker-compose ps
   
   # View logs if needed
   docker-compose logs web
   ```

3. **Verify deployment**:
   ```bash
   # Test application
   curl http://localhost:5000
   
   # Check database connection
   docker-compose exec web python -c "
   from app import db
   try:
       db.engine.execute('SELECT 1')
       print('✅ Database connection OK')
   except:
       print('❌ Database connection failed')
   "
   ```

### **🔒 Security Validation Checklist**

Before deploying to production, verify these settings in your `.env` file:

```bash
# Run this validation script:
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('🔒 Security Validation')
print('=' * 40)

# Check SECRET_KEY
secret = os.getenv('SECRET_KEY', '')
if len(secret) >= 64:
    print('✅ SECRET_KEY: Strong (64+ chars)')
elif len(secret) >= 32:
    print('⚠️  SECRET_KEY: Acceptable (32+ chars)')
else:
    print('❌ SECRET_KEY: Too weak (need 32+ chars)')

# Check database password
db_pass = os.getenv('POSTGRES_PASSWORD', '')
if len(db_pass) >= 16:
    print('✅ DB Password: Strong (16+ chars)')
else:
    print('❌ DB Password: Too weak (need 16+ chars)')

# Check debug mode
debug = os.getenv('FLASK_DEBUG', '').lower()
if debug != 'true':
    print('✅ Debug Mode: Disabled (production safe)')
else:
    print('❌ Debug Mode: Enabled (security risk!)')

# Check environment
env = os.getenv('FLASK_ENV', '')
if env == 'production':
    print('✅ Environment: Production')
else:
    print('⚠️  Environment: ' + (env or 'not set'))

print('=' * 40)
print('Review any ❌ or ⚠️  items before deployment!')
"
```

### **📁 Environment File Reference**

| File | Purpose | Include in Git? |
|------|---------|----------------|
| `.env` | Your actual secrets | ❌ **NO** (security risk) |
| `.env.example` | Template with safe defaults | ✅ Yes (if available) |
| `.env.production` | Production template | ✅ Yes (if available) |

**⚠️ NEVER commit your actual `.env` file to Git!** It contains sensitive secrets.

## ⚙️ Configuration

### **Environment Variables Summary**

💡 **For detailed step-by-step setup instructions, see the [Environment Setup](#-environment-setup) section above.**

**Quick Reference - Required Variables:**

```bash
# Security (REQUIRED)
SECRET_KEY=your-super-secret-key-64-chars-min
POSTGRES_PASSWORD=your-secure-database-password

# Database (Auto-configured in Docker)
DATABASE_URL=postgresql://tautulli_user:${POSTGRES_PASSWORD}@db:5432/tautulli_exporter

# Redis Session Storage (Auto-configured)
REDIS_URL=redis://redis:6379/0

# Application Settings
FLASK_ENV=production
FLASK_DEBUG=false
```

### **Security Requirements**

⚠️ **CRITICAL**: Before production deployment:

1. **Generate Strong Secrets**:
   ```bash
   # Generate SECRET_KEY (Linux/Mac)
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Generate SECRET_KEY (Windows PowerShell)
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Secure Database Password**: Use 16+ character password with mixed case, numbers, symbols

3. **Change Default Credentials**: Login as `admin`/`admin` and change immediately

### **Tautulli Configuration**

1. **Get API Key**: 
   - Tautulli → Settings → Web Interface → API → Show API Key
   
2. **Configure Access**:
   - URL: `http://your-tautulli-server:8181`
   - API Key: Your copied API key
   - Test connection before saving

## 📊 Data Export Features

### **Enhanced Filtering Options**

- **Date Range Selection**: Pick start and end dates with calendar widgets
- **Media Type Filtering**: Movies, TV episodes, music tracks
- **Watch Status Filter**: Completed, partial, or all watches
- **User Selection**: Choose from friendly usernames
- **Result Limiting**: Control export size (1-1000 items)

### **CSV Export Data**

The exported CSV includes comprehensive watch data:

| Field | Description | Example |
|-------|-------------|---------|
| **Date** | Watch date/time | 2025-09-22 14:30:15 |
| **User** | Friendly username | John Doe |
| **Title** | Content title | Breaking Bad - S01E01 |
| **Media Type** | Content category | episode |
| **Duration** | Runtime (minutes) | 47 |
| **Percent Complete** | Watch completion | 95% |
| **Watched Status** | Completion badge | ✅ Completed / ⏱️ Partial |
| **IP Address** | Client IP | 192.168.1.100 |

### **Visual Data Indicators**

- 🟢 **Completed**: 90%+ watch percentage
- 🟡 **Partial**: Less than 90% watched
- 📺 **TV Shows**: Episode information included
- 🎬 **Movies**: Full title display
- 🎵 **Music**: Track and artist details

## 🛠️ Development

### **Local Development Setup**

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env
# Edit .env with development settings

# 4. Initialize database
python -c "from app import db; db.create_all()"

# 5. Run development server
python app.py
```

### **Development Environment Variables**

```bash
SECRET_KEY=dev-secret-key-not-for-production
DATABASE_URL=sqlite:///tautulli_exporter.db
FLASK_ENV=development
FLASK_DEBUG=true
```

### **Project Structure**

```
tautulli-history-exporter/
├── app.py                 # Main Flask application
├── startup.py            # Production validation script
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Container orchestration
├── Dockerfile           # Container build instructions
├── templates/           # Jinja2 HTML templates
│   ├── base.html       # Base layout with dark mode
│   ├── index.html      # Main export interface  
│   ├── config.html     # Tautulli configuration
│   └── login.html      # Authentication form
├── static/             # CSS, JS, images
├── PRODUCTION.md       # Deployment guide
├── SECURITY-CHECKLIST.md # Security validation
└── README.md          # This file
```

### **API Integration**

**Tautulli API Endpoints Used:**
- `get_user_names`: Retrieve user list with friendly names
- `get_history`: Fetch watch history with filtering
- Connection testing and validation

**Rate Limiting:**
- API calls are rate-limited to prevent abuse
- Automatic retry logic for failed requests
- Error handling for API timeouts

## 🔧 Troubleshooting

### **Common Issues & Solutions**

#### **🔌 Connection Problems**

**Problem**: Can't connect to Tautulli
```
✅ Solutions:
• Verify Tautulli URL format: http://ip-address:port
• Check API key in Tautulli Settings → Web Interface → API
• Ensure Tautulli is accessible from Docker container network
• Test with: docker exec -it container_name curl http://tautulli-url/api/v2?apikey=KEY&cmd=get_user_names
```

**Problem**: Database connection errors
```
✅ Solutions:
• Check POSTGRES_PASSWORD in .env file
• Restart containers: docker-compose down && docker-compose up -d
• Verify PostgreSQL container health: docker-compose ps
```

#### **👤 User & Data Issues**

**Problem**: No users in dropdown
```
✅ Solutions:
• Test Tautulli connection in Configuration page
• Verify API key has proper permissions
• Check Tautulli has users with watch history
• Review application logs: docker-compose logs web
```

**Problem**: Date filtering not working
```
✅ Solutions:
• Dates are filtered server-side (not Tautulli API limitation)
• Ensure date format is correct (YYYY-MM-DD)
• Check timezone settings in browser
```

#### **💾 Export Problems**

**Problem**: CSV download fails
```
✅ Solutions:
• Verify data exists in history table
• Check browser popup/download blocker settings
• Try smaller date range or result limit
• Clear browser cache and cookies
```

#### **🔒 Security & Authentication**

**Problem**: Login issues after password change
```
✅ Solutions:
• Clear browser cookies and cache
• Restart application containers
• Check session storage (Redis) health
```

**Problem**: Rate limiting blocking requests
```
✅ Solutions:
• Wait for rate limit window to reset (1 minute)
• Reduce request frequency
• Check logs for rate limit violations
```

### **🐛 Debug Mode**

Enable debug logging by setting in `.env`:
```bash
FLASK_DEBUG=true
FLASK_ENV=development
```

### **📋 Health Checks**

Monitor application health:
```bash
# Check container status
docker-compose ps

# View application logs
docker-compose logs -f web

# Test database connection
docker-compose exec db psql -U tautulli_user -d tautulli_exporter -c "SELECT COUNT(*) FROM users;"

# Test Redis connection
docker-compose exec redis redis-cli ping
```

## 🔐 Security & Production

### **Production Deployment**

📖 **Complete Deployment Guide**: See `PRODUCTION.md` for:
- Docker deployment with HTTPS
- Cloud platform deployment (AWS, GCP, Azure)
- Reverse proxy configuration (Nginx/Apache)
- SSL/TLS certificate setup
- Monitoring and logging configuration
- Performance optimization

🔒 **Security Validation**: Use `SECURITY-CHECKLIST.md` to verify:
- Environment security settings
- Network and access controls
- Data protection measures
- Monitoring and incident response
- Compliance requirements

### **Security Features**

#### **Application Security**
- ✅ **CSRF Protection**: All forms protected against cross-site attacks
- ✅ **Rate Limiting**: 100 requests/minute per IP to prevent abuse
- ✅ **Security Headers**: CSP, HSTS, X-Frame-Options, etc.
- ✅ **Session Security**: HTTPOnly, Secure, SameSite cookies
- ✅ **Input Validation**: All user inputs sanitized and validated
- ✅ **Error Handling**: Secure error messages without information leakage

#### **Infrastructure Security**
- ✅ **Container Hardening**: Non-root user, minimal attack surface
- ✅ **Database Security**: Encrypted connections, limited permissions
- ✅ **Redis Security**: Password protection, connection encryption
- ✅ **Environment Isolation**: Secrets management with Docker secrets
- ✅ **Health Monitoring**: Automated health checks and recovery

#### **Operational Security**
- ✅ **Structured Logging**: Security events, authentication attempts
- ✅ **Audit Trail**: User actions and configuration changes
- ✅ **Backup Strategy**: Automated database backups with encryption
- ✅ **Update Management**: Regular security updates and patching

### **Security Best Practices**

1. **Strong Credentials**: Use complex passwords and API keys
2. **HTTPS Only**: Never deploy without SSL/TLS in production
3. **Network Security**: Use firewalls and restrict access
4. **Regular Updates**: Keep dependencies and containers updated
5. **Monitoring**: Set up alerts for security events
6. **Backup**: Regular encrypted backups with tested recovery

### **Compliance Considerations**

- **Data Privacy**: User watch history is sensitive data
- **Access Control**: Implement proper user management
- **Audit Logging**: Maintain logs for compliance requirements
- **Data Retention**: Configure appropriate data retention policies

## 🏗️ Architecture & Technology

### **Technology Stack**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Flask 2.3.3 + SQLAlchemy | Web framework & ORM |
| **Database** | PostgreSQL 15 | Persistent data storage |
| **Cache** | Redis 7 | Session storage & caching |
| **Frontend** | Bootstrap 5.3.2 + Vanilla JS | Responsive UI with dark mode |
| **Container** | Docker + Docker Compose | Containerized deployment |
| **Security** | Flask-Limiter + Flask-Talisman | Rate limiting & security headers |
| **WSGI** | Gunicorn | Production application server |

### **Application Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Reverse Proxy │    │   Web Container  │    │   Tautulli API  │
│  (Nginx/Apache) │◄──►│   Flask + Gun.   │◄──►│   Data Source   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────▼────────┐
                       │  PostgreSQL DB  │
                       │   Data Storage  │
                       └─────────────────┘
                                │
                       ┌────────▼────────┐
                       │   Redis Cache   │
                       │ Session Storage │
                       └─────────────────┘
```

### **Key Features Overview**

- 🎨 **Modern UI**: Dark/light mode with smooth animations
- 🔍 **Smart Filtering**: Date ranges, media types, watch status
- 📊 **Data Insights**: Visual indicators for completion status
- 🔐 **Enterprise Security**: Multi-layered protection
- 🚀 **Production Ready**: Comprehensive deployment & monitoring
- 📱 **Responsive**: Works on desktop, tablet, and mobile

---

## 📄 License & Credits

### **License**
This project is open source under the MIT License. Use responsibly and in accordance with:
- Tautulli's terms of service
- Your local data privacy regulations
- Applicable copyright laws

### **Acknowledgments**
- **Tautulli Team**: For the excellent media server monitoring tool
- **Flask Community**: For the robust web framework
- **Bootstrap Team**: For the beautiful UI components
- **Docker Team**: For containerization technology

### **Contributing**
Contributions welcome! Please:
1. Fork the repository
2. Create feature branches
3. Add tests for new functionality
4. Follow security best practices
5. Submit pull requests

---

## 📞 Support & Resources

### **Documentation**
- 📖 **`PRODUCTION.md`**: Complete deployment guide
- 🔒 **`SECURITY-CHECKLIST.md`**: Security validation checklist
- 🛠️ **`README.md`**: This comprehensive guide

### **Getting Help**
- **Issues**: Report bugs and feature requests
- **Security**: Report security issues privately
- **Community**: Join discussions and share experiences

### **Version Information**
- **Current Version**: 2.0.0 (Production Ready)
- **Last Updated**: September 2025
- **Python**: 3.11+ supported
- **Docker**: 20.10+ recommended

---

**⚡ Ready to deploy?** Start with the Quick Start section and follow the production guides for a secure, scalable deployment!