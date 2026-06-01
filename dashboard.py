#!/usr/bin/env python3
"""
AI Agent Dashboard - Graphical Interface
Shows AI activity, actions, and GitHub operations in real-time
"""

import os
import json
import base64
import subprocess
import requests
from datetime import datetime
from flask import Flask, render_template, jsonify, request, Response
from threading import Thread, Lock
import time

app = Flask(__name__)

# Configuration - Token will be set at runtime
GITHUB_TOKEN = ""
LOG_FILE = '/tmp/ai_activity.log'

# Activity log
activity_log = []
log_lock = Lock()

def log_activity(action_type, title, details=""):
    """Log AI activity"""
    with log_lock:
        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": action_type,
            "title": title,
            "details": details
        }
        activity_log.insert(0, entry)
        if len(activity_log) > 100:
            activity_log.pop()

# GitHub API wrapper
class GitHubClient:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_user(self):
        resp = requests.get("https://api.github.com/user", headers=self.headers)
        return resp.json()
    
    def list_repos(self):
        resp = requests.get("https://api.github.com/user/repos", headers=self.headers)
        return resp.json()
    
    def get_repo(self, owner, repo):
        resp = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=self.headers)
        return resp.json()
    
    def list_contents(self, owner, repo, path=""):
        resp = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=self.headers)
        return resp.json()
    
    def get_file(self, owner, repo, path):
        resp = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=self.headers)
        return resp.json()
    
    def create_or_update_file(self, owner, repo, path, content, message, sha=None):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        data = {
            "message": message,
            "content": content
        }
        if sha:
            data["sha"] = sha
        resp = requests.put(url, headers=self.headers, json=data)
        return resp.json()
    
    def create_branch(self, owner, repo, branch, from_branch="main"):
        # Get SHA of main
        ref_resp = requests.get(f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{from_branch}", headers=self.headers)
        if ref_resp.status_code != 200:
            # Try master
            ref_resp = requests.get(f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/master", headers=self.headers)
        
        if ref_resp.status_code != 200:
            return {"error": "Could not find base branch"}
        
        sha = ref_resp.json()["object"]["sha"]
        
        data = {
            "ref": f"refs/heads/{branch}",
            "sha": sha
        }
        resp = requests.post(f"https://api.github.com/repos/{owner}/{repo}/git/refs", headers=self.headers, json=data)
        return resp.json()
    
    def create_pull_request(self, owner, repo, title, body, head, base="main"):
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        resp = requests.post(f"https://api.github.com/repos/{owner}/{repo}/pulls", headers=self.headers, json=data)
        return resp.json()
    
    def list_branches(self, owner, repo):
        resp = requests.get(f"https://api.github.com/repos/{owner}/{repo}/branches", headers=self.headers)
        return resp.json()
    
    def commit_changes(self, owner, repo, message, files):
        """Commit multiple file changes"""
        results = []
        for path, content in files.items():
            result = self.create_or_update_file(owner, repo, path, content, message)
            results.append({"path": path, "result": result})
            log_activity("github", f"Updated {path}", f"Repo: {owner}/{repo}")
        return results

# Initialize GitHub client (token will be set from frontend)
github = None

def get_github_client(token):
    return GitHubClient(token)

# Routes
@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/init', methods=['POST'])
def init_token():
    """Initialize/verify token with PIN"""
    data = request.json
    pin = data.get('pin', '')
    
    if pin != "251172":
        return jsonify({"error": "Invalid PIN"})
    
    # Store token encrypted
    token = data.get('token', '')
    if token:
        import token_storage
        token_storage.store_token(token)
        log_activity("system", "Token encrypted & stored", "PIN verified")
        return jsonify({"status": "success", "message": "Token stored securely"})
    
    return jsonify({"error": "No token provided"})

@app.route('/api/unlock', methods=['POST'])
def unlock_token():
    """Unlock token with PIN"""
    data = request.json
    pin = data.get('pin', '')
    
    if pin != "251172":
        return jsonify({"error": "Invalid PIN"})
    
    import token_storage
    token = token_storage.get_token()
    
    if token:
        log_activity("system", "Token unlocked", "Session started")
        return jsonify({"status": "success", "token": token})
    
    return jsonify({"error": "No token stored"})

@app.route('/api/status')
def status():
    """System status"""
    user = None
    import token_storage
    token = token_storage.get_token()
    
    if token:
        client = get_github_client(token)
        try:
            user = client.get_user()
        except:
            pass
    
    return jsonify({
        "github_connected": user is not None,
        "github_user": user.get("login") if user else None,
        "activity_count": len(activity_log),
        "token_stored": token_storage.is_token_stored(),
        "token_unlocked": bool(token)
    })

@app.route('/api/activity')
def activity():
    """Get activity log"""
    return jsonify(activity_log)

@app.route('/api/github/repos')
def list_repos():
    """List user repos"""
    import token_storage
    token = token_storage.get_token()
    if not token:
        return jsonify({"error": "Token locked. Enter PIN to unlock."})
    
    client = get_github_client(token)
    try:
        repos = client.list_repos()
        return jsonify(repos)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/github/repo/<owner>/<repo>')
def repo_info(owner, repo):
    """Get repo info"""
    import token_storage
    token = token_storage.get_token()
    if not token:
        return jsonify({"error": "Token locked. Enter PIN to unlock."})
    
    client = get_github_client(token)
    try:
        info = client.get_repo(owner, repo)
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/github/repo/<owner>/<repo>/contents')
def repo_contents(owner, repo):
    """List repo contents"""
    import token_storage
    token = token_storage.get_token()
    if not token:
        return jsonify({"error": "Token locked. Enter PIN to unlock."})
    
    path = request.args.get('path', '')
    client = get_github_client(token)
    try:
        contents = client.list_contents(owner, repo, path)
        return jsonify(contents)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/github/file/<owner>/<repo>/<path:path>')
def get_file(owner, repo, path):
    """Get file contents"""
    import token_storage
    token = token_storage.get_token()
    if not token:
        return jsonify({"error": "Token locked. Enter PIN to unlock."})
    
    client = get_github_client(token)
    try:
        file_data = client.get_file(owner, repo, path)
        return jsonify(file_data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/github/edit', methods=['POST'])
def edit_file():
    """Create or update a file"""
    import token_storage
    token = token_storage.get_token()
    if not token:
        return jsonify({"error": "Token locked. Enter PIN to unlock."})
    
    data = request.json
    client = get_github_client(token)
    try:
        result = client.create_or_update_file(
            data['owner'],
            data['repo'],
            data['path'],
            data['content'],
            data['message']
        )
        log_activity("github_edit", f"Edited {data['path']}", 
                     f"Repo: {data['owner']}/{data['repo']}")
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/github/branch', methods=['POST'])
def create_branch():
    """Create a branch"""
    import token_storage
    token = token_storage.get_token()
    if not token:
        return jsonify({"error": "Token locked. Enter PIN to unlock."})
    
    data = request.json
    client = get_github_client(token)
    try:
        result = client.create_branch(
            data['owner'],
            data['repo'],
            data['branch'],
            data.get('base', 'main')
        )
        log_activity("github", f"Created branch: {data['branch']}",
                     f"Repo: {data['owner']}/{data['repo']}")
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/github/pr', methods=['POST'])
def create_pr():
    """Create a pull request"""
    import token_storage
    token = token_storage.get_token()
    if not token:
        return jsonify({"error": "Token locked. Enter PIN to unlock."})
    
    data = request.json
    client = get_github_client(token)
    try:
        result = client.create_pull_request(
            data['owner'],
            data['repo'],
            data['title'],
            data.get('body', ''),
            data['head'],
            data.get('base', 'main')
        )
        log_activity("github_pr", f"Created PR: {data['title']}",
                     f"Repo: {data['owner']}/{data['repo']}")
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/github/clone', methods=['POST'])
def clone_repo():
    """Clone a repository"""
    import token_storage
    token = token_storage.get_token()
    if not token:
        return jsonify({"error": "Token locked. Enter PIN to unlock."})
    
    data = request.json
    owner = data.get('owner')
    repo = data.get('repo')
    clone_path = data.get('path', f'/tmp/{repo}')
    
    log_activity("github", f"Cloning {owner}/{repo}", clone_path)
    
    try:
        # Using git with token
        clone_url = f"https://{token}@github.com/{owner}/{repo}.git"
        result = subprocess.run(
            ['git', 'clone', clone_url, clone_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            log_activity("github", f"Cloned {repo}", f"Path: {clone_path}")
            return jsonify({"status": "success", "path": clone_path})
        else:
            return jsonify({"status": "error", "message": result.stderr})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/github/push', methods=['POST'])
def push_changes():
    """Push changes to repo"""
    import token_storage
    token = token_storage.get_token()
    if not token:
        return jsonify({"error": "Token locked. Enter PIN to unlock."})
    
    data = request.json
    owner = data.get('owner')
    repo = data.get('repo')
    branch = data.get('branch', 'main')
    commit_message = data.get('message', 'AI update')
    files = data.get('files', {})  # {path: content}
    
    try:
        clone_path = f"/tmp/{repo}"
        
        # Clone if not exists
        if not os.path.exists(clone_path):
            clone_url = f"https://{token}@github.com/{owner}/{repo}.git"
            subprocess.run(['git', 'clone', clone_url, clone_path], capture_output=True)
        
        os.chdir(clone_path)
        
        # Configure git
        user_info = get_github_client(token).get_user()
        subprocess.run(['git', 'config', 'user.email', 'ai@local'], capture_output=True)
        subprocess.run(['git', 'config', 'user.name', user_info.get('login', 'AI Agent')], capture_output=True)
        
        # Write files
        for path, content in files.items():
            file_path = os.path.join(clone_path, path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
        
        # Commit and push
        subprocess.run(['git', 'add', '.'], capture_output=True)
        subprocess.run(['git', 'commit', '-m', commit_message], capture_output=True)
        
        result = subprocess.run(
            ['git', 'push', 'origin', branch],
            capture_output=True,
            text=True,
            env={**os.environ, 'GIT_TOKEN': token}
        )
        
        if result.returncode == 0:
            log_activity("github", f"Pushed changes to {branch}", commit_message)
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": result.stderr})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/ai/command', methods=['POST'])
def ai_command():
    """Execute AI command"""
    data = request.json
    command = data.get('command', '')
    
    log_activity("ai_command", f"AI Command: {command[:50]}...", command)
    
    # Try Ollama first
    try:
        import token_storage
        token = token_storage.get_token()
        if token:
            # Get user info for context
            client = get_github_client(token)
            user = client.get_user()
            username = user.get('login', 'User')
        else:
            username = 'User'
    except:
        username = 'User'
    
    # Call Ollama for actual AI response
    try:
        import requests as req
        ollama_resp = req.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2',
                'prompt': f"You are NetworkAI assistant for {username}. Respond to: {command}",
                'stream': False
            },
            timeout=60
        )
        
        if ollama_resp.status_code == 200:
            result = ollama_resp.json()
            ai_response = result.get('response', 'No response')
            log_activity("ai_response", f"Response generated", ai_response[:100])
            return jsonify({
                "status": "success",
                "action": "ai_response",
                "message": ai_response
            })
    except Exception as e:
        pass
    
    # Fallback simulation
    response = simulate_ai_action(command)
    return jsonify(response)

def simulate_ai_action(command):
    """Simulate AI action based on command - fallback when no Ollama"""
    command_lower = command.lower()
    
    # If Ollama is not running, give helpful responses
    responses = {
        "search": {
            "status": "success",
            "action": "search",
            "message": "Web search ready. To enable AI responses, install Ollama: curl -fsSL https://ollama.com/install.sh | sh\n\nFor now, use the GitHub panel to:\n- Browse repositories\n- Edit files\n- Create branches/PRs\n- Clone repos"
        },
        "scrape": {
            "status": "success",
            "action": "scrape",
            "message": "Web scraping ready. Use the API endpoints:\n- /api/dns?domain=example.com\n- /api/whois?domain=example.com\n- /api/headers?url=https://example.com\n- /api/scrape?url=https://example.com"
        },
        "clone": {
            "status": "success",
            "action": "clone",
            "message": "Git clone ready. Use the GitHub panel to:\n1. Enter owner and repo name\n2. Click Load Repos\n3. Select a repo to work with"
        },
        "push": {
            "status": "success",
            "action": "push",
            "message": "Git push ready. Use the File Editor tab to:\n1. Enter owner/repo/path\n2. Write your code\n3. Add commit message\n4. Save to GitHub"
        },
        "code": {
            "status": "success",
            "action": "code",
            "message": "Code generation ready. To enable AI coding:\n1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh\n2. Run: ollama pull codellama\n3. Restart dashboard\n\nThen I can write and edit code for you!"
        },
        "help": {
            "status": "success",
            "action": "help",
            "message": "NetworkAI Commands:\n\n📂 GitHub:\n- Clone repositories\n- Edit files\n- Create branches & PRs\n- Push changes\n\n🌐 Web:\n- DNS lookup\n- WHOIS search\n- Header analysis\n- Web scraping\n\n💬 Chat with me after installing Ollama!\n\nTo install Ollama:\ncurl -fsSL https://ollama.com/install.sh | sh\nollama pull llama3.2"
        }
    }
    
    # Check for keywords
    if any(word in command_lower for word in ['search', 'find', 'look']):
        return responses['search']
    elif any(word in command_lower for word in ['scrape', 'fetch', 'get']):
        return responses['scrape']
    elif any(word in command_lower for word in ['clone', 'download']):
        return responses['clone']
    elif any(word in command_lower for word in ['push', 'upload', 'commit']):
        return responses['push']
    elif any(word in command_lower for word in ['code', 'write', 'script', 'python']):
        return responses['code']
    elif any(word in command_lower for word in ['help', '?' , 'commands', 'what']):
        return responses['help']
    
    # Default helpful response
    return {
        "status": "success",
        "action": "general",
        "message": f"I received: '{command[:100]}...'\n\nTo enable full AI responses, install Ollama:\n\n1. curl -fsSL https://ollama.com/install.sh | sh\n2. ollama pull llama3.2\n3. Restart: ./stop.sh && ./start.sh\n\nWithout Ollama, you can still use:\n- GitHub panel (repos, files, branches, PRs)\n- DNS/WHOIS lookups\n- Web scraping via API"
    }

@app.route('/api/log', methods=['POST'])
def log_event():
    """Manually log an event"""
    data = request.json
    log_activity(data.get('type', 'info'), data.get('title', ''), data.get('details', ''))
    return jsonify({"status": "ok"})

# Stream updates
@app.route('/api/stream')
def stream():
    def generate():
        last_count = 0
        while True:
            with log_lock:
                current_count = len(activity_log)
            
            if current_count != last_count:
                yield f"data: {json.dumps({'count': current_count})}\n\n"
                last_count = current_count
            
            time.sleep(0.5)
    
    return Response(generate(), mimetype='text/event-stream')

# Serve templates
@app.route('/template/<name>')
def serve_template(name):
    return render_template(name)

if __name__ == '__main__':
    print("=" * 50)
    print("AI Agent Dashboard")
    print("=" * 50)
    print(f"GitHub Token: {'Set' if GITHUB_TOKEN else 'Not Set'}")
    print("Running on: http://0.0.0.0:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)