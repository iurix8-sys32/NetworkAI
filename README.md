# Local AI Security Lab

A self-hosted AI system with system-level internet access for security research and authorized testing. Features a graphical dashboard showing all AI activity in real-time with PIN-protected GitHub token encryption.

## Features

- **Ollama** - Local LLM inference engine
- **OpenWebUI** - Web interface for AI interaction
- **AI Dashboard** - Graphical interface showing AI activity
- **PIN-Protected Token** - GitHub token encrypted with AES, unlocked via PIN `251172`
- **GitHub Integration** - Full API access to edit, push, pull, and create PRs
- **Full internet access** - Web scraping, API calls, DNS resolution

## Security

```
GitHub Token → AES-256 Encryption → Stored in /tmp/.gh_token.enc
                                      ↓
                              Unlock with PIN: 251172
```

Token is encrypted on disk. Each session requires PIN entry.

## Quick Setup

```bash
chmod +x setup.sh
./setup.sh
pip install -r requirements.txt
python dashboard.py
```

Then open `http://your-server:5000` in your browser.

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