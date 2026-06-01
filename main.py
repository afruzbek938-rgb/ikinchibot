import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiohttp import web
import aiohttp

# 🟢 BOT TOKEN (O'zingiznikini qo'ying)
BOT_TOKEN = "8615110980:AAHl1YLkvZ1Z8qUr45uI3dMwx-lR0lKVp1E"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Foydalanuvchilarni qaysi tilni tanlaganini eslab qolish uchun vaqtinchalik ombor
user_languages = {}

async def startup_server():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

# Til tanlash tugmalarini yaratish funksiyasi
def get_lang_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha")
    builder.button(text="🇷🇺 Русский")
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    # Botga kirganda darhol til tanlash tugmalarini ko'rsatamiz
    await message.answer(
        "🇺🇿 Iltimos, tilni tanlang:\n🇷🇺 Пожалуйста, выберите язык:",
        reply_markup=get_lang_keyboard()
    )

@dp.message()
async def handle_everything(message: types.Message):
    user_text = message.text
    user_id = message.from_user.id

    # 1. Agar foydalanuvchi til tugmalaridan birini bossan:
    if user_text == "🇺🇿 O'zbekcha":
        user_languages[user_id] = "uz"
        await message.answer("O'zbek tili tanlandi! Menga video havolasini yuboring! 🎬")
        return
    elif user_text == "🇷🇺 Русский":
        user_languages[user_id] = "ru"
        await message.answer("Выбран русский язык! Отправьте мне ссылку на видео! 🎬")
        return

    # Foydalanuvchi tanlagan tilni aniqlaymiz (agar tanlamagan bo'lsa, o'zbekcha default bo'ladi)
    lang = user_languages.get(user_id, "uz")
    is_ru = lang == "ru"

    # 2. Video havola kelsa yuklash qismi:
    if any(x in user_text for x in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com"]):
        loading_text = "Обработка ссылки... Пожалуйста, подождите." if is_ru else "Havola tekshirilmoqda... Iltimos, kuting."
        msg = await message.answer(loading_text)
        
        api_url = "https://api.all-in-one-downloader.workers.dev/api/download"
        payload = {"url": user_text}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        video_url = None
                        if "links" in data and len(data["links"]) > 0:
                            video_url = data["links"][0].get("url")
                        
                        if video_url:
                            caption_text = "Готово! ✨" if is_ru else "Tayyor! ✨"
                            await message.answer_video(video=video_url, caption=caption_text)
                        else:
                            err_text = "Ошибка: Видео не найдено." if is_ru else "Xatolik: Video topilmadi."
                            await message.answer(err_text)
                    else:
                        busy_text = "Сервис занят. Попробуйте позже." if is_ru else "Server band. Birozdan so'ng urinib ko'ring."
                        await message.answer(busy_text)
            await msg.delete()

        except Exception as e:
            error_msg = "Ошибка при загрузке." if is_ru else "Yuklashda xatolik yuz berdi."
            await message.answer(error_msg)
            try:
                await msg.delete()
            except:
                pass
                
    # 3. Agar havola ham bo'lmasa, til ham tanlanmasa, shunchaki ogohlantiramiz:
    else:
        warn_text = "Пожалуйста, отправьте корректную ссылку!" if is_ru else "Iltimos, to'g'ri video havolasini yuboring!"
        await message.answer(warn_text)

async def main():
    await startup_server()  
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
