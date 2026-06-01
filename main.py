import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web
import aiohttp

# 🟢 BOT TOKEN (O'zingiznikini qo'ying)
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
    # Har doim foydalanuvchi tiliga qarab javob beradi (uz yoki ru)
    if message.from_user.language_code == "ru":
        await message.answer("Отправьте мне ссылку на видео из YouTube, Instagram или TikTok!")
    else:
        await message.answer("Menga YouTube, Instagram yoki TikTok video havolasini yuboring!")

@dp.message()
async def handle_video_download(message: types.Message):
    user_text = message.text
    is_ru = message.from_user.language_code == "ru"

    if any(x in user_text for x in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com"]):
        loading_text = "Обработка ссылки... Пожалуйста, подождите." if is_ru else "Havola tekshirilmoqda... Iltimos, kuting."
        msg = await message.answer(loading_text)
        
        api_url = f"https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": user_text,
            "vQuality": "720"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        video_url = data.get("url")
                        
                        if video_url:
                            caption_text = "Готово! ✨" if is_ru else "Tayyor! ✨"
                            await message.answer_video(video=video_url, caption=caption_text)
                        else:
                            err_text = "Ошибка: Не удалось найти видео." if is_ru else "Xatolik: Videoni topib bo'lmadi."
                            await message.answer(err_text)
                    else:
                        busy_text = "Сервис временно занят. Попробуйте еще раз." if is_ru else "Server band. Birozdan so'ng urinib ko'ring."
                        await message.answer(busy_text)
            await msg.delete()

        except Exception as e:
            await message.answer(f"Error: {e}")
            try:
                await msg.delete()
            except:
                pass
    else:
        warn_text = "Пожалуйста, отправьте корректную ссылку!" if is_ru else "Iltimos, to'g'ri video havolasini yuboring!"
        await message.answer(warn_text)

async def main():
    await startup_server()  
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
