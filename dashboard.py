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

@app.route('/api/status')
def status():
    """System status"""
    user = None
    token = request.headers.get('X-GitHub-Token')
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
        "token_set": bool(token)
    })

@app.route('/api/activity')
def activity():
    """Get activity log"""
    return jsonify(activity_log)

@app.route('/api/github/repos')
def list_repos():
    """List user repos"""
    token = request.headers.get('X-GitHub-Token') or request.args.get('token', '')
    if not token:
        return jsonify({"error": "No token provided"})
    
    client = get_github_client(token)
    try:
        repos = client.list_repos()
        return jsonify(repos)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/github/repo/<owner>/<repo>')
def repo_info(owner, repo):
    """Get repo info"""
    token = request.headers.get('X-GitHub-Token') or request.args.get('token', '')
    if not token:
        return jsonify({"error": "No token provided"})
    
    client = get_github_client(token)
    try:
        info = client.get_repo(owner, repo)
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/github/repo/<owner>/<repo>/contents')
def repo_contents(owner, repo):
    """List repo contents"""
    token = request.headers.get('X-GitHub-Token') or request.args.get('token', '')
    if not token:
        return jsonify({"error": "No token provided"})
    
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
    token = request.headers.get('X-GitHub-Token') or request.args.get('token', '')
    if not token:
        return jsonify({"error": "No token provided"})
    
    client = get_github_client(token)
    try:
        file_data = client.get_file(owner, repo, path)
        return jsonify(file_data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/github/edit', methods=['POST'])
def edit_file():
    """Create or update a file"""
    data = request.json
    token = data.get('token') or request.headers.get('X-GitHub-Token')
    if not token:
        return jsonify({"error": "No token provided"})
    
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
    data = request.json
    token = data.get('token') or request.headers.get('X-GitHub-Token')
    if not token:
        return jsonify({"error": "No token provided"})
    
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
    data = request.json
    token = data.get('token') or request.headers.get('X-GitHub-Token')
    if not token:
        return jsonify({"error": "No token provided"})
    
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
    data = request.json
    token = data.get('token') or request.headers.get('X-GitHub-Token')
    if not token:
        return jsonify({"error": "No token provided"})
    
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
    data = request.json
    token = data.get('token') or request.headers.get('X-GitHub-Token')
    if not token:
        return jsonify({"error": "No token provided"})
    
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
    
    # Simulate AI processing
    response = simulate_ai_action(command)
    
    return jsonify(response)

def simulate_ai_action(command):
    """Simulate AI action based on command"""
    command_lower = command.lower()
    
    if 'clone' in command_lower or 'pull' in command_lower:
        log_activity("github", "Git Clone/Pull", command)
        return {"status": "success", "action": "pull", "message": "Pulled latest changes"}
    
    elif 'push' in command_lower or 'commit' in command_lower:
        log_activity("github", "Git Push/Commit", command)
        return {"status": "success", "action": "push", "message": "Pushed changes to repository"}
    
    elif 'search' in command_lower or 'find' in command_lower:
        log_activity("search", "Web Search", command)
        return {"status": "success", "action": "search", "message": "Search completed"}
    
    elif 'scrape' in command_lower or 'fetch' in command_lower:
        log_activity("web", "Web Scrape", command)
        return {"status": "success", "action": "scrape", "message": "Web content scraped"}
    
    elif 'code' in command_lower or 'write' in command_lower:
        log_activity("code", "Code Generation", command)
        return {"status": "success", "action": "code", "message": "Code generated successfully"}
    
    else:
        log_activity("ai", "General AI Task", command)
        return {"status": "success", "action": "general", "message": "Task completed"}

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