import asyncio
import os
import re
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import yt_dlp

# =====================================================================
# TOKENS (BotFather'dan olgan yangi tokeningizni qo'ying)
# =====================================================================
TOKEN = "8615110980:AAHl1YLkvZ1Z8qUr45uI3dMwx-lR0lKVp1E"
# =====================================================================

dp = Dispatcher()
user_data = {}

TEXTS = {
    'uz': {
        'welcome': "👋 *Salom! InstaTubeBot-ga xush kelibsiz!*\n\n📥 Menga **Instagram (Reels), YouTube (Shorts/Video) yoki TikTok** videosining havolasini (linkini) yuboring, men uni sizga tezkor yuklab beraman!",
        'btn_video_mode': "📥 VIDEO YUKLASH",
        'btn_lang': "🌐 TILNI O'ZGARTIRISH",
        'prompt_video': "👇 Havolani yuboring:\n\nMenga video linkini tashlang, men uni yuklab beraman.",
        'error': "⚠️ Yuklashda xatolik yuz berdi. Havola to'g'riligini tekshiring yoki video yopiq profilda bo'lishi mumkin.",
        'remind': "💡 *Eslatma:* Iltimos, menga Instagram, YouTube yoki TikTok video havolasini yuboring!"
    },
    'ru': {
        'welcome': "👋 *Привет! Добро пожаловать в InstaTubeBot!*\n\n📥 Отправьте мне ссылку на видео из **Instagram (Reels), YouTube (Shorts/Видео) или TikTok**, и я скачаю его для вас!",
        'btn_video_mode': "📥 СКАЧАТЬ ВИДЕО",
        'btn_lang': "🌐 СМЕНИТЬ ЯЗЫК",
        'prompt_video': "👇 Отправьте ссылку:\n\nПришлите мне ссылку на видео, и я его скачаю.",
        'error': "⚠️ Ошибка при загрузке. Проверьте ссылку или видео может быть в закрытом профиле.",
        'remind': "💡 *Напоминание:* Пожалуйста, отправьте мне ссылку на видео из Instagram, YouTube или TikTok!"
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}

# --- 📹 VIDEO YUKLASH ENGINE ---
async def download_video(url: str):
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": "downloads/vid_%(id)s.%(ext)s",
        "quiet": True,
        "ignoreerrors": True,
        "http_headers": HEADERS
    }
    loop = asyncio.get_event_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            if info:
                video_id = info.get("id")
                ext = info.get("ext", "mp4")
                file_path = f"downloads/vid_{video_id}.{ext}"
                if os.path.exists(file_path):
                    return {"file_path": file_path, "title": info.get("title", "Video"), "id": video_id}
    except Exception as e:
        print("VIDEO ERROR:", e)
    return None

# --- 🎵 AUDIO AJRATISH ENGINE (MP3 TUGMASI UCHUN) ---
async def download_audio_from_url(url: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/aud_%(id)s.%(ext)s",
        "quiet": True,
        "http_headers": HEADERS
    }
    loop = asyncio.get_event_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            if info:
                file_path = f"downloads/aud_{info.get('id')}.{info.get('ext', 'mp3')}"
                if os.path.exists(file_path):
                    return {"file_path": file_path, "title": info.get("title", "Audio"), "performer": "InstaTubeBot"}
    except Exception as e:
        print("AUDIO ERROR:", e)
    return None

# --- KLAVIATURALAR ---
def get_main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TEXTS[lang]['btn_video_mode'])],
            [KeyboardButton(text=TEXTS[lang]['btn_lang'])]
        ],
        resize_keyboard=True
    )

def get_lang_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")]], resize_keyboard=True)

# --- INLINE CALLBACK (MP3 tugmasi bosilganda) ---
@dp.callback_query(F.data.startswith("getmp3_"))
async def process_callback_mp3(callback_query: CallbackQuery):
    await callback_query.answer("🎵 Videodan MP3 ajratib olinmoqda...")
    video_id = callback_query.data.split("_")[1]
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    if len(video_id) != 11: 
        url = callback_query.message.reply_to_message.text if callback_query.message.reply_to_message else f"https://instagram.com/p/{video_id}"

    track_info = await download_audio_from_url(url)
    if track_info and os.path.exists(track_info['file_path']):
        audio_file = FSInputFile(track_info['file_path'])
        await callback_query.message.reply_audio(audio=audio_file, title=track_info['title'], performer=track_info['performer'])
        os.remove(track_info['file_path'])
    else:
        await callback_query.message.reply("⚠️ Afsuski, ushbu videodan audio ajratib bo'lmadi.")

# --- HANDLERS ---
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    chat_id = message.chat.id
    user_data[chat_id] = {'lang': None}
    await message.reply(text="🤖 *Tilni tanlang / Выберите язык:*", reply_markup=get_lang_keyboard(), parse_mode=ParseMode.MARKDOWN)

@dp.message(F.text)
async def handle_message(message: Message):
    chat_id = message.chat.id
    text = message.text

    if chat_id not in user_data: user_data[chat_id] = {'lang': 'uz'}
    
    if text == "🇺🇿 O'zbekcha":
        user_data[chat_id]['lang'] = 'uz'
        await message.reply(TEXTS['uz']['welcome'], reply_markup=get_main_keyboard('uz'), parse_mode=ParseMode.MARKDOWN)
        return
    elif text == "🇷🇺 Русский":
        user_data[chat_id]['lang'] = 'ru'
        await message.reply(TEXTS['ru']['welcome'], reply_markup=get_main_keyboard('ru'), parse_mode=ParseMode.MARKDOWN)
        return

    lang = user_data[chat_id]['lang'] if user_data[chat_id]['lang'] else 'uz'

    # --- 🔗 HAVOLA KELGANDA ISHLASH ---
    url_match = re.search(r'(https?://[^\s]+)', text)
    if url_match:
        url = url_match.group(1)
        if any(x in url for x in ["instagram.com", "youtube.com", "youtu.be", "tiktok.com"]):
            wait_msg = await message.reply("⏳ *Video yuklanmoqda...*")
            video_info = await download_video(url)
            
            if video_info and os.path.exists(video_info['file_path']):
                await wait_msg.delete()
                
                short_id = video_info['id'] if video_info['id'] else text[-10:]
                inline_kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🎵 Musiqasini yuklash (MP3)", callback_data=f"getmp3_{short_id}")]
                ])
                
                video_file = FSInputFile(video_info['file_path'])
                await message.reply_video(video=video_file, caption=f"📹 *{video_info['title']}*", reply_markup=inline_kb, parse_mode=ParseMode.MARKDOWN)
                os.remove(video_info['file_path'])
            else:
                await wait_msg.edit_text(TEXTS[lang]['error'])
            return

    # --- 🎛 MENYU TUGMALARI ---
    if text in [TEXTS['uz']['btn_video_mode'], TEXTS['ru']['btn_video_mode']]:
        await message.reply(TEXTS[lang]['prompt_video'], parse_mode=ParseMode.MARKDOWN)
        return
    elif text in ["🌐 TILNI O'ZGARTIRISH", "🌐 СМЕНИТЬ ЯЗЫК"]:
        await message.reply("🤖 *Tilni tanlang / Выберите язык:*", reply_markup=get_lang_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    else:
        await message.reply(TEXTS[lang]['remind'], parse_mode=ParseMode.MARKDOWN)

async def main() -> None:
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
