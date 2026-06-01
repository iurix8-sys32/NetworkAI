#!/usr/bin/env python3
"""
REST API Server for AI Agent Tools
Provides HTTP endpoints for security research tools
"""

from flask import Flask, request, jsonify
import requests
import socket
import whois
import json
from datetime import datetime

app = Flask(__name__)

# ============ DNS & Network Tools ============

@app.route('/api/dns', methods=['GET'])
def dns_lookup():
    """DNS lookup endpoint"""
    domain = request.args.get('domain')
    if not domain:
        return jsonify({"error": "domain parameter required"}), 400
    
    try:
        ip = socket.gethostbyname(domain)
        return jsonify({"domain": domain, "ip": ip, "success": True})
    except Exception as e:
        return jsonify({"domain": domain, "error": str(e), "success": False})

@app.route('/api/whois', methods=['GET'])
def whois_lookup():
    """WHOIS lookup endpoint"""
    domain = request.args.get('domain')
    if not domain:
        return jsonify({"error": "domain parameter required"}), 400
    
    try:
        w = whois.whois(domain)
        return jsonify({
            "domain": domain,
            "registrar": str(w.registrar),
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "name_servers": w.name_servers,
            "success": True
        })
    except Exception as e:
        return jsonify({"domain": domain, "error": str(e), "success": False})

@app.route('/api/headers', methods=['GET'])
def analyze_headers():
    """Analyze HTTP headers for security headers"""
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "url parameter required"}), 400
    
    try:
        resp = requests.head(url, timeout=10)
        headers = dict(resp.headers)
        
        security_headers = [
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection'
        ]
        
        present = {h: headers.get(h, "MISSING") for h in security_headers}
        
        return jsonify({
            "url": url,
            "status_code": resp.status_code,
            "security_headers": present,
            "all_headers": headers,
            "success": True
        })
    except Exception as e:
        return jsonify({"url": url, "error": str(e), "success": False})

# ============ Web Tools ============

@app.route('/api/scrape', methods=['GET', 'POST'])
def scrape():
    """Web scraping endpoint"""
    url = request.json.get('url') if request.method == 'POST' else request.args.get('url')
    if not url:
        return jsonify({"error": "url parameter required"}), 400
    
    try:
        resp = requests.get(url, timeout=10)
        return jsonify({
            "url": url,
            "status_code": resp.status_code,
            "content_length": len(resp.text),
            "content_preview": resp.text[:1000],
            "headers": dict(resp.headers),
            "success": True
        })
    except Exception as e:
        return jsonify({"url": url, "error": str(e), "success": False})

@app.route('/api/search', methods=['GET'])
def web_search():
    """Simple web search via DuckDuckGo"""
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "q (query) parameter required"}), 400
    
    try:
        # Use DuckDuckGo HTML
        resp = requests.get(
            "https://duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        return jsonify({
            "query": query,
            "results_count": resp.text.count('<a class="result__a"'),
            "preview": resp.text[:2000],
            "success": True
        })
    except Exception as e:
        return jsonify({"query": query, "error": str(e), "success": False})

# ============ SSL/TLS Tools ============

@app.route('/api/ssl', methods=['GET'])
def ssl_info():
    """Get SSL certificate info"""
    host = request.args.get('host')
    if not host:
        return jsonify({"error": "host parameter required"}), 400
    
    import subprocess
    try:
        result = subprocess.run(
            ['openssl', 's_client', '-connect', f'{host}:443', '-servername', host],
            input='',
            capture_output=True,
            text=True,
            timeout=10
        )
        
        cert_result = subprocess.run(
            ['openssl', 'x509', '-noout', '-dates', '-subject'],
            input=result.stdout,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return jsonify({
            "host": host,
            "ssl_info": cert_result.stdout,
            "success": True
        })
    except Exception as e:
        return jsonify({"host": host, "error": str(e), "success": False})

# ============ System Tools ============

@app.route('/api/ping', methods=['GET'])
def ping():
    """Ping a host"""
    host = request.args.get('host')
    if not host:
        return jsonify({"error": "host parameter required"}), 400
    
    import subprocess
    try:
        result = subprocess.run(
            ['ping', '-c', '3', host],
            capture_output=True,
            text=True,
            timeout=15
        )
        return jsonify({
            "host": host,
            "reachable": result.returncode == 0,
            "output": result.stdout,
            "success": True
        })
    except Exception as e:
        return jsonify({"host": host, "error": str(e), "success": False})

@app.route('/api/trace', methods=['GET'])
def traceroute():
    """Traceroute to a host"""
    host = request.args.get('host')
    if not host:
        return jsonify({"error": "host parameter required"}), 400
    
    import subprocess
    try:
        result = subprocess.run(
            ['traceroute', host],
            capture_output=True,
            text=True,
            timeout=30
        )
        return jsonify({
            "host": host,
            "route": result.stdout,
            "success": True
        })
    except Exception as e:
        return jsonify({"host": host, "error": str(e), "success": False})

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Security Research API"
    })

if __name__ == '__main__':
    print("Starting Security Research API on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)