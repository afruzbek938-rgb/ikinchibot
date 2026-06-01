import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web
import yt_dlp

# 🟢 BOT TOKEN
BOT_TOKEN = "8615110980:AAHl1YLkvZ1Z8qUr45uI3dMwx-lR0lKVp1E"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def startup_server():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Send me a video link from YouTube, Instagram, or TikTok!")

@dp.message()
async def handle_video_download(message: types.Message):
    user_text = message.text

    if any(x in user_text for x in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com"]):
        msg = await message.answer("Downloading... Please wait.")
        
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'video.mp4',
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([user_text])
            
            video_file = types.FSInputFile('video.mp4')
            await message.answer_video(video=video_file, caption="Done! ✨")
            
            if os.path.exists('video.mp4'):
                os.remove('video.mp4')
            await msg.delete()

        except Exception as e:
            await message.answer(f"Error: {e}")
            if os.path.exists('video.mp4'):
                os.remove('video.mp4')
    else:
        await message.answer("Please send a valid video link!")

async def main():
    await startup_server()  
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
