# Production Deployment Guide

This guide covers deploying Tautulli History Exporter securely in a production environment.

## 🔒 Security Checklist

### ✅ **Pre-Deployment Security**

1. **Generate Strong Secrets**
   ```bash
   # Generate a secure secret key
   python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
   
   # Generate a secure database password
   python -c "import secrets; print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(32))"
   ```

2. **Create Production Environment File**
   ```bash
   cp .env.production .env
   # Edit .env with your secure values
   ```

3. **Set Proper File Permissions**
   ```bash
   chmod 600 .env
   chown root:root .env
   ```

## 🚀 **Production Deployment Options**

### Option 1: Direct Docker Deployment

```bash
# 1. Clone and configure
git clone <repository-url>
cd tautulli-history-exporter

# 2. Set up environment
cp .env.production .env
# Edit .env with your secure values

# 3. Deploy
docker-compose up -d
```

### Option 2: Behind Reverse Proxy (Recommended)

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /login {
        limit_req zone=login burst=3 nodelay;
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Apache Configuration
```apache
<VirtualHost *:80>
    ServerName your-domain.com
    Redirect permanent / https://your-domain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName your-domain.com
    
    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /path/to/your/certificate.crt
    SSLCertificateKeyFile /path/to/your/private.key
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
    SSLHonorCipherOrder on

    # Security Headers
    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"

    # Proxy Configuration
    ProxyPreserveHost On
    ProxyPass / http://localhost:5000/
    ProxyPassReverse / http://localhost:5000/
    
    # Rate Limiting (requires mod_evasive)
    DOSHashTableSize    2048
    DOSPageCount        10
    DOSSiteCount        50
    DOSPageInterval     2
    DOSSiteInterval     2
    DOSBlockingPeriod   60
</VirtualHost>
```

## 🔧 **Production Docker Compose**

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    environment:
      - DATABASE_URL=postgresql://tautulli:${POSTGRES_PASSWORD}@db:5432/tautulli_exporter
      - SECRET_KEY=${SECRET_KEY}
      - FLASK_ENV=production
      - SECURITY_HEADERS=true
      - RATE_LIMIT=60
      - SESSION_TIMEOUT=240
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - tautulli_network
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=tautulli_exporter
      - POSTGRES_USER=tautulli
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    networks:
      - tautulli_network
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    networks:
      - tautulli_network
    deploy:
      resources:
        limits:
          memory: 128M
          cpus: '0.1'

  # Optional: Database backup service
  db-backup:
    image: postgres:15-alpine
    depends_on:
      - db
    volumes:
      - ./backups:/backups
    networks:
      - tautulli_network
    environment:
      - PGPASSWORD=${POSTGRES_PASSWORD}
    command: >
      sh -c "
      while true; do
        sleep 86400
        pg_dump -h db -U tautulli -d tautulli_exporter > /backups/backup_$$(date +%Y%m%d_%H%M%S).sql
        find /backups -name '*.sql' -mtime +7 -delete
      done"

networks:
  tautulli_network:
    driver: bridge

volumes:
  postgres_data:
```

## 📋 **Security Best Practices**

### 1. **Network Security**
- Use a reverse proxy (Nginx/Apache) with HTTPS
- Implement fail2ban for brute force protection
- Configure firewall to only allow necessary ports
- Use private networks for container communication

### 2. **Container Security**
- Run containers as non-root user
- Use specific image tags, not `latest`
- Regularly update base images
- Scan images for vulnerabilities

### 3. **Data Protection**
- Encrypt data at rest and in transit
- Regular database backups
- Secure backup storage
- Test backup restoration procedures

### 4. **Monitoring & Logging**
- Centralized logging (ELK stack, Splunk, etc.)
- Monitor application metrics
- Set up alerts for security events
- Regular security audits

### 5. **Access Control**
- Strong password policies
- Regular password rotation
- Principle of least privilege
- Network segmentation

## 🔍 **Monitoring Setup**

### Health Checks
```bash
# Add to crontab for monitoring
*/5 * * * * curl -f http://localhost:5000/health || echo "Application down" | mail -s "Alert" admin@yourdomain.com
```

### Log Monitoring
```bash
# Monitor failed login attempts
tail -f logs/app.log | grep "Failed login attempt"

# Monitor rate limiting
tail -f logs/app.log | grep "Rate limit exceeded"
```

## 🚨 **Incident Response**

### Security Incident Checklist
1. **Immediate Response**
   - Isolate affected systems
   - Preserve evidence
   - Assess scope of breach

2. **Investigation**
   - Review logs for suspicious activity
   - Identify attack vectors
   - Document findings

3. **Recovery**
   - Patch vulnerabilities
   - Reset compromised credentials
   - Restore from clean backups if needed

4. **Post-Incident**
   - Update security procedures
   - Implement additional controls
   - Conduct security training

## 📞 **Support & Maintenance**

### Regular Maintenance Tasks
- [ ] Weekly: Review security logs
- [ ] Monthly: Update dependencies
- [ ] Quarterly: Security audit
- [ ] Annually: Penetration testing

### Emergency Contacts
- System Administrator: [contact info]
- Security Team: [contact info]
- Database Administrator: [contact info]

## 🔄 **Backup & Recovery**

### Automated Backup Script
```bash
#!/bin/bash
# backup.sh - Database backup script

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
PGPASSWORD="your-db-password"

# Create backup
pg_dump -h localhost -U tautulli -d tautulli_exporter > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Upload to secure cloud storage (optional)
# aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://your-backup-bucket/
```

### Recovery Procedure
```bash
# Stop application
docker-compose down

# Restore database
gunzip -c backup_YYYYMMDD_HHMMSS.sql.gz | psql -h localhost -U tautulli -d tautulli_exporter

# Start application
docker-compose up -d
```

## ⚠️ **Important Security Notes**

1. **Never expose the database directly to the internet**
2. **Always use HTTPS in production**
3. **Regularly update all components**
4. **Monitor logs for suspicious activity**
5. **Test backups regularly**
6. **Have an incident response plan**
7. **Keep security patches current**
8. **Use strong, unique passwords**
9. **Enable two-factor authentication if possible**
10. **Regular security assessments**