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
# Videolarni linkka bog'lash bazasi
video_database = {}
# Admin qaysi videoni yuklaganini vaqtincha eslab turish uchun
admin_waiting_link = {}

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
    
    # 1. BOSHQA BOTDAN VIDEONI FORWARD QILIB YUBORGANINGIZDA:
    if message.video:
        file_id = message.video.file_id
        # Videoni vaqtincha xotiraga olamiz va linkini kutamiz
        admin_waiting_link[user_id] = file_id
        
        await message.answer(
            "📥 **Video qabul qilindi!**\n\nEndi ushbu video qaysi ijtimoiy tarmoq linkiga (Instagram/YouTube/TikTok) tegishli bo'lsa, o'sha linkni menga yuboring. Men ularni bir-biriga ulab qo'yaman! 😉"
        )
        return

    user_text = message.text
    if not user_text:
        return

    # 2. Agar foydalanuvchi til tanlayotgan bo'lsa:
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

    # 3. AGAR SIZ BOYAGI VIDEONING LINKINI YUBORGAN BO'LSANGIZ (Bog'lash jarayoni):
    if user_id in admin_waiting_link and any(x in user_text for x in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com", "facebook.com"]):
        saved_file_id = admin_waiting_link[user_id]
        # Linkni bazaga ulaymiz
        video_database[user_text] = saved_file_id
        # Kutish rejimidan o'chiramiz
        del admin_waiting_link[user_id]
        
        await message.answer("🎉 **Ajoyib! Video va Link muvaffaqiyatli bir-biriga ulandi!**\n\nEndi kim shu linkni botga tashlasa, bot videoni srazu bazadan yuklab beradi!")
        return

    # 4. ODDIY FOYDALANUVChI LINK TASHAGANDA:
    if any(x in user_text for x in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com", "facebook.com"]):
        
        # AGAR BU LINK BAZADA BOR BO'LSA (Siz bog'lagan video srazu uchib boradi):
        if user_text in video_database:
            caption_text = "Готово! ✨" if is_ru else "Tayyor! ✨"
            await message.answer_video(video=video_database[user_text], caption=caption_text)
            return

        # Agar bazada bo'lmasa, har doimgidek zaxira sayt havolasini beradi
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
            f"🚀 [Скачать через {site_name}]({fallback_url})\n\n💡 *Лайфхак:* Перешлите готовое видео из другого бота сюда, а затем отправьте ссылку, чтобы я запомнил её\!"
            if is_ru else
            f"🚀 [{site_name} orqali yuklash]({fallback_url})\n\n💡 *Layfhak:* Boshqa botdan yuklangan tayyor videoni menga Forward qilib yuboring, keyin esa linkini tashlang, men eslab qolaman\!"
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
