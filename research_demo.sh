#!/bin/bash
# Security Research Demo Script
# Demonstrates legitimate security research capabilities

echo "=== Security Research Demo ==="
echo ""

# DNS Lookup
echo "1. DNS Lookup for google.com:"
dig +short google.com
echo ""

# WHOIS
echo "2. WHOIS for google.com:"
whois google.com | head -20
echo ""

# HTTP Headers Analysis
echo "3. HTTP Headers (security check):"
curl -sI https://google.com | grep -iE "(strict-transport|content-security|x-frame|x-content-type)"
echo ""

# SSL Certificate Info
echo "4. SSL Certificate Info:"
echo | openssl s_client -connect google.com:443 -servername google.com 2>/dev/null | openssl x509 -noout -dates -subject 2>/dev/null || echo "SSL check skipped"
echo ""

# Traceroute
echo "5. Traceroute to 8.8.8.8:"
traceroute -m 10 8.8.8.8 2>/dev/null || traceroute 8.8.8.8 2>/dev/null || echo "Traceroute not available"
echo ""

# Web Scraping Demo
echo "6. Web scraping example:"
curl -s "https://httpbin.org/ip" 2>/dev/null || echo "Web request demo"
echo ""

echo "=== Demo Complete ==="
echo "This script demonstrates authorized security research capabilities."