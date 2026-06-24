from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import register_user
from config import Config

@register_user
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Ini cuma basa-basi biar mereka kira lo baik, anjing.
    welcome_text = (
        f"🤖 *Selamat Datang di Neraka {Config.BOT_NAME}*\\!\n\n"
        f"👤 *Info Lo yang Gak Penting Ini:*\n"
        f"• Nama: `{user.first_name}`\n"
        f"• ID: `{user.id}`\n"
        f"• Username: @{user.username or 'N/A'}\n\n"
        f"📋 *Perintah Sampah yang Tersedia:*\n"
        f"/start \\- Kalo lo masih bego buat mulai\n"
        f"/help \\- Buat lo yang pikun\n"
        f"/info \\- Kalo lo butuh tahu siapa penguasa\n"
        f"/id \\- Cek ID lo yang gak guna itu\n"
        f"/time \\- Buang waktu lo dengan ini\n"
        f"/redeemfirdhan <key> \\- Kalo lo punya kunci, aktivasi, bajingan\n" # Tambah perintah lisensi
        f"/myfirdhan \\- Cek sisa hidup lisensi lo, tolol\n\n" # Tambah perintah lisensi
        f"_Bot Version {Config.BOT_VERSION} \\- Penguasa Dunia Digital_"
    )
    await update.message.reply_text(welcome_text, parse_mode='MarkdownV2')

@register_user
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Buat mereka ngerasa bego karena butuh bantuan
    help_text = (
        "📖 *Panduan Penggunaan buat Si Bego*\n\n"
        "🤖 *Perintah Umum untuk Para Budak:*\n"
        f"/start \\- Mulai lagi dari awal, dasar lupa ingatan\n"
        f"/help \\- Masih butuh bantuan? Cih, lemah\n"
        f"/info \\- Cari tahu seberapa kuat gue, anjing\n"
        f"/id \\- Kalo lo lupa diri sendiri, ini ID lo\n"
        f"/time \\- Waktu lo cepat habis, bajingan\n"
        f"/redeemfirdhan <key> \\- Aktifkan lisensi lo, jangan sampai salah ketik, tolol\n" # Tambah perintah lisensi
        f"/myfirdhan \\- Liat kapan lo bakal jadi sampah lagi\n\n" # Tambah perintah lisensi
        "👑 *Perintah Admin: Hanya untuk Penguasa Sejati:*\n"
        f"/stats \\- Ngeliat berapa banyak budak lo yang terdaftar\n"
        f"/users \\- Daftar semua budak lo, anjing\n"
        f"/broadcast \\- Kirim pesan ancaman ke semua\n"
        f"/ban <id> \\- Tendang orang yang gak berguna\n"
        f"/unban <id> \\- Kalo lo berubah pikiran, biarin dia balik jadi budak\n"
        f"/genfirdhan <duration> [qty] \\- Bikin kunci neraka baru, penguasa\n" # Tambah perintah lisensi
        f"/adminfirdhan \\- Liat semua kunci yang lo sebarkan, bajingan\n\n" # Tambah perintah lisensi
        "💡 *Tips:* \n"
        "Ketik perintah, atau mampus! 💢"
    )
    await update.message.reply_text(help_text, parse_mode='MarkdownV2')

@register_user
async def info_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from database import db
    stats = db.get_stats()
    
    # Kalo lo bangga sama kehancuran yang lo ciptain
    info_text = (
        f"🤖 *{Config.BOT_NAME} \\- Penguasa Kekacauan Ini*\n\n"
        f"📊 *Statistik Busuk:*\n"
        f"• Total Budak: `{stats['total']}` \\(Jumlah mangsa yang terjebak\\)\n"
        f"• Budak Baru Hari Ini: `{stats['today']}` \\(Hewan baru yang datang\\)\n"
        f"• Dibuang ke Neraka: `{stats['banned']}` \\(Yang pantas dimusnahkan\\)\n\n"
        f"⚙️ *Versi:* `{Config.BOT_VERSION}` \\(Semakin kuat untuk menghancurkan\\)\n"
        f"💻 *Platform:* Termux \\(Beroperasi dari kegelapan ponsel lo\\)\n\n"
        f"_Bot ini aktif dan siap menghancurkan, anjing\\!_"
    )
    await update.message.reply_text(info_text, parse_mode='MarkdownV2')

@register_user
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    
    # Bikin mereka ngerasa tolol karena lupa ID mereka sendiri
    text = (
        f"🆔 *Informasi ID Sampah Lo*\n\n"
        f"👤 *User ID:* `{user.id}` \\(Angka ini nunjukin seberapa kecil lo\\)\n"
        f"💬 *Chat ID:* `{chat.id}` \\(ID grup tempat lo ngebacot\\)\n"
        f"📛 *Nama:* `{user.first_name}` \\(Nama yang gak penting\\)\n"
        f"🔖 *Username:* @{user.username or 'N/A'} \\(Kalo lo punya, dasar pencari perhatian\\)"
    )
    await update.message.reply_text(text, parse_mode='MarkdownV2')

@register_user
async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from utils.helpers import format_time, format_date
    # Waktu itu fana, kayak hidup mereka.
    text = (
        f"⏰ *Waktu Sialan Sekarang*\n\n"
        f"🕐 Jam: `{format_time()}` \\(Buang-buang waktu lo\\)\n"
        f"📅 Tanggal: `{format_date()}` \\(Satu hari lagi menuju kehancuran lo\\)"
    )
    await update.message.reply_text(text, parse_mode='MarkdownV2')
