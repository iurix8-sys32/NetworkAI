# Local AI Security Lab

A self-hosted AI system with system-level internet access for security research and authorized testing. Features a graphical dashboard showing all AI activity in real-time.

## Features

- **Ollama** - Local LLM inference engine
- **OpenWebUI** - Web interface for AI interaction
- **AI Dashboard** - Graphical interface showing AI activity
- **GitHub Integration** - Full API access to edit, push, pull, and create PRs
- **Full internet access** - Web scraping, API calls, DNS resolution

## Quick Setup

```bash
chmod +x setup.sh
./setup.sh
python dashboard.py
```

Then open `http://your-server:5000` in your browser.

## Dashboard Features

| Feature | Description |
|---------|-------------|
| Activity Feed | Real-time log of all AI actions |
| GitHub Control | Connect with token, browse repos, edit files |
| File Editor | Edit and save files directly to GitHub |
| Branch/PR | Create branches and pull requests |
| AI Commands | Send commands and see responses |

## GitHub Token Setup

1. Enter your GitHub token in the dashboard header
2. Click "Connect" to authenticate
3. Token is saved locally in your browser

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