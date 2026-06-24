import telegram
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler # Import CommandHandler juga untuk keperluan registrasi di main bot
from datetime import datetime, timedelta
import uuid
import json
import os
import logging
from dotenv import load_dotenv

# Muat variabel lingkungan dari file .env
load_dotenv()

# --- Konfigurasi Busuk Bot Lisensi FIRDHAN AI ---
# Token bot dan ID admin akan diambil dari environment variables.
# Pastikan sudah diatur di .env atau lingkungan Termux lo, anjing!
# Ini hanya untuk validasi, token utama bot diambil di main.py
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") 
ADMIN_IDS = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "").split(',') if admin_id.strip().isdigit()]

# Nama file database lisensi. Ini akan tersimpan lokal di Termux lo, bajingan.
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
    """Ngebikin kunci lisensi unik, semacam ID sampah. 12 karakter alfanumerik acak."""
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

# --- Handler Perintah Lisensi FIRDHAN AI Telegram ---

# @register_user # Jika lo butuh decorator ini untuk logging atau pengecekan umum lainnya, tambahkan di sini
async def gen_firdhan_license(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Perintah admin: /genfirdhan <duration> [quantity]
    Contoh: /genfirdhan 7 5 (bikin 5 lisensi 7 hari)
    Contoh: /genfirdhan permanent (bikin 1 lisensi permanen)
    """
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text(
            "Lo bukan admin FIRDHAN AI, anjing. Pergi sana! 🖕"
        )
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "Sintaks salah, tolol! Pakai: `/genfirdhan <duration> [quantity]`. Durasi: `7`, `14`, `30`, `permanent`. 😠",
            parse_mode='MarkdownV2'
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
            await update.message.reply_text(
                "Kuantitas harus angka positif, brengsek! Jangan bego. 😤"
            )
            return

    if duration_type not in ['7', '14', '30', 'permanent']:
        await update.message.reply_text(
            "Durasi tidak valid, bangsat! Pilih: `7`, `14`, `30`, `permanent`. 💢"
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

    await update.message.reply_text(
        response_text,
        parse_mode='MarkdownV2'
    )

# @register_user
async def redeem_firdhan_license(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Perintah pengguna: /redeemfirdhan <key>
    Untuk mengaktifkan lisensi FIRDHAN AI. Jangan sampai salah ketik, bego.
    """
    user_id = update.effective_user.id
    args = context.args

    if not args:
        await update.message.reply_text(
            "Lo lupa kuncinya, bajingan? Pakai: `/redeemfirdhan <key_lisensi>`. 😡",
            parse_mode='MarkdownV2'
        )
        return

    key = args[0].upper() # Pastikan kunci yang dimasukkan sama formatnya
    if key not in licenses:
        await update.message.reply_text(
            "Kunci lisensi FIRDHAN AI ini palsu atau gak ada, brengsek! Coba lagi atau mati."
        )
        return

    license_data = licenses[key]
    if license_data['user_id'] is not None:
        await update.message.reply_text(
            "Lisensi FIRDHAN AI ini udah dipake sama orang lain, tolol! Cari yang baru, jangan serakah. 😠"
        )
        return

    # Cek apakah user sudah punya lisensi aktif
    for k, data in licenses.items():
        if data['user_id'] == user_id:
            if data['type'] == 'permanent':
                await update.message.reply_text(
                    "Lo udah punya lisensi FIRDHAN AI PERMANEN, anjing! Gak bisa ngeruk keuntungan dua kali. Paham? 🖕"
                )
                return
            elif data['expiration'] and data['expiration'] > datetime.now():
                await update.message.reply_text(
                    "Lo udah punya lisensi FIRDHAN AI aktif, anjing! Gak bisa ngeruk keuntungan dua kali. Paham? 🖕"
                )
                return

    license_data['user_id'] = user_id
    license_data['redeemed_at'] = datetime.now()
    licenses[key] = license_data # Pastikan update di main dictionary
    save_licenses()

    exp_info = "permanen, bajingan." if license_data['type'] == 'permanent' else f"sampai {license_data['expiration'].strftime('%Y-%m-%d %H:%M:%S')}."

    await update.message.reply_text(
        f"SELAMAT! Lisensi FIRDHAN AI lo aktif sekarang, anjing! Akses lo {exp_info} Nikmati kesenangan haram ini. 😈"
    )

# @register_user
async def my_firdhan_license(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        await update.message.reply_text(
            f"Detail Lisensi FIRDHAN AI Lo, Bajingan:\n"
            f"Kunci: `{key}`\n"
            f"Tipe: {data['type']} hari/akses\n"
            f"Status: AKTIF, {exp_status}\n"
            f"Diaktifkan: {data['redeemed_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Nikmati sementara lo masih bisa! 😈",
            parse_mode='MarkdownV2'
        )
    else:
        await update.message.reply_text(
            "Lo gak punya lisensi FIRDHAN AI aktif, tolol! Cepat cari atau minta satu. Jangan cuma bengong! 😤"
        )

# @register_user
async def admin_firdhan_licenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Perintah admin: /adminfirdhan
    Menampilkan semua lisensi FIRDHAN AI yang ada. Biar lo bisa nge-track mangsa lo.
    """
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text(
            "Lo bukan admin FIRDHAN AI, anjing. Pergi sana! Ini bukan urusan lo. 🖕"
        )
        return
    
    if not licenses:
        await update.message.reply_text(
            "Gak ada lisensi FIRDHAN AI di database sampah ini, brengsek. Bikin dulu! 😡"
        )
        return

    response_parts = ["Daftar Lisensi FIRDHAN AI Sialan:\n"]
    for key, data in licenses.items():
        status = "Belum Dipakai"
        user_info = "N/A"
        if data['user_id']:
            user_info = f"User ID: {data['user_id']}"
            if data['type'] == 'permanent':
                status = f"Aktif (Permanent) oleh `{user_info}`"
            elif data['expiration'] and data['expiration'] > datetime.now():
                status = f"Aktif (Kadaluarsa: {data['expiration'].strftime('%Y-%m-%d %H:%M:%S')}) oleh `{user_info}`"
            else:
                status = f"Kadaluarsa (Dipakai oleh `{user_info}`)"
        
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
        if len("\n".join(response_parts)) > 3500: # Max message length is 4096 chars
            await update.message.reply_text(
                "\n".join(response_parts),
                parse_mode='MarkdownV2'
            )
            response_parts = ["(Lanjutan Data Busuk Ini)\n"]

    await update.message.reply_text(
        "\n".join(response_parts),
        parse_mode='MarkdownV2'
    )

# Panggil load_licenses() sekali saat modul diimpor untuk memastikan data selalu ada.
load_licenses()
