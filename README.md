# 🎬 Tautulli History Exporter

A simple web app that makes it easy to export your Plex watch history from Tautulli. Perfect for homelabbers who want to back up their viewing data or analyze their watching habits.

## 🎯 What Problem Does This Solve?

Ever wanted to export your Plex watch history but found Tautulli's built-in export features limited? This tool provides:

- **Easy CSV exports** of your watch history with smart filtering
- **User-friendly interface** with dark/light mode toggle
- **Flexible date ranges** and media type filtering  
- **Clean data format** that's perfect for spreadsheets or analysis
- **Simple setup** with Docker - no complex configuration needed

## ✨ Features

### 🎨 **Clean Interface**
- Dark/light mode toggle for comfortable viewing
- Responsive design that works on desktop and mobile
- Visual indicators for completed vs. partial watches
- Easy-to-use date pickers and filters

### 📊 **Smart Data Export**
- Filter by date range, user, media type, and watch completion
- Export up to 10,000 items at once
- CSV format includes watch date, user, title, duration, completion percentage
- Shows both movies and TV episodes with proper formatting

### � **Simple Setup**
- One-command Docker deployment
- Automatic database setup
- Built-in security features without the complexity
- Works with any Tautulli installation

## 🤖 AI Disclosure

This project was developed with assistance from AI tools (GitHub Copilot and Claude) to ensure good coding practices and comprehensive documentation. All AI-generated code has been reviewed and tested.

## 🚀 How to Install

### Prerequisites
- Docker and Docker Compose installed on your system
- A running Tautulli server with API access
- 5 minutes of your time

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/jdplab/tautulli-history-exporter
   cd tautulli-history-exporter
   ```

2. **Generate security keys**
   ```bash
   # Generate SECRET_KEY and save to .env
   python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" > .env
   
   # Generate database password and append to .env
   python3 -c "import secrets, string; chars=string.ascii_letters+string.digits; print('POSTGRES_PASSWORD=' + ''.join(secrets.choice(chars) for i in range(20)))" >> .env
   ```

3. **Add the rest of the configuration**
   ```bash
   cat >> .env << 'EOF'
   
   # Database configuration
   DATABASE_URL=postgresql://tautulli_user:${POSTGRES_PASSWORD}@db:5432/tautulli_exporter
   
   # Session storage
   REDIS_URL=redis://redis:6379/0
   
   # App settings
   FLASK_ENV=production
   HOST=0.0.0.0
   PORT=5000
   EOF
   ```

4. **Start the application**
   ```bash
   docker-compose up -d
   ```

5. **Access and configure**
   - Open http://localhost:5000 in your browser
   - Login with username: `admin`, password: `admin`
   - You'll be prompted to change the password immediately
   - Go to Configuration and add your Tautulli URL and API key
   - Test the connection and save

That's it! You're ready to export your watch history.

### Getting Your Tautulli API Key

1. Open your Tautulli web interface
2. Go to Settings → Web Interface → API
3. Click "Show API Key" and copy it
4. Your Tautulli URL is usually something like `http://your-server-ip:8181`

## � Troubleshooting

### Common Issues

**Can't connect to Tautulli?**
- Make sure your Tautulli URL includes `http://` and the correct port (usually 8181)
- Verify your API key is correct (copy it fresh from Tautulli settings)
- Check that Tautulli is accessible from your Docker containers

**No users showing up?**
- Test your Tautulli connection in the Configuration page
- Make sure there's actually watch history in Tautulli
- Check the browser's developer console for any errors

**Can't login or forgot password?**
- Reset the database: `docker-compose down -v && docker-compose up -d`
- This will recreate the default admin/admin credentials

**CSV download not working?**
- Check your browser's download settings
- Try a smaller date range or fewer results
- Make sure there's actually data for your selected filters

### Getting Help

If you run into issues:
1. Check the application logs: `docker-compose logs web`
2. Verify all containers are running: `docker-compose ps`
3. Test your Tautulli connection manually in a browser
4. Open an issue on GitHub with details about your setup

## � What Data Gets Exported?

The CSV export includes all the good stuff:

| Field | Description | Example |
|-------|-------------|---------|
| **Date** | When it was watched | 2025-09-22 14:30:15 |
| **User** | Who watched it | John Doe |
| **Title** | What was watched | Breaking Bad - S01E01 |
| **Media Type** | Movie, episode, etc. | episode |
| **Duration** | How long (minutes) | 47 |
| **Percent Complete** | How much was watched | 95% |
| **Status** | Completed or partial | ✅ Completed |

## 🏗️ What's Under the Hood?

- **Backend**: Flask (Python web framework)
- **Database**: PostgreSQL (for storing app data, not your watch history)
- **Cache**: Redis (for sessions)
- **Frontend**: Bootstrap with dark/light mode
- **Container**: Docker for easy deployment

The app doesn't store your watch history - it pulls it fresh from Tautulli each time you export.

## 📄 License

MIT License - use it however you want! Just remember to follow Tautulli's terms of service and your local privacy laws.

## 🙏 Thanks

- **Tautulli team** for making an awesome Plex monitoring tool
- **AI assistants** (GitHub Copilot & Claude) for helping write clean code
- **You** for using this tool to organize your media habits!