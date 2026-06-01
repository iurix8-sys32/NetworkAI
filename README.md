# NetworkAI - Local AI Security Lab

A self-hosted AI system with system-level internet access for security research and authorized testing. Features a graphical dashboard showing all AI activity in real-time with PIN-protected GitHub token encryption.

## Quick Setup

```bash
# 1. Clone or download this repo
git clone https://github.com/iurix8-sys32/NetworkAI.git
cd NetworkAI

# 2. Run setup (installs dependencies + configures firewall)
chmod +x setup_firewall.sh
sudo ./setup_firewall.sh

# 3. Start in screen
chmod +x start.sh
./start.sh
```

Then access: **http://YOUR_SERVER_IP:5000**

---

## 🔥 Firewall Configuration

### Ports to Open

| Port | Service | URL |
|------|---------|-----|
| **5000** | AI Dashboard | http://YOUR_IP:5000 |
| **8080** | OpenWebUI | http://YOUR_IP:8080 |
| **11434** | Ollama API | localhost only |

### Commands by Firewall Type

#### UFW (Debian/Ubuntu)
```bash
sudo ufw allow 5000/tcp comment 'NetworkAI Dashboard'
sudo ufw allow 8080/tcp comment 'NetworkAI WebUI'
sudo ufw allow 11434/tcp comment 'NetworkAI Ollama'
sudo ufw enable
```

#### firewalld (RHEL/CentOS/Fedora)
```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=11434/tcp
sudo firewall-cmd --reload
```

#### iptables (Generic)
```bash
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 11434 -j ACCEPT
```

---

## 🚀 Usage with Screen

### Start AI Dashboard
```bash
./start.sh
```

### Reconnect to Screen
```bash
screen -r AI
```

### Detach from Screen
```
Press: Ctrl+A then D
```

### Stop AI Dashboard
```bash
./stop.sh
```

### View Logs
```bash
tail -f ai.log
```

---

## Security

```
GitHub Token → AES-256 Encryption → Stored in /tmp/.gh_token.enc
                                      ↓
                              Unlock with PIN: 251172
```

Token is encrypted on disk. Each session requires PIN entry.

## Dashboard Features

| Feature | Description |
|---------|-------------|
| Activity Feed | Real-time log of all AI actions |
| GitHub Control | PIN-locked token, browse repos, edit files |
| File Editor | Edit and save files directly to GitHub |
| Branch/PR | Create branches and pull requests |
| AI Commands | Send commands and see responses |
| Token Lock | Lock/unlock button in header |

## PIN Protection Flow

1. **First time**: Enter GitHub token + PIN `251172` → Token encrypted & stored
2. **Next times**: Just enter PIN `251172` → Token decrypted & unlocked
3. **Lock button**: Returns to lock screen, token remains encrypted

## Services

| Service | Port | URL |
|---------|-----|-----|
| AI Dashboard | 5000 | http://localhost:5000 |
| OpenWebUI | 8080 | http://localhost:8080 |
| Ollama API | 11434 | http://localhost:11434 |

## Security Notice

- This AI has no content filters
- Only use on networks you own/control
- Always maintain proper authorization for security testing
- Comply with applicable laws and regulations

## License

MIT