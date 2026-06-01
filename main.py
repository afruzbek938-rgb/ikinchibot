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

# Hech qanday kalit talab qilmaydigan ochiq API yuklovchisi
async def download_video_free(url):
    # Bu dunyodagi eng ochiq va tekin yuklash API-laridan biri
    api_url = f"https://api.tikconvert.com/api/download?url={url}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, timeout=15) as res:
                if res.status == 200:
                    data = await res.json()
                    # Instagram, TikTok va YouTube uchun video linkini tekshiramiz
                    if "video" in data:
                        return data.get("video")
                    elif "links" in data and len(data["links"]) > 0:
                        return data["links"][0].get("url")
        except Exception as e:
            print(f"Error: {e}")
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

    if any(x in user_text for x in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com", "facebook.com"]):
        loading_text = "Скачиваю видео автоматически... Пожалуйста, подождите." if is_ru else "Video avtomatik yuklanmoqda... Iltimos, kuting."
        msg = await message.answer(loading_text)
        
        # Bot hech qanday kalitsiz to'g'ridan-to'g'ri qidiradi
        video_url = await download_video_free(user_text)

        if video_url:
            try:
                caption_text = "Готово! ✨" if is_ru else "Tayyor! ✨"
                await message.answer_video(video=video_url, caption=caption_text)
                await msg.delete()
            except Exception:
                fallback_text = (
                    f"📁 Видео найдено, но оно слишком большое. Скачайте напрямую: [Скачать]({video_url})" 
                    if is_ru else 
                    f"📁 Video topildi, lekin hajmi juda katta. Havola orqali yuklang: [Yuklash]({video_url})"
                )
                await message.answer(fallback_text, parse_mode="Markdown")
                await msg.delete()
        else:
            # Agar bu ochiq API ham yuklab bera olmasa, foydalanuvchiga silliqqina zaxira sayt havolasini beradi
            from urllib.parse import quote
            encoded_url = quote(user_text)
            fallback_url = f"https://savefrom.net/?url={encoded_url}"
            
            err_text = (
                f"⚠️ Прямая загрузка сейчас недоступна. Вы можете скачать через сайт: [SaveFrom.net]({fallback_url})"
                if is_ru else
                f"⚠️ To'g'ridan-to'g'ri yuklashning imkoni bo'lmadi. Ushbu sayt orqali yuklab olishingiz mumkin: [SaveFrom.net]({fallback_url})"
            )
            await message.answer(err_text, parse_mode="Markdown")
            await msg.delete()
    else:
        warn_text = "Пожалуйста, отправьте корректную ссылку!" if is_ru else "Iltimos, to'g'ri video havolasini yuboring!"
        await message.answer(warn_text)

async def main():
    await startup_server()  
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
