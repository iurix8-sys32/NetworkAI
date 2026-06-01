#!/usr/bin/env python3
"""
AI Agent with Web Access - Security Research Tool
For authorized testing only
"""

import subprocess
import requests
import socket
import whois
from datetime import datetime

class SecurityResearcher:
    """AI-assisted security research tools"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SecurityResearcher/1.0'
        })
    
    # DNS lookup
    def dns_lookup(self, domain):
        try:
            ip = socket.gethostbyname(domain)
            return {"domain": domain, "ip": ip, "success": True}
        except socket.gaierror as e:
            return {"domain": domain, "error": str(e), "success": False}
    
    # WHOIS lookup
    def whois_lookup(self, domain):
        try:
            w = whois.whois(domain)
            return {
                "domain": domain,
                "registrar": w.registrar,
                "creation_date": w.creation_date,
                "expiration_date": w.expiration_date,
                "name_servers": w.name_servers,
                "success": True
            }
        except Exception as e:
            return {"domain": domain, "error": str(e), "success": False}
    
    # Web scraping
    def scrape_url(self, url):
        try:
            response = self.session.get(url, timeout=10)
            return {
                "url": url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content_length": len(response.text),
                "success": True
            }
        except Exception as e:
            return {"url": url, "error": str(e), "success": False}
    
    # HTTP headers analysis
    def analyze_headers(self, url):
        try:
            response = self.session.head(url, timeout=10)
            headers = dict(response.headers)
            analysis = {
                "security_headers": {},
                "recommendations": []
            }
            
            # Check for security headers
            security_headers = [
                'Strict-Transport-Security',
                'Content-Security-Policy',
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection'
            ]
            
            for header in security_headers:
                if header in headers:
                    analysis["security_headers"][header] = headers[header]
                else:
                    analysis["recommendations"].append(f"Missing {header}")
            
            return {"url": url, "headers": headers, "analysis": analysis, "success": True}
        except Exception as e:
            return {"url": url, "error": str(e), "success": False}
    
    # Subdomain enumeration via DNS
    def enumerate_subdomains(self, domain):
        common_subdomains = [
            'www', 'mail', 'ftp', 'admin', 'blog', 'dev',
            'test', 'api', 'staging', 'beta', 'secure'
        ]
        results = []
        for sub in common_subdomains:
            fqdn = f"{sub}.{domain}"
            result = self.dns_lookup(fqdn)
            if result.get("success"):
                results.append(result)
        return results
    
    # Ping check
    def ping_check(self, host):
        try:
            result = subprocess.run(
                ['ping', '-c', '3', host],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                "host": host,
                "success": result.returncode == 0,
                "output": result.stdout
            }
        except Exception as e:
            return {"host": host, "error": str(e), "success": False}
    
    # Traceroute
    def traceroute(self, host):
        try:
            result = subprocess.run(
                ['traceroute', host],
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "host": host,
                "success": result.returncode == 0,
                "route": result.stdout
            }
        except Exception as e:
            return {"host": host, "error": str(e), "success": False}


def main():
    researcher = SecurityResearcher()
    
    # Example usage
    print("=== Security Research Tools ===\n")
    
    # DNS lookup
    domain = input("Enter domain to research (or 'quit'): ")
    if domain and domain != 'quit':
        print("\nDNS Lookup:")
        print(researcher.dns_lookup(domain))
        
        print("\nWHOIS Lookup:")
        print(researcher.whois_lookup(domain))
        
        print("\nHeader Analysis:")
        print(researcher.analyze_headers(f"http://{domain}"))


if __name__ == "__main__":
    main()