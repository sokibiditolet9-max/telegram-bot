# -*- coding: utf-8 -*-
import os
import random
import string
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Tao ma don hang
def tao_ma_don():
    return "DH" + "".join(random.choices(string.digits, k=6))

# Khi nguoi dung bam /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ma_don = tao_ma_don()
    context.user_data["ma_don"] = ma_don

    caption = f"""
MA DON HANG: {ma_don}

San pham: Acc LV15
Gia: 10.000 VND

Vui long quet ma QR ben duoi de thanh toan.
Sau khi chuyen khoan xong hay gui bill vao day de admin check.
"""

    with open("qr.jpg", "rb") as photo:
        await update.message.reply_photo(photo=photo, caption=caption)

# Khi nguoi dung gui anh (bill)
async def nhan_bill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        ma_don = context.user_data.get("ma_don", "Khong ro")

        await update.message.reply_text("Da nhan bill. Vui long doi admin check.")

        # Gui cho admin
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Co bill moi.\nMa don: {ma_don}\nUser: @{update.message.from_user.username}"
        )
        await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )

# Chay bot
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, nhan_bill))

print("Bot dang chay...")
app.run_polling()