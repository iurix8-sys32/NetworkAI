#!/usr/bin/env python3
"""
Simple AI Agent with Web Access
Powered by Ollama - for authorized security research
"""

import requests
import json
import sys

OLLAMA_URL = "http://localhost:11434"
WEB_UI_URL = "http://localhost:8080"

class LocalAIAgent:
    """AI Agent with system-level internet access"""
    
    def __init__(self, model="llama3.2"):
        self.model = model
        self.system_prompt = """You are a helpful AI assistant with full internet access.
You can help with:
- Web research and data gathering
- Code development and review
- Security analysis of public information
- DNS and network research
- Technical documentation

Always maintain ethical boundaries and proper authorization for security testing."""
    
    def chat(self, message):
        """Send message to local Ollama"""
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": message}
                    ],
                    "stream": False
                },
                timeout=120
            )
            return response.json().get("message", {}).get("content", "No response")
        except Exception as e:
            return f"Error: {e}"
    
    def web_scrape(self, url):
        """Scrape web content"""
        try:
            resp = requests.get(url, timeout=10)
            return {
                "status": resp.status_code,
                "content": resp.text[:2000],  # Limit output
                "headers": dict(resp.headers)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def dns_lookup(self, domain):
        """DNS resolution"""
        import socket
        try:
            ip = socket.gethostbyname(domain)
            return {"domain": domain, "ip": ip, "success": True}
        except Exception as e:
            return {"domain": domain, "error": str(e), "success": False}
    
    def whois_query(self, domain):
        """WHOIS lookup"""
        try:
            import whois
            w = whois.whois(domain)
            return {
                "domain": domain,
                "registrar": w.registrar,
                "creation_date": str(w.creation_date),
                "success": True
            }
        except Exception as e:
            return {"domain": domain, "error": str(e), "success": False}


def main():
    agent = LocalAIAgent()
    
    print("=== Local AI Security Agent ===")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['quit', 'exit']:
                break
            
            print("\nAI: ", end="")
            response = agent.chat(user_input)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()