import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiohttp import web
import yt_dlp

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
        
        file_name = f"video_{user_id}.mp4"
        
        # O'sha VS Code dagi eng birinchi sozlamalar + Android blockdan o'tish
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': file_name,
            'quiet': True,
            'no_warnings': True,
            # YouTube bloklamasligi uchun telefon brauzeri qiyofasini olamiz:
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                }
            }
        }

        try:
            # Xuddi VS Code dagidek to'g'ridan-to'g'ri yuklash
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([user_text])
            
            if os.path.exists(file_name):
                # Telegram 50MB dan kattasini o'tkazmagani uchun tekshiramiz
                file_size = os.path.getsize(file_name)
                if file_size > 48 * 1024 * 1024:
                    err_size = "Файл слишком большой для отправки (больше 50MB)." if is_ru else "Fayl yuborish uchun juda katta (50MB dan ko'p)."
                    await message.answer(err_size)
                else:
                    video_file = types.FSInputFile(file_name)
                    caption_text = "Готово! ✨" if is_ru else "Tayyor! ✨"
                    await message.answer_video(video=video_file, caption=caption_text)
            else:
                await message.answer("Ошибка при загрузке." if is_ru else "Yuklashda xatolik yuz berdi.")

        except Exception as e:
            await message.answer(f"Error: {e}")
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
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
