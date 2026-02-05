# -*- coding: utf-8 -*-
import os
import random
import string
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Lấy biến môi trường từ Render
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)

# ==============================
# TẠO MÃ ĐƠN HÀNG
# ==============================
def tao_ma_don():
    return "DH" + "".join(random.choices(string.digits, k=6))


# ==============================
# /START
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ma_don = tao_ma_don()
    context.user_data["ma_don"] = ma_don

    caption = f"""
🧾 MÃ ĐƠN HÀNG: {ma_don}

🎮 Sản phẩm: Acc LV15
💰 Giá: 10.000 VND

📌 Vui lòng quét mã QR bên dưới để thanh toán.
Sau khi chuyển khoản xong hãy gửi bill vào đây để admin check.
"""

    try:
        with open("qr.jpg", "rb") as photo:
            await update.message.reply_photo(photo=photo, caption=caption)
    except:
        await update.message.reply_text("Không tìm thấy ảnh qr.jpg")


# ==============================
# NHẬN BILL
# ==============================
async def nhan_bill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        ma_don = context.user_data.get("ma_don", "Không rõ")
        user = update.message.from_user

        # Gửi bill cho admin
        await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id,
        )

        # Gửi thông tin kèm theo cho admin
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"""
📥 Có bill mới

👤 User: @{user.username}
🆔 ID: {user.id}
🧾 Mã đơn: {ma_don}
""",
        )

        await update.message.reply_text(
            "✅ Đã gửi bill cho admin. Vui lòng chờ kiểm tra."
        )


# ==============================
# ADMIN GỬI TÀI KHOẢN
# /gui IDUSER taikhoan matkhau
# ==============================
async def gui(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    if len(context.args) < 3:
        await update.message.reply_text(
            "Cách dùng:\n/gui IDUSER taikhoan matkhau"
        )
        return

    user_id = int(context.args[0])
    tai_khoan = context.args[1]
    mat_khau = context.args[2]

    await context.bot.send_message(
        chat_id=user_id,
        text=f"""
🎉 Thanh toán thành công!

🔐 Tài khoản: {tai_khoan}
🔑 Mật khẩu: {mat_khau}

Chúc bạn chơi game vui vẻ!
""",
    )

    await update.message.reply_text("✅ Đã gửi tài khoản cho khách.")


# ==============================
# MAIN
# ==============================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gui", gui))
    app.add_handler(MessageHandler(filters.PHOTO, nhan_bill))

    print("Bot dang chay...")
    app.run_polling()


if __name__ == "__main__":
    main()
