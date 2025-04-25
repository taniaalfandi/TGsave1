# FileStore-Tg-Bot

# 📁 FileStore-Tg-Bot

A Telegram bot to **upload and share Telegram files with shareable links**, using a storage channel.

Made with ❤️ in Python using the `requests` module and the Telegram Bot API (not using any framework).

---

## ✨ Features

- 📤 Upload any file (video, doc, audio, image, etc.)
- 🔗 Generate shareable link like: `https://t.me/YourBot?start=somecode`
- 🗂 Save files to your private storage channel
- 🚫 Ban/unban users
- 📢 Broadcast messages
- 🔒 Force join before usage
- 👤 Track total users

---

## ⚙️ Environment Variables

You need to set these variables before deploying:

| Name               | Description                                  |
|--------------------|----------------------------------------------|
| `BOT_TOKEN`         | Your BotFather token                         |
| `OWNER_ID`          | Your Telegram user ID                        |
| `STORAGE_CHANNEL_ID`| Your private channel's numeric ID (with `-100`) |
| `FORCE_SUB_CHANNEL` | Your public channel username (e.g. `@MyChannel`) |
| `BOT_USERNAME`      | Your bot username without `@`                |

---


#📮 Credits
Developed by @priyanshusingh999
Bot logic & deployment steps prepared with ❤️ by community

