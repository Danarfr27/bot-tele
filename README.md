# 🤖 Telegram Bot

Bot Telegram yang berjalan di Termux.

## Setup di Termux

```bash
# Update dan install dependencies
pkg update && pkg upgrade -y
pkg install python git -y

# Clone repository
git clone https://github.com/USERNAME/REPO_ANDA.git
cd REPO_ANDA

# Install Python dependencies
pip install -r requirements.txt

# Buat file .env
cp .env.example .env
nano .env  # Edit dan masukkan BOT_TOKEN

# Jalankan bot
python bot.py
