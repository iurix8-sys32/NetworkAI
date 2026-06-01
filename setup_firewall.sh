#!/bin/bash
# NetworkAI - AI Dashboard Setup Script
# For authorized security research only

set -e

echo "============================================"
echo "  NetworkAI - Setup & Firewall Configuration"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}[ERROR] Please run as root or with sudo${NC}"
   exit 1
fi

# Detect OS
if [[ -f /etc/debian_version ]]; then
    OS="debian"
elif [[ -f /etc/redhat-release ]]; then
    OS="redhat"
elif [[ -f /etc/arch-release ]]; then
    OS="arch"
else
    OS="unknown"
fi

echo -e "${GREEN}[*] Detected OS: $OS${NC}"

# ============ FIREWALL CONFIGURATION ============
echo ""
echo -e "${YELLOW}[*] Configuring Firewall...${NC}"

# Ports to open
PORTS=(5000 8080 11434)

# Check if ufw is available (Debian/Ubuntu)
if command -v ufw &> /dev/null; then
    echo -e "${GREEN}[+] Using UFW firewall${NC}"
    
    for PORT in "${PORTS[@]}"; do
        echo "  Opening port $PORT/tcp..."
        ufw allow $PORT/tcp comment "NetworkAI" 2>/dev/null || true
    done
    
    # Enable UFW if not active
    if ! ufw status | grep -q "Status: active"; then
        echo -e "${YELLOW}[!] Enabling UFW...${NC}"
        echo "y" | ufw enable 2>/dev/null || true
    fi

# Check if firewalld is available (RHEL/CentOS/Fedora)
elif command -v firewall-cmd &> /dev/null; then
    echo -e "${GREEN}[+] Using firewalld${NC}"
    
    for PORT in "${PORTS[@]}"; do
        echo "  Opening port $PORT/tcp..."
        firewall-cmd --permanent --add-port=$PORT/tcp 2>/dev/null || true
    done
    
    firewall-cmd --reload 2>/dev/null || true

# Check if iptables is available
elif command -v iptables &> /dev/null; then
    echo -e "${GREEN}[+] Using iptables${NC}"
    
    for PORT in "${PORTS[@]}"; do
        echo "  Opening port $PORT/tcp..."
        iptables -A INPUT -p tcp --dport $PORT -j ACCEPT 2>/dev/null || true
    done
    
    # Save rules (Debian)
    if [[ -f /etc/debian_version ]]; then
        iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
    fi

else
    echo -e "${RED}[!] No firewall tool found. Please configure manually.${NC}"
fi

echo -e "${GREEN}[+] Firewall configured!${NC}"

# ============ DEPENDENCIES ============
echo ""
echo -e "${YELLOW}[*] Installing dependencies...${NC}"

# Update system
if [[ "$OS" == "debian" ]]; then
    apt update -qq
    apt upgrade -y -qq
    apt install -y -qq python3-pip python3-venv curl git screen
elif [[ "$OS" == "redhat" ]]; then
    yum update -y -q
    yum install -y -q python3-pip curl git screen
fi

# Install Python packages
pip3 install -q flask requests python-whois cryptography werkzeug

echo -e "${GREEN}[+] Dependencies installed!${NC}"

# ============ INSTALL OLLAMA (Optional) ============
echo ""
echo -e "${YELLOW}[*] Install Ollama? (y/n)${NC}"
read -r -p "This downloads ~5GB of AI models: " response
if [[ "$response" =~ ^[Yy]$ ]]; then
    curl -fsSL https://ollama.com/install.sh | sh
    echo -e "${GREEN}[+] Ollama installed!${NC}"
    
    # Pull default model
    echo -e "${YELLOW}[*] Pulling AI model (llama3.2)...${NC}"
    ollama pull llama3.2 2>/dev/null || echo "Model pull skipped"
fi

# ============ START SCRIPT ============
echo ""
echo -e "${YELLOW}[*] Creating start script...${NC}"

# Create start.sh in the same directory as this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cat > "$SCRIPT_DIR/start.sh" << 'STARTSCRIPT'
#!/bin/bash
# NetworkAI - Start AI Dashboard in Screen

SESSION_NAME="AI"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/ai.log"

# Kill existing session if running
screen -S "$SESSION_NAME" -X quit 2>/dev/null

echo "Starting NetworkAI Dashboard..."
echo "Press Ctrl+A, then D to detach"
echo "Use 'screen -r AI' to reconnect"
echo ""

# Start in screen
cd "$SCRIPT_DIR"
screen -dmS "$SESSION_NAME" bash -c "python3 dashboard.py 2>&1 | tee $LOG_FILE; exec bash"

sleep 1

# Check if running
if screen -list | grep -q "$SESSION_NAME"; then
    echo -e "\033[0;32m[OK] NetworkAI started in screen session 'AI'\033[0m"
    echo "Connect with: screen -r AI"
    echo "Logs: $LOG_FILE"
else
    echo -e "\033[0;31m[ERROR] Failed to start\033[0m"
fi
STARTSCRIPT

chmod +x "$SCRIPT_DIR/start.sh"

# ============ CREATE STOP SCRIPT ============
cat > "$SCRIPT_DIR/stop.sh" << 'STOPSCRIPT'
#!/bin/bash
echo "Stopping NetworkAI..."
screen -S AI -X quit 2>/dev/null
echo "Stopped."
STOPSCRIPT

chmod +x "$SCRIPT_DIR/stop.sh"

# ============ CREATE INSTALL OLLAMA SCRIPT ============
cat > "$SCRIPT_DIR/install_ollama.sh" << 'OLLA'
#!/bin/bash
curl -fsSL https://ollama.com/install.sh | sh
echo "Pulling default model..."
ollama pull llama3.2
echo "Done!"
OLLA

chmod +x "$SCRIPT_DIR/install_ollama.sh"

echo -e "${GREEN}[+] Start scripts created!${NC}"

# ============ FIREWALL SUMMARY ============
echo ""
echo "============================================"
echo "  FIREWALL - OPENED PORTS"
echo "============================================"
echo ""
echo "Port   Service          URL"
echo "----   -------          ---"
echo "5000   AI Dashboard     http://YOUR_IP:5000"
echo "8080   OpenWebUI        http://YOUR_IP:8080"
echo "11434  Ollama API       localhost only"
echo ""
echo -e "${YELLOW}Manual firewall commands:${NC}"
echo ""
echo "# UFW (Debian/Ubuntu):"
for PORT in "${PORTS[@]}"; do
    echo "  sudo ufw allow $PORT/tcp"
done
echo ""
echo "# firewalld (RHEL/CentOS):"
for PORT in "${PORTS[@]}"; do
    echo "  sudo firewall-cmd --permanent --add-port=$PORT/tcp"
done
echo "  sudo firewall-cmd --reload"
echo ""
echo "# iptables:"
for PORT in "${PORTS[@]}"; do
    echo "  sudo iptables -A INPUT -p tcp --dport $PORT -j ACCEPT"
done
echo ""

# ============ USAGE ============
echo "============================================"
echo "  USAGE"
echo "============================================"
echo ""
echo "1. Start AI Dashboard:"
echo "   ./start.sh"
echo ""
echo "2. Reconnect to screen:"
echo "   screen -r AI"
echo ""
echo "3. Detach from screen:"
echo "   Press Ctrl+A, then D"
echo ""
echo "4. Stop AI Dashboard:"
echo "   ./stop.sh"
echo ""
echo "5. View logs:"
echo "   tail -f ai.log"
echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo "============================================"