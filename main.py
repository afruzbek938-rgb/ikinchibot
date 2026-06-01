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

# 🔥 AVTOMATIK BAZA: Bot videolarni (link -> file_id) shaklida o'zi eslab qoladi
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

# To'g'ridan-to'g'ri video oqimi linkini olish
def extract_direct_url(url):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info.get('url')
        except Exception as e:
            print(f"YTDL Error: {e}")
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
        
        # 1-QADAM: Bot bazani tekshiradi. Agar bu link oldin so'ralgan bo'lsa, srazu videoni beradi!
        if user_text in video_database:
            caption_text = "Готово! (Из базы) 🚀" if is_ru else "Tayyor! (Bazadan olindi) 🚀"
            try:
                await message.answer_video(video=video_database[user_text], caption=caption_text)
                return
            except Exception:
                # Agar bazadagi file_id eskorgan bo'lsa, pastdagi kodga o'tib qayta yuklaydi
                pass

        # 2-QADAM: Agar link bazada yo'l bo'lsa, internetdan qidiradi
        loading_text = "📥 Загружаю видео... Пожалуйста, подождите." if is_ru else "📥 Video yuklanmoqda... Iltimos, kuting."
        msg = await message.answer(loading_text)
        
        loop = asyncio.get_event_loop()
        direct_video_url = await loop.run_in_executor(None, extract_direct_url, user_text)

        if direct_video_url:
            try:
                caption_text = "Готово! (Сохранено в базу) ✨" if is_ru else "Tayyor! (Bazaga saqlandi) ✨"
                
                # Videoni yuboramiz va Telegram qaytargan xabarni o'zgaruvchiga olamiz
                sent_message = await message.answer_video(video=direct_video_url, caption=caption_text)
                
                # 🔥 MANA SHU YERDA MO'JIZA: Bot yuborilgan videoning yashirin ID kodini bazaga avtomatik yozib qo'yadi!
                if sent_message.video:
                    video_database[user_text] = sent_message.video.file_id
                
                await msg.delete()
            except Exception:
                fallback_text = (
                    f"📁 Видео слишком большое. Ссылка: [Скачать]({direct_video_url})" 
                    if is_ru else 
                    f"📁 Video hajmi juda katta. Havola: [Yuklash]({direct_video_url})"
                )
