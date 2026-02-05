import logging
import random
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7874979166:AAF8yy3eUmYIlJmBEHO9ffzKYl-XE9KIZgA"
ADMIN_ID = 6204301614

orders = {}
last_user = {}

# chống spam
start_cooldown = {}
bill_cooldown = {}

COOLDOWN_TIME = 30  # 30 giây

logging.basicConfig(level=logging.INFO)

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    now = time.time()

    # kiểm tra spam start
    if user_id in start_cooldown:
        remaining = int(COOLDOWN_TIME - (now - start_cooldown[user_id]))
        if remaining > 0:
            await update.message.reply_text(f"⛔ Vui lòng chờ {remaining} giây trước khi dùng lại.")
            return

    start_cooldown[user_id] = now

    order_id = f"DH{random.randint(100000,999999)}"
    orders[user_id] = order_id

    caption_text = (
        "🎮 SHOP ACC FREE FIRE 🎮\n\n"
        "📌 Sản phẩm: Acc Lv15\n"
        "💰 Giá: 10.000 VNĐ\n\n"
        f"🧾 Mã đơn của bạn: {order_id}\n\n"
        "📷 Vui lòng quét mã QR để thanh toán.\n"
        "Sau khi chuyển khoản hãy gửi bill để admin check."
    )

    await update.message.reply_photo(
        photo=open("qr.jpg", "rb"),
        caption=caption_text
    )

# ===== NHẬN BILL =====
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    now = time.time()

    # kiểm tra spam bill
    if chat_id in bill_cooldown:
        remaining = int(COOLDOWN_TIME - (now - bill_cooldown[chat_id]))
        if remaining > 0:
            await update.message.reply_text(f"⛔ Bạn vừa gửi bill rồi. Chờ {remaining} giây.")
            return

    bill_cooldown[chat_id] = now
    last_user["user_id"] = chat_id

    order_id = orders.get(chat_id, "Chưa có mã đơn")

    await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=chat_id,
        message_id=update.message.message_id
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📥 Bill mới\n\n👤 User ID: {chat_id}\n🧾 Mã đơn: {order_id}"
    )

    await update.message.reply_text("✅ Đã gửi bill cho admin, vui lòng chờ.")

# ===== ADMIN GỬI MẬT KHẨU =====
async def gui(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    if "user_id" not in last_user:
        await update.message.reply_text("Chưa có ai gửi bill.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Cách dùng: /gui matkhau")
        return

    password = context.args[0]
    user_id = last_user["user_id"]

    await context.bot.send_message(
        chat_id=user_id,
        text=f"🎉 Thanh toán thành công!\n\n🔐 Mật khẩu acc: {password}"
    )

    await update.message.reply_text("✅ Đã gửi mật khẩu cho khách.")

# ===== CHECK ĐƠN =====
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    if len(context.args) < 1:
        await update.message.reply_text("Cách dùng:\n/check user_id")
        return

    user_id = int(context.args[0])

    if user_id in orders:
        order_id = orders[user_id]
        await update.message.reply_text(
            f"🔎 Thông tin đơn hàng\n\n👤 User ID: {user_id}\n🧾 Mã đơn: {order_id}"
        )
    else:
        await update.message.reply_text("Không tìm thấy đơn.")

# ===== RUN BOT =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(CommandHandler("gui", gui))
app.add_handler(CommandHandler("check", check))

app.run_polling()
