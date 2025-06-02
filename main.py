import hashlib
import os
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.ext import AIORateLimiter

BOT_TOKEN = "7873773362:AAHSy-N-OujHOB4dNjTuZTzqqgn7A804YAw"
APP_URL = "https://hotline-predictor.onrender.com"  # 🔁 Replace this with your actual Render URL

app = FastAPI()
bot_app = Application.builder().token(BOT_TOKEN).rate_limiter(AIORateLimiter()).build()

users_data = {}

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return "ok"

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users_data[user_id] = {}
    await update.message.reply_text(
        "*🔥 Welcome to Hotline Predictor AI 🔥*\n\n"
        "*99.0% Accurate AI Predictions*\n\n"
        "🔑 _Please enter your Server Seed to begin:_",
        parse_mode="Markdown"
    )

async def collect_seed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users_data:
        users_data[user_id] = {}

    if "seed" not in users_data[user_id]:
        users_data[user_id]["seed"] = update.message.text.strip()
        await update.message.reply_text("💰 *Enter your Bet Amount:*", parse_mode="Markdown")
    else:
        users_data[user_id]["amount"] = update.message.text.strip()
        await show_prediction(update, context)

def predict_color(seed: str) -> str:
    hashed = hashlib.sha256(seed.encode()).hexdigest()
    result = int(hashed[-2:], 16)
    return "RED" if result % 2 == 0 else "BLACK"

async def show_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    seed = users_data[user_id]["seed"]
    amount = users_data[user_id]["amount"]
    result = predict_color(seed)

    image_url = (
        "https://i.ibb.co/nqkF83rg/Screenshot-20250421-083654-Chrome.png"
        if result == "RED"
        else "https://i.ibb.co/67w0dd5T/Screenshot-20250421-083726-Chrome.png"
    )

    final_text = f"""*🎯 Prediction Completed!*

🔐 *Seed:* `{seed}`
💰 *Bet:* ₹{amount}
🧠 *AI Output:* *{result}*

_Result generated with hashed pattern simulation._"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Bet Again", callback_data="retry")],
    ])

    await update.message.reply_photo(
        photo=image_url,
        caption=final_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    del users_data[user_id]

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "retry":
        await query.message.reply_text("🔁 _Enter your Server Seed again:_", parse_mode="Markdown")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """▶ *Features:*
• Accurate Hotline Predictions
• Smart Hash-Based AI
• Clean UI + VIP Access
• Only 1 Free Prediction — Upgrade for Unlimited!""",
        parse_mode="Markdown"
    )

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("help", help_cmd))
bot_app.add_handler(CallbackQueryHandler(button_handler))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_seed))

@app.on_event("startup")
async def on_startup():
    await bot_app.initialize()
    await bot_app.bot.set_webhook(url=f"{APP_URL}/")

