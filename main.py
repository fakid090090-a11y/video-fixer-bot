import os
import subprocess
from threading import Thread
from flask import Flask
from pyrogram import Client, filters

# Render par bot ko active rakhne ke liye chota web server
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is Running Live!"

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# Main Telegram Bot Code
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("video_converter_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 Hello! Mujhe koi bhi aisi video bhejein jo aage-piche nahi ho rahi hai, main use theek kar dunga.")

@app.on_message(filters.video | filters.document)
async def convert_video(client, message):
    status = await message.reply_text("📥 Video download ho rahi hai...")
    file_path = await message.download()
    
    await status.edit_text("⚙️ Video format theek kiya ja raha hai (Fixing Seek)...")
    output_path = "fixed_" + os.path.basename(file_path).split('.')[0] + ".mp4"
    
    cmd = f'ffmpeg -i "{file_path}" -c:v libx264 -pix_fmt yuv420p -profile:v high -level 4.1 -movflags +faststart -c:a aac "{output_path}" -y'
    process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if process.returncode == 0:
        await status.edit_text("📤 Fixed video upload ho rahi hai...")
        await message.reply_video(video=output_path, caption="✅ Ab aap is video ko aage-piche (seek) karke dekh sakte hain!")
    else:
        await status.edit_text("❌ Error: Video convert nahi ho payi.")
    
    if os.path.exists(file_path): os.remove(file_path)
    if os.path.exists(output_path): os.remove(output_path)

if __name__ == "__main__":
    # Web server ko background me start karein
    Thread(target=run_flask).start()
    # Telegram bot ko run karein
    app.run()
    
