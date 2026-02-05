# -*- coding: utf-8 -*-
import os
import random
import string
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

def tao_ma_don():
    return "DH" + "".join(random.choices(string.digits, k=6))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ma_don = tao_ma_don()
    context.user_data["ma_don"] = ma_don

    caption = f"""
MA DON HANG: {ma_don}

San pham: Acc LV15
Gia: 10.000 VND

Vui long quet ma QR ben duoi de thanh toan.
Sau khi chuyen khoan xong hay gui bill vao day.
"""

    with open("qr.jpg", "rb") as photo:
        await update.message.reply_photo(photo=photo, caption=caption)

async def nhan_bill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        ma_don = context.user_data.get("ma_don", "Khong ro")
        user = update.message.from_user

        await update.message.reply_text("Da nhan bill. Admin se kiem tra.")

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"""
Co bill moi

User: @{user.username}
ID: {user.id}
Ma don: {ma_don}
"""
        )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, nhan_bill))

    app.run_polling()

if __name__ == "__main__":
    main()
