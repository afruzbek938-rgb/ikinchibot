import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web
import yt_dlp

# 🟢 BOT TOKEN: Faqat telegram bot tokenini yozing
BOT_TOKEN = "8615110980:AAHl1YLkvZ1Z8qUr45uI3dMwx-lR0lKVp1E"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Render o'chirib qo'ymasligi uchun port ochadigan qism (Bunga tegmang)
async def startup_server():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Salom! Menga YouTube, Instagram yoki TikTok havolasini yuboring, men uni yuklab beraman! 🎬")

@dp.message()
async def handle_video_download(message: types.Message):
    user_text = message.text

    # Faqat havola kelsa ishlaydi
    if any(x in user_text for x in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com"]):
        msg = await message.answer("🎬 Video havola aniqlandi. Yuklashni boshlayapman, kuting...")
        
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'video.mp4',
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([user_text])
            
            # Videoni telegramga yuborish
            video_file = types.FSInputFile('video.mp4')
            await message.answer_video(video=video_file, caption="Mana sizning videongiz! ✨")
            
            # Server to'lib qolmasligi uchun videoni o'chirish
            if os.path.exists('video.mp4'):
                os.remove('video.mp4')
            await msg.delete()

        except Exception as e:
            await message.answer(f"❌ Videoni yuklashda xatolik bo'ldi: {e}")
            if os.path.exists('video.mp4'):
                os.remove('video.mp4')
    else:
        # Link bo'lmagan oddiy gaplarga bot javob bermaydi yoki ogohlantiradi
        await message.answer("⚠️ Iltimos, menga faqat video havolasini (link) yuboring!")

async def main():
    await startup_server()  # Render o'chib qolmasligi uchun shart
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
