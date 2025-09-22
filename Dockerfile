FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories and set permissions
RUN mkdir -p /app/data /app/logs && \
    chmod 755 /app/data /app/logs

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Run the application with startup validation
CMD ["sh", "-c", "python startup.py && gunicorn --bind 0.0.0.0:5000 --workers 4 --access-logfile /app/logs/access.log --error-logfile /app/logs/error.log app:app"]