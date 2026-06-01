# NetworkAI - Complete Setup Guide

This is a detailed guide to set up NetworkAI on your Linux server from scratch.

---

## 📋 Prerequisites

- Linux Server (Ubuntu/Debian/CentOS/RHEL)
- Root/sudo access
- Internet connection
- Git installed

---

## 🚀 Step 1: Install Git & Clone Repo

### For Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y git
```

### For CentOS/RHEL:
```bash
sudo yum install -y git
```

### Clone the repository:
```bash
git clone https://github.com/iurix8-sys32/NetworkAI.git
cd NetworkAI
```

---

## 🔥 Step 2: Configure Firewall

### Option A: Automatic (Recommended)

Run the setup script which handles everything:
```bash
chmod +x setup_firewall.sh
sudo ./setup_firewall.sh
```

This will:
- Install dependencies (pip, screen, curl, git)
- Configure firewall for all required ports
- Create start/stop scripts

### Option B: Manual

#### If using UFW (Ubuntu/Debian):
```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 5000/tcp     # AI Dashboard
sudo ufw allow 8080/tcp    # OpenWebUI
sudo ufw allow 11434/tcp   # Ollama API
sudo ufw enable
sudo ufw status
```

#### If using firewalld (CentOS/RHEL/Fedora):
```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=11434/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

#### If using iptables directly:
```bash
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 11434 -j ACCEPT
```

---

## 📦 Step 3: Install Dependencies

### Install Python & pip:
```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install -y python3 python3-pip
```

### Install required packages:
```bash
pip3 install flask requests python-whois cryptography werkzeug
```

### Install screen (for background running):
```bash
# Ubuntu/Debian
sudo apt install -y screen

# CentOS/RHEL
sudo yum install -y screen
```

---

## 🤖 Step 4: Install Ollama (Optional)

Ollama is needed if you want local AI models. Skip this if you only need the dashboard.

### Install Ollama:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Pull a model (takes ~5GB):
```bash
ollama pull llama3.2
```

### Verify Ollama is running:
```bash
ollama list
```

---

## 🎯 Step 5: Start the Dashboard

### Make scripts executable:
```bash
chmod +x start.sh stop.sh setup_firewall.sh
```

### Start in Screen:
```bash
./start.sh
```

You should see:
```
============================================
  NetworkAI - Starting Dashboard
============================================

Press Ctrl+A, then D to detach
Use 'screen -r AI' to reconnect

[✓] NetworkAI started successfully!

Connect with:  screen -r AI
Logs:         tail -f ai.log
```

---

## 🌐 Step 6: Access the Dashboard

Open your browser and go to:
```
http://YOUR_SERVER_IP:5000
```

Find your server IP with:
```bash
hostname -I
```

---

## 🔐 Step 7: Login with PIN

1. On the lock screen, enter your PIN: `251172`
2. If first time, also paste your GitHub token
3. Click "🔓 Unlock"

---

## 📺 Screen Commands Reference

| Command | Description |
|---------|-------------|
| `./start.sh` | Start AI Dashboard in screen session |
| `screen -r AI` | Reconnect to AI session |
| `Ctrl+A, D` | Detach from screen (leave running) |
| `./stop.sh` | Stop the AI Dashboard |
| `screen -ls` | List all screen sessions |
| `tail -f ai.log` | View live logs |

---

## 🔧 Troubleshooting

### Port already in use?
```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill it if needed
sudo kill -9 <PID>
```

### Screen won't start?
```bash
# Check if screen is installed
which screen

# Kill any existing sessions
screen -S AI -X quit

# Try starting manually
screen -dmS AI bash
```

### Python modules missing?
```bash
pip3 install flask requests python-whois cryptography werkzeug
```

### Ollama not responding?
```bash
# Check if Ollama is running
systemctl status ollama 2>/dev/null || ps aux | grep ollama

# Restart Ollama
systemctl restart ollama 2>/dev/null || ollama serve
```

### Check if services are running:
```bash
# Dashboard
curl http://localhost:5000

# Ollama
curl http://localhost:11434/api/tags
```

---

## 📊 Service Ports Summary

| Port | Service | Public Access |
|------|---------|---------------|
| 5000 | AI Dashboard | ✅ Yes |
| 8080 | OpenWebUI | ✅ Yes |
| 11434 | Ollama API | ⚠️ Local only |

---

## 🔒 Security Notes

- Dashboard requires PIN `251172` to unlock
- GitHub token is AES-256 encrypted on disk
- Use only on networks you control
- Consider firewall rules to limit access

---

## 🚀 Quick Commands (One-Liner)

```bash
# Complete setup in one go
git clone https://github.com/iurix8-sys32/NetworkAI.git && cd NetworkAI && chmod +x *.sh && sudo ./setup_firewall.sh && ./start.sh
```

```bash
# Just restart after reboot
cd ~/NetworkAI && ./start.sh
```

```bash
# Check status
screen -r AI
```

---

## 📁 File Structure

```
NetworkAI/
├── dashboard.py       # Main Flask app
├── token_storage.py   # Encrypted token storage
├── api_server.py      # REST API endpoints
├── ai_agent.py        # AI agent CLI
├── security_tools.py  # Security research tools
├── start.sh           # Start in screen
├── stop.sh            # Stop screen
├── setup_firewall.sh  # Firewall setup
├── requirements.txt   # Python dependencies
├── README.md          # Quick overview
├── SETUP.md           # This file
└── templates/
    └── dashboard.html # Web interface
```

---

## ✅ Setup Complete Checklist

- [ ] Repo cloned
- [ ] Firewall configured (ports 5000, 8080, 11434)
- [ ] Dependencies installed
- [ ] Ollama installed (optional)
- [ ] `./start.sh` executed
- [ ] Dashboard accessible at port 5000
- [ ] PIN `251172` working
- [ ] GitHub token connected

---

For issues, check logs: `tail -f ai.log`