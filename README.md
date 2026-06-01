# Local AI Security Lab

A self-hosted AI system with system-level internet access for security research and authorized testing.

## Features

- **Ollama** - Local LLM inference engine
- **OpenWebUI** - Web interface for AI interaction
- **Full internet access** - Web scraping, API calls, DNS resolution
- **Tool access** - curl, wget, python requests, and more

## Quick Setup

```bash
chmod +x setup.sh
./setup.sh
```

## Services

| Service | Port | URL |
|---------|-----|-----|
| OpenWebUI | 8080 | http://localhost:8080 |
| Ollama API | 11434 | http://localhost:11434 |

## Usage

1. Access OpenWebUI at `http://your-server:8080`
2. Download a model (e.g., llama3.2, codellama)
3. Interact with the AI

## Security Notice

- This AI has no content filters
- Only use on networks you own/control
- Always maintain proper authorization for security testing
- Comply with applicable laws and regulations

## Model Recommendations

For security work:
- `llama3.2` - General purpose
- `codellama` - Code generation
- `mistral` - Balanced performance

## License

MIT