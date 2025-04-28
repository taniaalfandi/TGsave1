import os
import time
import json
import base64
import threading
import requests
from flask import Flask
from config import *

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is Running!'

def run_flask():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()

API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'
offset = 0
ban_file = 'banned.json'
users_file = 'users.json'

def load_json(path):
    if not os.path.exists(path): return []
    with open(path, 'r') as f: return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f: json.dump(data, f)

def is_banned(user_id):
    return user_id in load_json(ban_file)

def register_user(user_id):
    users = load_json(users_file)
    if user_id not in users:
        users.append(user_id)
        save_json(users_file, users)

def is_owner(user_id):
    return user_id == OWNER_ID
    

def send_message(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", data={"chat_id": chat_id, "text": text})

def send_force_sub_msg(chat_id):
    btn = {
        "inline_keyboard": [
            [{"text": "📢 Join Channel", "url": f"https://t.me/{FORCE_SUB_CHANNEL.strip('@')}"}],
            [{"text": "✅ I Joined", "callback_data": "checksub"}]
        ]
    }
    requests.post(f"{API_URL}/sendMessage", data={
        "chat_id": chat_id,
        "text": "🔐 Pehle channel join karo tabhi access milega!",
        "reply_markup": json.dumps(btn)
    })

def check_subscription(user_id):
    try:
        res = requests.get(f"{API_URL}/getChatMember", params={
            "chat_id": FORCE_SUB_CHANNEL,
            "user_id": user_id
        }).json()
        return res.get("result", {}).get("status") in ["member", "administrator", "creator"]
    except:
        return False

def handle_file(chat_id, user_id, file_type, file_id, message_id):
    if is_banned(user_id):
        send_message(chat_id, "❌ You are banned from using this bot.")
        return
    if not check_subscription(user_id):
        send_force_sub_msg(chat_id)
        return

    try:
        
        resp = requests.post(f"{API_URL}/forwardMessage", data={
            "chat_id": STORAGE_CHANNEL_ID,
            "from_chat_id": chat_id,
            "message_id": message_id
        })
        result = resp.json()
        if not result.get("ok"):
            send_message(chat_id, "❌ File forward nahi hua.")
            return

        stored_message_id = result['result']['message_id']
        unique_code = base64.urlsafe_b64encode(str(stored_message_id).encode()).decode()
        link = f"https://t.me/{BOT_USERNAME}?start={unique_code}"
        send_message(chat_id, f"🔗 Share link:{link}")

    except Exception as e:
        print("handle_file error:", e)
        send_message(chat_id, "❌ File save karne me error aayi.")


def handle_start(chat_id, user_id, args):
    if is_banned(user_id):
        send_message(chat_id, "❌ You are banned from using this bot.")
        return
    if not check_subscription(user_id):
        send_force_sub_msg(chat_id)
        return

    if args:
        try:
            message_id = int(base64.urlsafe_b64decode(args.encode()).decode())
            resp = requests.post(f"{API_URL}/copyMessage", data={
                "chat_id": chat_id,
                "from_chat_id": STORAGE_CHANNEL_ID,
                "message_id": message_id
            })
            if not resp.json().get("ok"):
                send_message(chat_id, "❌ File mil nahi rahi.")
        except:
            send_message(chat_id, "❌ Galat ya expire link.")
    else:
        send_message(chat_id, "👋 Send me any file and I’ll give you a shareable link!")

def handle_callback(callback):
    user_id = callback.get("from", {}).get("id")
    chat_id = callback.get("message", {}).get("chat", {}).get("id")
    data = callback.get("data")

    if data == "checksub":
        if check_subscription(user_id):
            send_message(chat_id, "✅ Thanks! Ab file bhejo.")
        else:
            send_message(chat_id, "❌ Pehle join karo channel!")

def handle_broadcast(text):
    users = load_json(users_file)
    for uid in users:
        try:
            requests.post(f"{API_URL}/sendMessage", data={"chat_id": uid, "text": text})
            time.sleep(0.1)
        except:
            continue

while True:
    try:
        resp = requests.get(f"{API_URL}/getUpdates", params={"offset": offset, "timeout": 30})
        updates = resp.json().get("result", [])

        for update in updates:
            offset = update['update_id'] + 1

            if 'callback_query' in update:
                handle_callback(update['callback_query'])
                continue

            message = update.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            user_id = message.get('from', {}).get('id')
            if not chat_id or not user_id:
                continue

            register_user(user_id)

            if 'text' in message:
                text = message['text']

                if text.startswith('/start'):
                    args = text.split(' ', 1)[1] if ' ' in text else ""
                    handle_start(chat_id, user_id, args)

                elif text.startswith('/ban') and is_owner(user_id):
                    try:
                        ban_id = int(text.split(" ", 1)[1])
                        bans = load_json(ban_file)
                        if ban_id not in bans:
                            bans.append(ban_id)
                            save_json(ban_file, bans)
                            send_message(chat_id, f"✅ Banned {ban_id}")
                    except:
                        send_message(chat_id, "❌ Usage: /ban user_id")

                elif text.startswith('/unban') and is_owner(user_id):
                    try:
                        unban_id = int(text.split(" ", 1)[1])
                        bans = load_json(ban_file)
                        if unban_id in bans:
                            bans.remove(unban_id)
                            save_json(ban_file, bans)
                            send_message(chat_id, f"✅ Unbanned {unban_id}")
                    except:
                        send_message(chat_id, "❌ Usage: /unban user_id")

                elif text.startswith('/broadcast') and is_owner(user_id):
                    msg = text.split(" ", 1)[1] if " " in text else ""
                    if msg:
                        send_message(chat_id, "📤 Broadcasting...")
                        handle_broadcast(msg)
                        send_message(chat_id, "✅ Done broadcasting.")
                    else:
                        send_message(chat_id, "❌ Usage: /broadcast your message")

                elif text.startswith('/users') and is_owner(user_id):
                    users = load_json(users_file)
                    send_message(chat_id, f"👥 Total users: {len(users)}")

            for media_type in ['document', 'video', 'audio', 'voice', 'video_note', 'photo']:
                if media_type in message:
                    media = message[media_type]
                    file_info = media[-1] if media_type == 'photo' else media
                    file_id = file_info['file_id']
                    handle_file(chat_id, user_id, media_type, file_id, message['message_id'])
                    break

    except Exception as e:
        print("Main loop error:", e)
        time.sleep(3)


if __name__=="__main__":
    main()
