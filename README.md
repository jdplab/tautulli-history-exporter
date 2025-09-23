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

## 🚀 Production Deployment

This application is designed for production use with Docker. Follow these steps for a secure, production-ready deployment.

### **📋 Prerequisites**

- Docker and Docker Compose installed
- Tautulli server with API access
- Basic terminal/command line knowledge

### **⚡ Quick Deployment**

### **🔒 Security & Default Credentials**

> **⚠️ CRITICAL SECURITY INFORMATION**
> 
> **Default Login Credentials:**
> - **Username:** `admin`
> - **Password:** `admin`
> 
> **SECURITY REQUIREMENTS:**
> 1. ⚠️ **IMMEDIATELY change the default password** after first login
> 2. 🔐 Use a **strong, unique password** (minimum 6 characters)
> 3. 🛡️ Consider using **HTTPS with SSL certificates** in production
> 4. 🚫 **Never leave default credentials** in production environments
> 
> The application will **force a password change** on first login for security.

#### **Step 1: Clone Repository**
```bash
git clone https://github.com/jdplab/tautulli-history-exporter
cd tautulli-history-exporter
```

#### **Step 2: Generate Secure Configuration**
```bash
# Generate SECRET_KEY and save to .env
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" > .env

# Generate database password and append to .env
python3 -c "import secrets, string; chars=string.ascii_letters+string.digits; print('POSTGRES_PASSWORD=' + ''.join(secrets.choice(chars) for i in range(20)))" >> .env

# Add the rest of the production configuration
cat >> .env << 'EOF'

# Production database (auto-configured)
DATABASE_URL=postgresql://tautulli_user:${POSTGRES_PASSWORD}@db:5432/tautulli_exporter

# Redis session storage (auto-configured)
REDIS_URL=redis://redis:6379/0

# Production settings (do not change)
FLASK_ENV=production
FLASK_DEBUG=false
HOST=0.0.0.0
PORT=5000

# Security settings
RATE_LIMIT=100
SESSION_TIMEOUT=60
MAX_EXPORT_ITEMS=10000
SECURITY_HEADERS=true
EOF

# Verify your .env file was created correctly
echo "✅ Generated .env file:"
cat .env
```

#### **Step 3: Deploy with Docker**
```bash
# Start all services
docker-compose up -d

# Verify deployment
docker-compose ps
```

#### **Step 4: Initial Login & Security Setup**

> **⚠️ IMPORTANT - Default Credentials**
> 
> **Default Username:** `admin`  
> **Default Password:** `admin`
> 
> ⚠️ **SECURITY NOTICE**: These are the default credentials created on first startup. You **MUST** change them immediately after first login for security reasons.

1. **Access the application**: Open http://localhost:5000
2. **Login**: Use the default credentials above
3. **Change password**: You'll be prompted to create a strong admin password immediately after login
4. **Configure Tautulli**:
   - Get your API key: Tautulli → Settings → Web Interface → API → Show API Key
   - Enter your Tautulli URL: `http://your-tautulli-server:8181`
   - Enter your API key and test the connection
   - Save configuration

#### **Step 5: Validate Security**
Run this security check to ensure proper configuration:

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('🔒 Security Validation')
print('=' * 40)

# Check SECRET_KEY
secret = os.getenv('SECRET_KEY', '')
if len(secret) >= 64:
    print('✅ SECRET_KEY: Strong')
else:
    print('❌ SECRET_KEY: Too weak')

# Check database password
db_pass = os.getenv('POSTGRES_PASSWORD', '')
if len(db_pass) >= 16:
    print('✅ Database Password: Strong')
else:
    print('❌ Database Password: Too weak')

# Check debug mode
if os.getenv('FLASK_DEBUG', '').lower() != 'true':
    print('✅ Debug Mode: Disabled (secure)')
else:
    print('❌ Debug Mode: Enabled (security risk!)')

