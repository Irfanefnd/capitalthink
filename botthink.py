from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import pandas as pd
import logging

API_TOKEN = '8013194953:AAHrZkwLTmoG7dAKbhttqEPwAdPe2mS6JCI'  # Ganti dengan token dari BotFather

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Data frame global untuk menyimpan aset user
assets_df = pd.DataFrame(columns=["UserID", "User", "IDR", "USDT", "Rate"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Kirim laporan keuangan dengan format:\n"
        "IDR: <jumlah>\nUSDT: <jumlah>\nrate: <nilai>\n"
        "Contoh: IDR: 1000000 USDT: 50 rate: 16000\n\n"
        "Gunakan /lihatdata untuk melihat data Anda."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Format pesan:\nIDR: <jumlah> USDT: <jumlah> rate: <nilai>\n"
        "Contoh: IDR: 1000000 USDT: 50 rate: 16000\n"
        "Gunakan /lihatdata untuk melihat data Anda."
    )

def parse_report(message):
    try:
        parts = message.replace('\n', ' ').split()
        idr = float([p.split(':')[1] for p in parts if p.lower().startswith('idr:')][0])
        usdt = float([p.split(':')[1] for p in parts if p.lower().startswith('usdt:')][0])
        rate = float([p.split(':')[1] for p in parts if p.lower().startswith('rate:')][0])
        return idr, usdt, rate
    except Exception:
        return None, None, None

async def handle_financial_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Hanya proses pesan di chat pribadi, atau jika di grup hanya perintah
    if update.effective_chat.type != "private":
        return

    user = update.message.from_user.first_name
    user_id = update.message.from_user.id
    message = update.message.text

    idr, usdt, rate = parse_report(message)
    if idr is None or usdt is None or rate is None:
        await update.message.reply_text(
            "Format salah!\nContoh: IDR: 1000000 USDT: 50 rate: 16000"
        )
        return

    # Simpan data user ke DataFrame global
    global assets_df
    # Hapus data lama user (agar hanya simpan data terakhir)
    assets_df = assets_df[assets_df.UserID != user_id]
    assets_df = assets_df.append({
        "UserID": user_id,
        "User": user,
        "IDR": idr,
        "USDT": usdt,
        "Rate": rate
    }, ignore_index=True)

    total = idr + usdt * rate
    await update.message.reply_text(
        f"Data tersimpan!\nUser: {user}\nIDR: {idr}\nUSDT: {usdt}\nRate: {rate}\nTotal aset (IDR): {total:,.2f}"
    )

async def lihatdata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.first_name
    user_id = update.message.from_user.id
    global assets_df
    user_data = assets_df[assets_df.UserID == user_id]
    if user_data.empty:
        await update.message.reply_text("Belum ada data yang tersimpan untuk Anda.")
        return
    row = user_data.iloc[-1]
    total = row.IDR + row.USDT * row.Rate
    await update.message.reply_text(
        f"Data Anda:\nUser: {row.User}\nIDR: {row.IDR}\nUSDT: {row.USDT}\nRate: {row.Rate}\nTotal aset (IDR): {total:,.2f}"
    )

def main():
    app = Application.builder().token('7960193868:AAFGkXMqQheatftT7465kOg3dMcud5jNdBA').build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("lihatdata", lihatdata))
    # Handler untuk laporan keuangan hanya di chat pribadi
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_financial_report))

    print("Bot berjalan... Tekan CTRL+C untuk berhenti.")
    app.run_polling()

if __name__ == "__main__":
    main()
