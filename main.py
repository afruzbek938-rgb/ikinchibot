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

# Videoni avtomatik qidirib topuvchi yangi barqaror server
async def auto_fetch_video(url):
    # Bu ochiq va hozir faol bo'lgan muqobil yuklovchi API
    api_url = "https://corsproxy.io/?https://api.v01.es/api/download"
    payload = {"url": url}
    
    # Agar v01 mutlaqo o'chgan bo'lsa, zaxira barqaror API
    backup_url = "https://api.cobalt.tools/api/json"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1-Urinish: Proxy orqali xavfsiz yuklash
            async with session.post(api_url, json=payload, timeout=15) as res:
                if res.status == 200:
                    data = await res.json()
                    if "links" in data and len(data["links"]) > 0:
                        return data["links"][0].get("url")
        except:
            pass

        try:
            # 2-Urinish: Zaxira Cobalt tizimi
            headers = {"Accept": "application/json", "Content-Type": "application/json"}
            async with session.post(backup_url, json={"url": url, "vQuality": "720"}, headers=headers, timeout=15) as res:
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

    if any(x in user_text for x in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com", "facebook.com"]):
        loading_text = "Поиск видео... Пожалуйста, подождите." if is_ru else "Video qidirilmoqda... Iltimos, kuting."
        msg = await message.answer(loading_text)
        
        # Bot hech qanday yordamsiz o'zi qidiradi
        video_url = await auto_fetch_video(user_text)

        if video_url:
            try:
                caption_text = "Готово! ✨" if is_ru else "Tayyor! ✨"
                # To'g'ridan-to'g'ri yuborish
                await message.answer_video(video=video_url, caption=caption_text)
                await msg.delete()
            except Exception:
                # Agar video Telegram limiti (50MB) dan katta bo'lsa, silliqqina ko'k havola beradi
                fallback_text = (
                    f"📁 Видео найдено, но оно слишком большое. Скачайте напрямую: [Скачать]({video_url})" 
                    if is_ru else 
                    f"📁 Video topildi, lekin hajmi juda katta. Havola orqali yuklang: [Yuklash]({video_url})"
                )
                await message.answer(fallback_text, parse_mode="Markdown")
                await msg.delete()
        else:
            err_text = "Не удалось автоматически найти видео. Попробуйте другую ссылку." if is_ru else "Videoni avtomatik topib bo'lmadi. Boshqa havola yuborib ko'ring."
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
