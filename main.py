import asyncio
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

# Videoni topib beruvchi funksiya
def get_video_stream(url):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info.get('url')
        except:
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

    if not user_text:
        return

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
        loading_text = "📥 Загружаю видео..." if is_ru else "📥 Video yuklanmoqda..."
        msg = await message.answer(loading_text)
        
        loop = asyncio.get_event_loop()
        video_url = await loop.run_in_executor(None, get_video_stream, user_text)

        if video_url:
            try:
                # Shunchaki videoni o'zini yuborish
                await message.answer_video(video=video_url)
                await msg.delete()
            except:
                fallback_text = f"📁 Ссылка: [Скачать]({video_url})" if is_ru else f"📁 Havola: [Yuklash]({video_url})"
                await message.answer(fallback_text, parse_mode="Markdown")
                await msg.delete()
        else:
            err_text = "Не удалось найти видео." if is_ru else "Videoni yuklab bo'lmadi."
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