print('=' * 40)
print('✅ Ready for production!' if all([len(secret) >= 64, len(db_pass) >= 16, os.getenv('FLASK_DEBUG', '').lower() != 'true']) else '❌ Fix security issues before deployment')
"
```

### **� Additional Security (Recommended)**

For internet-facing deployments, set up a reverse proxy with HTTPS:

📖 **See `PRODUCTION.md`** for detailed guides on:
- Nginx/Apache reverse proxy setup
- SSL/TLS certificate configuration
- Cloud platform deployment
- Advanced monitoring and logging

🔒 **Use `SECURITY-CHECKLIST.md`** to validate your complete security configuration.

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

## 🛠️ Project Structure

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
├── PRODUCTION.md       # Advanced deployment guide
├── SECURITY-CHECKLIST.md # Security validation
└── README.md          # This file
```

### **API Integration**

**Tautulli API Endpoints Used:**
- `get_user_names`: Retrieve user list with friendly names
- `get_history`: Fetch watch history with filtering
- Connection testing and validation

**Security Features:**
- Rate limiting prevents API abuse
- Automatic retry logic for failed requests
- Comprehensive error handling

## 🔧 Troubleshooting

### **Deployment Issues**

#### **🐳 Docker Problems**

**Issue**: Containers won't start
```bash
# Check service status
docker-compose ps

# View error logs
docker-compose logs

# Restart services
docker-compose down && docker-compose up -d
```

**Issue**: Database connection errors
```bash
# Verify .env file exists and has correct values
cat .env | grep -E "(SECRET_KEY|POSTGRES_PASSWORD)"

# Check PostgreSQL container health
docker-compose exec db pg_isready -U tautulli_user

# Reset database if needed
docker-compose down -v && docker-compose up -d
```

#### **🔌 Connection Problems**

**Issue**: Can't connect to Tautulli
```
✅ Solutions:
• Verify Tautulli URL format: http://ip-address:port
• Check API key in Tautulli Settings → Web Interface → API
• Ensure Tautulli is accessible from Docker network:
  docker-compose exec web curl http://your-tautulli-server:8181/api/v2?apikey=KEY&cmd=get_user_names
```

**Issue**: No users in dropdown
```
✅ Solutions:
• Test Tautulli connection in Configuration page
• Verify API key has proper permissions
• Check Tautulli has users with watch history
• Review logs: docker-compose logs web
```

#### **💾 Data Export Problems**

**Issue**: CSV download fails
```
✅ Solutions:
• Verify data exists (check user history in Tautulli)
• Check browser popup/download settings
• Try smaller date range or result limit
• Clear browser cache and restart containers
```

**Issue**: Date filtering not working
```
✅ Solutions:
• Dates are filtered server-side after API retrieval
• Ensure proper date format (YYYY-MM-DD)
• Check browser timezone settings
```

#### **🔒 Security & Authentication**

**Issue**: Having trouble with login credentials
```
✅ Solutions:
• Use the default credentials: username=admin, password=admin
• Check if database is properly initialized:
  docker-compose logs web | grep "Database initialization"
• Manually reset the admin user:
  docker-compose exec web python -c "
  from app import app, db, User
  from werkzeug.security import generate_password_hash
  with app.app_context():
      admin = User.query.filter_by(username='admin').first()
      if admin:
          admin.must_change_password = True
          db.session.commit()
          print('Admin user reset to require password change')
      else:
          print('Admin user not found')
  "
• Full database reset if needed:
  docker-compose down -v && docker-compose up -d
```

**Issue**: Can't login after password change
```
✅ Solutions:
• Clear browser cookies and cache
• Restart containers: docker-compose restart
• Check Redis health: docker-compose exec redis redis-cli ping
```

**Issue**: Rate limiting blocking requests
```
✅ Solutions:
• Wait 1 minute for rate limit reset
• Check logs: docker-compose logs web | grep "rate limit"
• Adjust RATE_LIMIT in .env if needed
```

### **� Health Monitoring**

Check application health with these commands:

```bash
# Overall system status
docker-compose ps

# Application logs
docker-compose logs -f web

# Database connection test
docker-compose exec db psql -U tautulli_user -d tautulli_exporter -c "SELECT version();"

# Redis connection test
docker-compose exec redis redis-cli ping

# Web application health
curl -f http://localhost:5000 || echo "Web service down"
```

### **📋 Performance Optimization**

For high-traffic deployments:

```bash
# Monitor resource usage
docker stats

# Increase rate limits in .env
RATE_LIMIT=500

# Add more worker processes (edit docker-compose.yml)
command: gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
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