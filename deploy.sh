#!/bin/bash
set -e
echo "=== Deploying KaoYan Assistant ==="

# 1. Install packages
echo "1. Installing packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3-pip python3-venv git nginx 2>&1 | tail -3

# 2. Clone repo
echo "2. Cloning repo..."
sudo rm -rf /opt/kaoyan-assistant
sudo git clone https://github.com/xiaohu-cmd/kaoyan-assistant.git /opt/kaoyan-assistant
sudo chown -R ubuntu:ubuntu /opt/kaoyan-assistant

# 3. Setup venv
echo "3. Installing Python dependencies..."
cd /opt/kaoyan-assistant
python3 -m venv venv
venv/bin/pip install --quiet -r requirements.txt 2>&1 | tail -5

# 4. Init database
echo "4. Initializing database..."
cd /opt/kaoyan-assistant
venv/bin/python -c "
from backend.database import init_db
init_db()
print('Database ready')
"

# 5. Create service
echo "5. Creating systemd service..."
sudo tee /etc/systemd/system/kaoyan.service > /dev/null << 'SERVICEEOF'
[Unit]
Description=KaoYan Assistant
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/kaoyan-assistant
ExecStart=/opt/kaoyan-assistant/venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICEEOF

# 6. Start service
echo "6. Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable kaoyan
sudo systemctl restart kaoyan
sleep 4

# 7. Check
echo "7. Verifying..."
curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost:8000
echo ""
echo "=== Deploy Complete ==="
echo "URL: http://120.53.245.38:8000"
