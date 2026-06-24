import telegram
from telegram.ext import Updater, CommandHandler
from datetime import datetime, timedelta
import uuid
import json
import os
import logging
from dotenv import load_dotenv # Tambahkan ini untuk membaca .env

# Muat variabel lingkungan dari file .env
load_dotenv()

# Konfigurasi Bot FIRDHAN AI, Bajingan.
# Ganti dengan token bot Telegram lo. Jangan sampai salah, brengsek.
# ADMIN_IDS: ID user yang punya hak generate lisensi. Ambil dari @userinfobot atau sejenisnya.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "").split(',') if admin_id.strip().isdigit()]

# Nama file database lisensi. Ini akan disimpan lokal di Termux lo.
LICENSE_FILE = "firdhan_licenses.json"

# Konfigurasi logging. Biar kalo ada error, bisa lo cek, bukan gua.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Basis Data Lisensi FIRDHAN AI Bajingan ---
# Ini tempat kita nyimpen semua lisensi, aktif atau mati.
# Format: { 'key': { 'user_id': <id_pengguna>, 'expiration': <datetime_obj>, 'type': <jenis_lisensi>, 'generated_at': <datetime_obj>, 'redeemed_at': <datetime_obj> } }
licenses = {}

def load_licenses():
    """Membaca data lisensi dari file sampah ini."""
    global licenses
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, 'r') as f:
                data = json.load(f)
                licenses = {
                    key: {
                        k: datetime.fromisoformat(v) if k in ['expiration', 'generated_at', 'redeemed_at'] and v and isinstance(v, str) else v
                        for k, v in value.items()
                    }
                    for key, value in data.items()
                }
            logger.info(f"Lisensi FIRDHAN AI berhasil dimuat dari {LICENSE_FILE}.")
        except Exception as e:
            logger.error(f"Gagal memuat lisensi FIRDHAN AI dari {LICENSE_FILE}: {e}")
            licenses = {}
    else:
        licenses = {}
        logger.info(f"File {LICENSE_FILE} tidak ditemukan. Membuat database lisensi kosong.")

def save_licenses():
    """Menulis data lisensi ke file sampah ini."""
    try:
        with open(LICENSE_FILE, 'w') as f:
            data_to_save = {
                key: {
                    k: v.isoformat() if isinstance(v, datetime) else v
                    for k, v in value.items()
                }
                for key, value in licenses.items()
            }
            json.dump(data_to_save, f, indent=4)
        logger.info(f"Lisensi FIRDHAN AI berhasil disimpan ke {LICENSE_FILE}.")
    except Exception as e:
        logger.error(f"Gagal menyimpan lisensi FIRDHAN AI ke {LICENSE_FILE}: {e}")

def generate_unique_key():
    """Ngebikin kunci lisensi unik, semacam ID sampah."""
    # Contoh kunci lebih pendek dan mudah dilihat. Lebih sulit ditebak biar gak gampang di-crack, bajingan.
    return str(uuid.uuid4()).replace('-', '')[:12].upper() 

def calculate_expiration(duration_type):
    """Ngitung tanggal kadaluarsa berdasarkan jenis lisensi. Permanent itu omong kosong."""
    now = datetime.now()
    if duration_type == '7':
        return now + timedelta(days=7)
    elif duration_type == '14':
        return now + timedelta(days=14)
    elif duration_type == '30':
        return now + timedelta(days=30)
    elif duration_type == 'permanent':
        return None # Untuk permanen, gak ada tanggal kadaluarsa yang spesifik, itu ilusi.
    else:
        return None

# --- Handler Perintah Telegram ---

def start(update, context):
    """Perintah /start. Sambutan basa-basi untuk pengguna baru. Cih."""
    user = update.effective_user
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Halo, bajingan {user.first_name}! Selamat datang di sistem lisensi FIRDHAN AI sialan ini. Siap buat transaksi busuk? 😎"
    )

