import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiohttp import web
from urllib.parse import quote

# 🟢 BOT TOKEN (O'zingiznikini qo'ying)
BOT_TOKEN = "8615110980:AAHl1YLkvZ1Z8qUr45uI3dMwx-lR0lKVp1E"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_languages = {}
# Videolarni eslab qolish uchun vaqtinchalik baza (link -> file_id)
video_database = {}

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
    user_id = message.from_user.id
    
    # 1. Agar boshqa botdan tayyor video FORWARD qilib yuborilsa:
    if message.video:
        file_id = message.video.file_id
        # Bot videoni qabul qilib oladi va sizga uning telegram kodi bilan javob beradi
        reply_text = (
            f"✅ Видео успешно принято! Теперь я могу мгновенно отправлять его.\n`{file_id}`"
            if user_languages.get(user_id) == "ru" else
            f"✅ Video muvaffaqiyatli qabul qilindi! Endi buni srazu yubora olaman.\n`{file_id}`"
        )
        await message.answer(reply_text, parse_mode="MarkdownV2")
        return

    user_text = message.text
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

    # Linklarni tekshirish
    if any(x in user_text for x in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com", "facebook.com"]):
        
        # SIZNING REJANGIZ: Agar bu link oldin bazaga qo'shilgan bo'lsa, srazu tayyor videoni beradi!
        if user_text in video_database:
            caption_text = "Готово! (Из базы) ✨" if is_ru else "Tayyor! (Bazadan) ✨"
            await message.answer_video(video=video_database[user_text], caption=caption_text)
            return

        # Agar bazada bo'lmasa, har doimgidek yuklash havolasini tayyorlaydi
        msg = await message.answer("Обработка ссылки..." if is_ru else "Havola tekshirilmoqda...")
        encoded_url = quote(user_text)
        
        if "instagram.com" in user_text:
            fallback_url = f"https://snapinsta.app/?url={encoded_url}"
            site_name = "SnapInsta"
        elif "tiktok.com" in user_text:
            fallback_url = f"https://ssstik.io/uz?url={encoded_url}"
            site_name = "SSSTik"
        else:
            fallback_url = f"https://savefrom.net/?url={encoded_url}"
            site_name = "SaveFrom"

        fallback_text = (
            f"🚀 [Скачать через {site_name}]({fallback_url})\n\n💡 *Лайфхак:* Вы можете переслать (Forward) готовое видео из другого бота сюда, и я запомню его\!"
            if is_ru else
            f"🚀 [{site_name} orqali yuklash]({fallback_url})\n\n💡 *Layfhak:* Boshqa botdan yuklangan tayyor videoni menga Forward qilib yuborsangiz, eslab qolaman\!"
        )
        await message.answer(fallback_text, parse_mode="MarkdownV2", disable_web_page_preview=True)
        await msg.delete()
    else:
        warn_text = "Пожалуйста, отправьте корректную ссылку!" if is_ru else "Iltimos, to'g'ri video havolasini yuboring!"
        await message.answer(warn_text)

async def main():
    await startup_server()  
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
