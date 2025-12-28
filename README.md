# 🐾 WildGuard AI – Forest Saver

**WildGuard AI** is an anonymous wildlife crime reporting and monitoring system that uses **AI, cyber intelligence, and conversational bots** to combat illegal wildlife trade and forest crimes.

Built during **CUJ Hackathon 2025**, the project focuses on **protecting citizens, enabling anonymous reporting, and assisting forest & law-enforcement authorities with real-time intelligence.**

---

## 🚨 The Problem We Address

Illegal wildlife trade and forest crimes often go unreported due to:

- Fear of retaliation from criminals  
- Lack of awareness about reporting channels  
- Complicated and slow reporting systems  
- No anonymity for citizens  
- Delayed action by authorities  

---

## 💡 Our Solution

**WildGuard AI turns fear into action using AI.**

### 🔐 Key Features
- **100% Anonymous Reporting** – No identity exposure  
- **AI-Powered Message Classification** – Detects suspicious activity  
- **Real-Time Admin Alerts** – Instant notification to authorities  
- **Cross-Platform Access** – Telegram (current), expandable to WhatsApp & Web  
- **Secure Data Storage** – Encrypted evidence handling  

---

## 🧠 System Architecture (High Level)

- **User Layer**: Citizens reporting incidents anonymously  
- **Conversational Layer**: Telegram Bot  
- **AI Layer**: OpenRouter LLM + keyword fallback  
- **Backend**: Python + Flask/FastAPI (extensible)  
- **Database**: MySQL / SQLite  
- **Admin Dashboard**: Case review & monitoring  

---

## 📂 Project Structure
'''
├── app.py # Telegram bot & AI logic
├── requirements.txt # Python dependencies
├── admins.json # Registered admin IDs
├── ui/
│ ├── main.py
│ ├── database.sql
│ ├── templates/
│ │ ├── index.html
│ │ ├── login.html
│ │ └── dashboard.html
│ └── static/
│ ├── assets/
│ │ ├── style.css
│ │ └── script.js
└── README.md
'''


---

## ⚙️ Tech Stack

- **Language**: Python  
- **Bot Framework**: `python-telegram-bot`  
- **AI**: OpenRouter (LLM-based classification)  
- **Database**: MySQL  
- **Frontend**: HTML, CSS, JavaScript  
- **Backend**: Flask / FastAPI (extensible)  

---

## 🚀 How to Run Locally

### 1️⃣ Install dependencies
```bash
pip install -r requirements.txt
2️⃣ Create .env file
BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
ADMIN_REG_SECRET=your_admin_secret


⚠️ Never upload .env to GitHub

3️⃣ Run the bot
python app.py


The bot will start listening for messages on Telegram.

👮 Admin Commands

/start – Start the bot

/register_admin <secret> – Register as admin

/unregister_admin – Remove admin access

/list_admins – View registered admins

Admins receive real-time alerts for suspicious messages.

🌍 Impact Highlights

✅ 100% anonymous citizen protection

✅ 24/7 availability

✅ Faster response for forest authorities

✅ AI-assisted threat detection

🔮 Future Enhancements

WhatsApp & Web integration

In-house AI model training

Predictive crime hotspot mapping

Secure evidence upload (images/videos)

HTTPS inspection & metadata stripping

👥 Team

CyberSpecies

Sehaj Kashyap

Bhumika Koushal

Krishika Gupta

Sandeep Kumar

Event: CUJ Hackathon 2025

📜 License

This project is for educational and research purposes.
License can be added later if required.

“Together, we can stop illegal wildlife trade — one report at a time.” 🐅🌱



