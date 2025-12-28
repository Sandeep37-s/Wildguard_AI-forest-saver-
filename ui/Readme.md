# 🛡️ Police Security Bot - Complete Setup Guide

A professional AI-powered Telegram security bot with a beautiful web dashboard for monitoring suspicious messages.

## 📁 File Structure

```
C:/xampp/htdocs/security-bot/
├── index.html          # Homepage with day/night animation
├── login.html          # Admin login page
├── dashboard.html      # Main admin dashboard
├── api.php            # Backend API
└── database.sql       # Database setup script
```

## 🚀 Quick Setup

### Step 1: Install XAMPP

1. Download XAMPP from [https://www.apachefriends.org](https://www.apachefriends.org)
2. Install XAMPP to `C:/xampp/`
3. Start **Apache** and **MySQL** from XAMPP Control Panel

### Step 2: Setup Database

1. Open phpMyAdmin: [http://localhost/phpmyadmin](http://localhost/phpmyadmin)
2. Click "Import" tab
3. Choose `database.sql` file
4. Click "Go" to create database and tables

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

### Step 3: Copy Website Files

1. Create folder: `C:/xampp/htdocs/security-bot/`
2. Place all HTML and PHP files in this folder
3. Your website is now at: [http://localhost/security-bot/](http://localhost/security-bot/)

### Step 4: Setup Telegram Bot

1. Install Python packages:
```bash
pip install python-telegram-bot requests python-dotenv mysql-connector-python
```

2. Add the database integration code to your bot:
```python
# At the top of your bot file
from bot_integration import save_message_to_db

# Inside handle_message function, after classification
save_message_to_db(
    text=text,
    sender=sender_id,
    score=score,
    reasons=reasons,
    label=label
)
```

3. Run your bot:
```bash
python your_bot.py
```

## 🌐 Access the Dashboard

1. **Homepage**: [http://localhost/security-bot/index.html](http://localhost/security-bot/index.html)
   - Beautiful landing page with day/night transition
   - Scroll down to watch sunset and stars appear
   - See features, how it works, and meet the team

2. **Login**: [http://localhost/security-bot/login.html](http://localhost/security-bot/login.html)
   - Login with: `admin` / `admin123`
   - Beautiful animated gradient background

3. **Dashboard**: [http://localhost/security-bot/dashboard.html](http://localhost/security-bot/dashboard.html)
   - Real-time message monitoring
   - Live statistics and charts
   - Privacy controls (toggle identity masking)
   - Auto-refreshes every 5 seconds

## 🎨 Features

### Homepage
- ☀️ **Day/Night Animation**: Smooth transition as you scroll
- 🌲 **Forest Scene**: Beautiful layered trees
- 🌟 **Twinkling Stars**: Appear during night
- ⭐ **Feature Cards**: Highlight key capabilities
- 👥 **Team Section**: Showcase creators

### Login Page
- 🌈 **Animated Gradient Background**
- 🔒 **Secure Authentication**
- 💎 **Glass Morphism Design**
- 📱 **Social Login Options** (UI ready)

### Dashboard
- 📊 **Live Statistics**: Total, suspicious, safe messages
- 📈 **Activity Charts**: Weekly overview
- 🥧 **Threat Distribution**: Visual pie chart
- 🔴 **Real-time Alerts**: Pulsing notifications
- 👁️ **Identity Protection**: Toggle visibility
- 🎨 **Glassmorphism UI**: Modern, elegant design
- ⚡ **Auto-refresh**: Updates every 5 seconds

## 🔧 Configuration

### Database Connection (api.php)
```php
$host = 'localhost';
$dbname = 'security_bot';
$username = 'root';
$password = ''; // Add password if needed
```

### Bot Database Connection (bot_integration.py)
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'security_bot'
}
```

## 📊 Database Schema

### `messages` table
- `id`: Auto-increment primary key
- `text`: Message content
- `sender`: User ID (masked in dashboard)
- `timestamp`: When message was received
- `score`: Threat score (0.0 - 1.0)
- `reasons`: JSON array of detection reasons
- `label`: 'suspicious' or 'safe'

### `admins` table
- `id`: Auto-increment primary key
- `username`: Admin username
- `password`: Hashed password
- `email`: Admin email

## 🔐 Security Features

1. **User Privacy**
   - IDs masked by default: `•••••1234`
   - Only admins can toggle full visibility

2. **Secure Authentication**
   - Passwords hashed with bcrypt
   - Session management
   - Protected dashboard access

3. **CORS Protection**
   - Controlled API access
   - Same-origin policy

## 🎯 Usage

### For Public Users
1. Send messages in Telegram group
2. Bot analyzes each message
3. Receive confirmation
4. Suspicious messages flagged to admins

### For Admins
1. Login to dashboard
2. View real-time statistics
3. Monitor suspicious messages
4. Review threat analysis
5. Toggle identity visibility when needed

## 🐛 Troubleshooting

### "Database connection failed"
- Ensure MySQL is running in XAMPP
- Check database exists: `security_bot`
- Verify credentials in `api.php`

### "No messages appearing"
- Confirm bot is running
- Check bot has database integration code
- Verify messages are being saved to DB
- Check browser console for errors

### "Login not working"
- Default credentials: `admin` / `admin123`
- Check `admins` table has data
- Clear browser cache/sessionStorage

## 🎨 Customization

### Change Admin Credentials
```sql
UPDATE admins 
SET password = '$2y$10$YOUR_NEW_HASH' 
WHERE username = 'admin';
```

Generate hash in PHP:
```php
echo password_hash('your_password', PASSWORD_DEFAULT);
```

### Customize Theme Colors
Edit dashboard.html:
- Blue: `bg-blue-600` → `bg-purple-600`
- Adjust gradient in login.html
- Modify glass effects: `bg-white/10`

### Add Team Members
Edit index.html team section:
- Change names and roles
- Update gradient colors
- Add profile images

## 📞 Support

For issues or questions:
1. Check XAMPP logs: `C:/xampp/mysql/data/mysql_error.log`
2. Check browser console: F12 → Console tab
3. Verify file permissions
4. Ensure ports 80 and 3306 are free

## 📝 Notes

- Default port: 80 (Apache)
- Default MySQL port: 3306
- Auto-refresh interval: 5 seconds
- Message history limit: 50 messages
- Session timeout: Browser close

## 🚀 Production Deployment

For live deployment:
1. Change database credentials
2. Add SSL certificate
3. Update API URLs in HTML files
4. Set secure session handling
5. Enable HTTPS-only cookies
6. Add rate limiting
7. Configure firewall rules

---

**Created with ❤️ for secure Telegram communities**

🌟 **Star this project if you find it useful!**