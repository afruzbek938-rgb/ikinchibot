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

    if any(x in user_text for x in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com", "facebook.com"]):
        loading_text = "Обработка ссылки... Пожалуйста, подождите." if is_ru else "Havola tekshirilmoqda... Iltimos, kuting."
        msg = await message.answer(loading_text)
        
        # O'sha siz aytgan eng birinchi ishlagan ishonchli API tizimi
        api_url = "https://api.v01.es/api/download"
        payload = {"url": user_text}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, timeout=20) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        video_url = None
                        if "links" in data and len(data["links"]) > 0:
                            video_url = data["links"][0].get("url")
                        elif "url" in data:
                            video_url = data.get("url")
                        
                        if video_url:
                            file_name = f"download_{user_id}.mp4"
                            try:
                                # O'sha sizga yoqqan qism: videoni serverga yuklab olamiz
                                async with session.get(video_url, timeout=45) as video_res:
                                    if video_res.status == 200:
                                        with open(file_name, 'wb') as f:
                                            f.write(await video_res.read())
                                
                                # Videoni telegramga toza fayl qilib yuboramiz
                                video_file = types.FSInputFile(file_name)
                                caption_text = "Готово! ✨" if is_ru else "Tayyor! ✨"
                                await message.answer_video(video=video_file, caption=caption_text)
                            
                            except Exception:
                                # Agar video juda katta bo'lsa va yuklashda xato bersa, srazu linkini beradi
                                fallback_text = (
                                    f"📁 Видео слишком большое. Скачайте напрямую: [Скачать]({video_url})" 
                                    if is_ru else 
                                    f"📁 Video juda katta. Havola orqali yuklab oling: [Yuklash]({video_url})"
                                )
                                await message.answer(fallback_text, parse_mode="Markdown")
                            finally:
                                # Serverda fayl qolib ketmasligi uchun o'chiramiz
                                if os.path.exists(file_name):
                                    os.remove(file_name)
                        else:
                            await message.answer("Ошибка: Видео не найдено." if is_ru else "Xatolik: Video topilmadi.")
                    else:
                        await message.answer("Сервис занят. Попробуйте еще раз." if is_ru else "Server band. Birozdan so'ng urinib ko'ring.")
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
