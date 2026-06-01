import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web
from urllib.parse import quote

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

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    # Oddiy va tushunarli inline tugmalar bilan til tanlash
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha", callback_data="lang_uz")
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.adjust(2)
    
    await message.answer(
        "🇺🇿 Iltimos, tilni tanlang:\n🇷🇺 Пожалуйста, выберите язык:",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]
    user_languages[user_id] = lang
    
    msg = "O'zbek tili tanlandi! Menga video havolasini (Instagram/YouTube/TikTok) yuboring! 🎬" if lang == "uz" else "Выбран русский язык! Отправьте мне ссылку на видео! 🎬"
    await callback.message.answer(msg)
    await callback.answer()

@dp.message()
async def handle_everything(message: types.Message):
    user_text = message.text
    user_id = message.from_user.id

    if not user_text:
        return

    lang = user_languages.get(user_id, "uz")
    is_ru = lang == "ru"

    # Ijtimoiy tarmoq linklarini tekshiramiz
    if any(x in user_text for x in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com", "facebook.com"]):
        
        encoded_url = quote(user_text)
        
        # Foydalanuvchiga videoni qulay yuklab olishi uchun tugmalar builder-i
        builder = InlineKeyboardBuilder()
        
        if "instagram.com" in user_text:
            builder.button(text="📥 Скачать (SnapInsta)" if is_ru else "📥 Yuklash (SnapInsta)", url=f"https://snapinsta.app/?url={encoded_url}")
            builder.button(text="📥 Альтернатива (SaveFrom)", url=f"https://savefrom.net/?url={encoded_url}")
        elif "tiktok.com" in user_text:
            builder.button(text="📥 Скачать (SSSTik)" if is_ru else "📥 Yuklash (SSSTik)", url=f"https://ssstik.io/uz?url={encoded_url}")
            builder.button(text="📥 Альтернатива (SaveFrom)", url=f"https://savefrom.net/?url={encoded_url}")
        else:
            builder.button(text="📥 Скачать (SaveFrom)" if is_ru else "📥 Yuklash (SaveFrom)", url=f"https://savefrom.net/?url={encoded_url}")
            builder.button(text="📥 Альтернатива (Y2Mate)", url=f"https://y2mate.com/?url={encoded_url}")
            
        builder.adjust(1) # Tugmalarni qatorasiga chiroyli joylash

        reply_text = (
            "✨ **Ваша ссылка успешно обработана\!**\n\nНажмите на кнопку ниже, чтобы быстро и без рекламы скачать видео в один клик:"
            if is_ru else
            "✨ **Videongiz muvaffaqiyatli tayyorlandi\!**\n\nVideoni reklamasiz va tez yuklab olish uchun pastdagi tugmani bosing:"
        )
        
        await message.answer(reply_text, parse_mode="MarkdownV2", reply_markup=builder.as_markup())
    else:
        warn_text = "Пожалуйста, отправьте корректную ссылку!" if is_ru else "Iltimos, to'g'ri video havolasini yuboring!"
        await message.answer(warn_text)

async def main():
    await startup_server()  
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
