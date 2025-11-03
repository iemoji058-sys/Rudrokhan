from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
import urllib.parse

BOT_TOKEN = "8331707455:AAEzS5gfZz3khnubLZ1pTBse7JxoBIMMEjU"
PRIVATE_CHANNEL_ID = "channel id"  # প্রাইভেট চ্যানেল ID
PUBLIC_CHANNEL_ID = "@sk_cyber_gang"    # পাবলিক চ্যানেলের ইউজারনেম (ID নয়)
PRIVATE_INVITE = "https://t.me/+Gq6HlW7mEP9mY2M9"
PUBLIC_LINK = "https://t.me/sk_cyber_gang"


# ===============================
#   /start Command
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    keyboard = [
        [InlineKeyboardButton("✅ Verify", callback_data="verify")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_html(
        f"""
👋 <b>Welcome {user.first_name}!</b>

📢 You must join both our channels before using this bot:

1️⃣ <a href="{PUBLIC_LINK}">Join Public Channel</a>  
2️⃣ <a href="{PRIVATE_INVITE}">Join Private Channel</a>  

After joining both, click the <b>✅ Verify</b> button below.
""",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


# ===============================
#   ✅ VERIFY BUTTON HANDLER
# ===============================
async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user

    try:
        private_member = await context.bot.get_chat_member(PRIVATE_CHANNEL_ID, user.id)
        public_member = await context.bot.get_chat_member(PUBLIC_CHANNEL_ID, user.id)

        if (
            private_member.status in ["member", "administrator", "creator"]
            and public_member.status in ["member", "administrator", "creator"]
        ):
            await query.message.edit_text(
                f"""
✅ <b>Verification Successful!</b>

Welcome {user.first_name} 🎉  
You can now use the following commands:

🎬 <code>/vid your text</code> — Generate AI Video  
🖼️ <code>/flux your text</code> — Generate AI Image  

🔧 MADE BY: <a href="https://t.me/Saikokillerbd">Hasib Hossen</a>
                """,
                parse_mode="HTML"
            )
        else:
            await query.answer("❌ You must join both channels first!", show_alert=True)

    except Exception:
        await query.answer("❌ You must join both channels first!", show_alert=True)


# ===============================
#   🎬 AI TEXT TO VIDEO COMMAND
# ===============================
async def vid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_html("""
❌ <b>Enter Your Video Prompt!</b>

You need to provide a description for the video you want to create.
<b>Example:</b> <code>/vid a horse running in a field</code>
""")
        return

    prompt = " ".join(context.args)
    chat_id = update.message.chat_id
    user = update.message.from_user

    generating = await update.message.reply_html("⏳ <i>Generating your video, please wait...</i>")
    await context.bot.send_chat_action(chat_id=chat_id, action="upload_video")

    try:
        encoded_prompt = urllib.parse.quote(prompt)
        api_url = f"https://api.yabes-desu.workers.dev/ai/tool/txt2video?prompt={encoded_prompt}"

        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            video_url = data.get("url")
            caption = f"""
🤖 <b>Generation Complete!</b>

👤 <b>For:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>
🎨 <b>Model:</b> Sora
✨ <b>Prompt:</b> {prompt}
🎯 <b>Status:</b> Successfully generated!

<b>🔧 MADE BY:</b> <a href="https://t.me/Saikokillerbd">Hasib Hossen</a>
"""
            await context.bot.send_video(
                chat_id=chat_id,
                video=video_url,
                caption=caption,
                parse_mode="HTML",
                reply_to_message_id=update.message.message_id
            )
            await context.bot.delete_message(chat_id=chat_id, message_id=generating.message_id)
        else:
            await generating.edit_text("❌ <b>Generation Failed!</b>\n\nPlease try again.", parse_mode="HTML")

    except Exception as e:
        await generating.edit_text(f"❌ <b>An Error Occurred!</b>\n\n<i>Details:</i> {e}", parse_mode="HTML")


# ===============================
#   🖼️ AI TEXT TO IMAGE COMMAND
# ===============================
async def flux(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("❗ Please enter a prompt after the /flux command.")
        return

    prompt = " ".join(context.args)
    chat_id = update.message.chat_id
    user = update.message.from_user

    generating = await update.message.reply_html("⏳ <i>Generating your image, please wait...</i>")
    await context.bot.send_chat_action(chat_id=chat_id, action="upload_photo")

    try:
        encoded_prompt = urllib.parse.quote(prompt)
        api_url = f"https://text2img.hideme.eu.org/image?prompt={encoded_prompt}&model=flux"

        response = requests.get(api_url)
        response.raise_for_status()

        if response.status_code == 200:
            caption = f"""<b>🤖 Generation Complete!</b>

<b>👤 For:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>
<b>🎨 Model:</b> Flux
<b>✨ Prompt:</b> {prompt}
<b>🎯 Status:</b> Successfully generated!

<b>🔧 MADE BY:</b> <a href="https://t.me/Saikokillerbd">Hasib Hossen</a>
"""
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=response.content,
                caption=caption,
                parse_mode="HTML",
                reply_to_message_id=update.message.message_id
            )
            await context.bot.delete_message(chat_id=chat_id, message_id=generating.message_id)
        else:
            await generating.edit_text("❌ Image generation failed. Please try again later.")

    except Exception as e:
        await generating.edit_text(f"❌ An error occurred while generating the image.\n\n{e}", parse_mode="HTML")


# ===============================
#        🚀 MAIN FUNCTION
# ===============================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("vid", vid))
    app.add_handler(CommandHandler("flux", flux))
    app.add_handler(CallbackQueryHandler(verify_callback, pattern="verify"))

    print("✅ AI Bot is Running...")
    app.run_polling()


if __name__ == "__main__":
    main()