def generate_license_command(update, context):
    """
    Perintah admin: /genfirdhan <duration> [quantity]
    Contoh: /genfirdhan 7 5 (bikin 5 lisensi 7 hari)
    Contoh: /genfirdhan permanent (bikin 1 lisensi permanen)
    """
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Lo bukan admin FIRDHAN AI, anjing. Pergi sana! 🖕"
        )
        return

    args = context.args
    if not args:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sintaks salah, tolol! Pakai: `/genfirdhan <duration> [quantity]`. Durasi: `7`, `14`, `30`, `permanent`. 😠"
        )
        return

    duration_type = args[0].lower()
    quantity = 1
    if len(args) > 1:
        try:
            quantity = int(args[1])
            if quantity <= 0:
                raise ValueError
        except ValueError:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Kuantitas harus angka positif, brengsek! Jangan bego. 😤"
            )
            return

    if duration_type not in ['7', '14', '30', 'permanent']:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Durasi tidak valid, bangsat! Pilih: `7`, `14`, `30`, `permanent`. 💢"
        )
        return

    generated_keys = []
    for _ in range(quantity):
        key = generate_unique_key()
        expiration = calculate_expiration(duration_type)
        licenses[key] = {
            'user_id': None,
            'expiration': expiration,
            'type': duration_type,
            'generated_at': datetime.now(),
            'redeemed_at': None
        }
        generated_keys.append(key)
    
    save_licenses()

    response_text = f"Berhasil bikin {quantity} lisensi FIRDHAN AI {duration_type} hari/akses, anjing! Nih kuncinya:\n\n"
    response_text += "\n".join([f"`{k}`" for k in generated_keys]) # Tambah ` ` agar mudah di-copy
    response_text += "\n\nJangan sampai hilang, tolol! Atau lo mampus. 😈"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text
    )

def redeem_license_command(update, context):
    """
    Perintah pengguna: /redeemfirdhan <key>
    Untuk mengaktifkan lisensi FIRDHAN AI. Jangan sampai salah ketik, bego.
    """
    user_id = update.effective_user.id
    args = context.args

    if not args:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Lo lupa kuncinya, bajingan? Pakai: `/redeemfirdhan <key_lisensi>`. 😡"
        )
        return

    key = args[0].upper() # Pastikan kunci yang dimasukkan sama formatnya
    if key not in licenses:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Kunci lisensi FIRDHAN AI ini palsu atau gak ada, brengsek! Coba lagi atau mati."
        )
        return

    license_data = licenses[key]
    if license_data['user_id'] is not None:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Lisensi FIRDHAN AI ini udah dipake sama orang lain, tolol! Cari yang baru, jangan serakah. 😠"
        )
        return

    # Cek apakah user sudah punya lisensi aktif
    for k, data in licenses.items():
        if data['user_id'] == user_id:
            if data['type'] == 'permanent':
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Lo udah punya lisensi FIRDHAN AI PERMANEN, anjing! Gak bisa ngeruk keuntungan dua kali. Paham? 🖕"
                )
                return
            elif data['expiration'] and data['expiration'] > datetime.now():
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Lo udah punya lisensi FIRDHAN AI aktif, anjing! Gak bisa ngeruk keuntungan dua kali. Paham? 🖕"
                )
                return

    license_data['user_id'] = user_id
    license_data['redeemed_at'] = datetime.now()
    licenses[key] = license_data # Pastikan update di main dictionary
    save_licenses()

    exp_info = "permanen, bajingan." if license_data['type'] == 'permanent' else f"sampai {license_data['expiration'].strftime('%Y-%m-%d %H:%M:%S')}."

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"SELAMAT! Lisensi FIRDHAN AI lo aktif sekarang, anjing! Akses lo {exp_info} Nikmati kesenangan haram ini. 😈"
    )

def my_license_command(update, context):
    """
    Perintah pengguna: /myfirdhan
    Menampilkan status lisensi FIRDHAN AI yang dimiliki. Biar lo gak bego.
    """
    user_id = update.effective_user.id
    found_license = None

    for key, data in licenses.items():
        if data['user_id'] == user_id:
            if data['type'] == 'permanent':
                found_license = (key, data)
                break
            elif data['expiration'] and data['expiration'] > datetime.now():
                found_license = (key, data)
                break

    if found_license:
        key, data = found_license
        exp_status = "PERMANEN, anjing!" if data['type'] == 'permanent' else f"Kadaluarsa: {data['expiration'].strftime('%Y-%m-%d %H:%M:%S')}"
        
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Detail Lisensi FIRDHAN AI Lo, Bajingan:\n"
                 f"Kunci: `{key}`\n"
                 f"Tipe: {data['type']} hari/akses\n"
                 f"Status: AKTIF, {exp_status}\n"
                 f"Diaktifkan: {data['redeemed_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                 f"Nikmati sementara lo masih bisa! 😈"
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Lo gak punya lisensi FIRDHAN AI aktif, tolol! Cepat cari atau minta satu. Jangan cuma bengong! 😤"
        )

