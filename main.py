import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiohttp import web
import aiohttp

# 🟢 BOT TOKEN (O'zingiznikini qo'ying)
BOT_TOKEN = "8615110980:AAHl1YLkvZ1Z8qUr45uI3dMwx-lR0lKVp1E"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_languages = {}

async def startup_server():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

def get_lang_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha")
    builder.button(text="🇷🇺 Русский")
    return builder.as_markup(resize_keyboard=True)

# API lardan video linkini olish
async def fetch_video_url(url):
    apis = [
        "https://api.all-in-one-downloader.workers.dev/api/download",
        "https://api.cobalt.tools/api/json"
    ]
    
    async with aiohttp.ClientSession() as session:
        # 1-API ni tekshirish
        try:
            async with session.post(apis[0], json={"url": url}, timeout=15) as res:
                if res.status == 200:
                    data = await res.json()
                    if "links" in data and len(data["links"]) > 0:
                        return data["links"][0].get("url")
        except:
            pass
            
        # 2-API ni tekshirish
        try:
            headers = {"Accept": "application/json", "Content-Type": "application/json"}
            async with session.post(apis[1], json={"url": url, "vQuality": "720"}, headers=headers, timeout=15) as res:
                if res.status == 200:
                    data = await res.json()
                    return data.get("url")
        except:
            pass
            
    return None

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "🇺🇿 Iltimos, tilni tanlang:\n🇷🇺 Пожалуйста, выберите язык:",
        reply_markup=get_lang_keyboard()
    )

@dp.message()
async def handle_everything(message: types.Message):
    user_text = message.text
    user_id = message.from_user.id

    if user_text == "🇺🇿 O'zbekcha":
        user_languages[user_id] = "uz"
        await message.answer("O'zbek tili tanlandi! Menga video havolasini yuboring! 🎬")
        return
    elif user_text == "🇷🇺 Русский":
        user_languages[user_id] = "ru"
        await message.answer("Выбран русский язык! Отправьте мне ссылку на видео! 🎬")
        return

    lang = user_languages.get(user_id, "uz")
    is_ru = lang == "ru"

    if any(x in user_text for x in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com"]):
        loading_text = "Обработка ссылки... Пожалуйста, подождите." if is_ru else "Havola tekshirilmoqda... Iltimos, kuting."
        msg = await message.answer(loading_text)
        
        # Sifati zo'r video linkini olamiz
        video_url = await fetch_video_url(user_text)

        if video_url:
            file_name = f"video_{user_id}.mp4"
            try:
                # Videoni Render serverining o'ziga yuklab olamiz (Xatolik bo'lmasligi uchun)
                async with aiohttp.ClientSession() as session:
                    async with session.get(video_url, timeout=60) as response:
                        if response.status == 200:
                            with open(file_name, 'wb') as f:
                                f.write(await response.read())
                
                # Videoni haqiqiy fayl ko'rinishida Telegramga yuboramiz
                video_file = types.FSInputFile(file_name)
                caption_text = "Готово! ✨" if is_ru else "Tayyor! ✨"
                await message.answer_video(video=video_file, caption=caption_text)
                
            except Exception as e:
                error_msg = f"Ошибка при отправке: {e}" if is_ru else f"Yuborishda xatolik: {e}"
                await message.answer(error_msg)
            finally:
                # Server to'lib qolmasligi uchun faylni darhol o'chiramiz
                if os.path.exists(file_name):
                    os.remove(file_name)
                await msg.delete()
        else:
            err_text = "Не удалось скачать видео. Попробуйте позже." if is_ru else "Videoni yuklab bo'lmadi. Birozdan so'ng urinib ko'ring."
            await message.answer(err_text)
            await msg.delete()
                
    else:
        warn_text = "Пожалуйста, отправьте корректную ссылку!" if is_ru else "Iltimos, to'g'ri video havolasini yuboring!"
        await message.answer(warn_text)

async def main():
    await startup_server()  
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
