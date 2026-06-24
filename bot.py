import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN tidak ditemukan! Pastikan file .env sudah benar.")

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Halo {user.first_name}! 👋\n"
        f"Bot Anda aktif dan berjalan di Termux!\n\n"
        f"Ketik /help untuk melihat perintah yang tersedia."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *Daftar Perintah:*\n\n"
        "/start - Memulai bot\n"
        "/help - Menampilkan bantuan\n"
        "/status - Cek status bot\n\n"
        "_Bot running on Termux_",
        parse_mode='Markdown'
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import platform
    await update.message.reply_text(
        f"🤖 *Status Bot*\n\n"
        f"Platform: `{platform.system()}`\n"
        f"Python: `{platform.python_version()}`\n"
        f"Status: *Online* ✅",
        parse_mode='Markdown'
    )

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    
    logger.info("Bot sedang berjalan...")
    print("=" * 40)
    print("🚀 Bot Telegram Aktif!")
    print("Tekan Ctrl+C untuk berhenti")
    print("=" * 40)
    
    application.run_polling()

if __name__ == "__main__":
    main()