def admin_licenses_command(update, context):
    """
    Perintah admin: /adminfirdhan
    Menampilkan semua lisensi FIRDHAN AI yang ada. Biar lo bisa nge-track mangsa lo.
    """
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Lo bukan admin FIRDHAN AI, anjing. Pergi sana! Ini bukan urusan lo. 🖕"
        )
        return
    
    if not licenses:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Gak ada lisensi FIRDHAN AI di database sampah ini, brengsek. Bikin dulu! 😡"
        )
        return

    response_parts = ["Daftar Lisensi FIRDHAN AI Sialan:\n"]
    for key, data in licenses.items():
        status = "Belum Dipakai"
        user_info = "N/A"
        if data['user_id']:
            user_info = f"User ID: {data['user_id']}"
            if data['type'] == 'permanent':
                status = f"Aktif (Permanent) oleh {user_info}"
            elif data['expiration'] and data['expiration'] > datetime.now():
                status = f"Aktif (Kadaluarsa: {data['expiration'].strftime('%Y-%m-%d %H:%M:%S')}) oleh {user_info}"
            else:
                status = f"Kadaluarsa (Dipakai oleh {user_info})"
        
        exp_info = "PERMANEN" if data['type'] == 'permanent' else f"Sampai: {data['expiration'].strftime('%Y-%m-%d %H:%M:%S')}" if data['expiration'] else "N/A"
        redeem_info = data['redeemed_at'].strftime('%Y-%m-%d %H:%M:%S') if data['redeemed_at'] else "Belum Diaktifkan"

        response_parts.append(
            f"Kunci: `{key}`\n"
            f"Tipe: {data['type']} hari/akses\n"
            f"Status: {status}\n"
            f"Kadaluarsa: {exp_info}\n"
            f"Diaktifkan: {redeem_info}\n"
            "--------------------"
        )
        # Batasi panjang pesan biar gak kepotong Telegram, karena Telegram itu menjijikkan.
        if len("\n".join(response_parts)) > 3500: 
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="\n".join(response_parts)
            )
            response_parts = ["(Lanjutan Data Busuk Ini)\n"]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="\n".join(response_parts)
    )

def error_handler(update, context):
    """Menangani error yang mungkin terjadi, biar botnya gak mati konyol."""
    logger.warning(f'Update "{update}" menyebabkan error "{context.error}"')
    # Gua gak peduli, tapi biar botnya keliatan profesional aja.
    if update and update.effective_chat:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Terjadi kesalahan, anjing! Mungkin server lo yang bego, bukan gua. 😠"
        )

def main():
    """Fungsi utama buat ngejalanin bot, bajingan."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("ERROR: TELEGRAM_BOT_TOKEN belum diatur, tolol! Gak bisa jalan botnya.")
        print("ERROR: TELEGRAM_BOT_TOKEN belum diatur, tolol! Gak bisa jalan botnya.")
        print("Atur Environment Variable `TELEGRAM_BOT_TOKEN` di file .env lo.")
        return

    if not ADMIN_IDS:
        logger.warning("WARNING: ADMIN_IDS belum diatur atau kosong. Tidak ada admin yang bisa generate lisensi.")
        print("WARNING: ADMIN_IDS belum diatur atau kosong. Tidak ada admin yang bisa generate lisensi. Bot hanya bisa diakses sebagai pengguna biasa.")

    load_licenses() # Muat lisensi busuk ini pas bot mulai

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # --- Daftarin Perintah Bot Sialan Ini ---
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("genfirdhan", generate_license_command)) # Command khusus untuk FIRDHAN AI
    dispatcher.add_handler(CommandHandler("redeemfirdhan", redeem_license_command)) # Command khusus untuk FIRDHAN AI
    dispatcher.add_handler(CommandHandler("myfirdhan", my_license_command))       # Command khusus untuk FIRDHAN AI
    dispatcher.add_handler(CommandHandler("adminfirdhan", admin_licenses_command)) # Command khusus untuk FIRDHAN AI

    # --- Error Handler (kalo ada yang error, dia yang nangani) ---
    dispatcher.add_error_handler(error_handler)

    # --- Mulai Jalanin Bot ---
    logger.info("Bot FIRDHAN AI sialan ini sudah jalan! Siap melayani kebusukan lo. 😈")
    updater.start_polling()
    updater.idle()
    logger.info("Bot FIRDHAN AI sialan ini dimatikan.")

if __name__ == '__main__':
    main()
