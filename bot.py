import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
import yt_dlp

# הגדרת הבוט עם הטוקן שלך
TOKEN = "9250009613:AAH-pjKjixUio9ku6K81HTcW9NtVErnunn8"
bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(F.text.startswith("http"))
async def download_tiktok_video(message: Message):
    url = message.text.strip()
    status_message = await message.answer("⏳ מוריד את הסרטון מטיקטוק, אנא המתן...")

    output_filename = f"tiktok_{message.from_user.id}.mp4"

    ydl_opts = {
        'outtmpl': output_filename,
        'format': 'best',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
    }

    try:
        # הורדת הסרטון באמצעות yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # שליחת הקובץ למשתמש בטלגרם
        from aiogram.types import FSInputFile
        video_file = FSInputFile(output_filename)
        await message.answer_video(video_file)

        # מחיקת הודעת הטעינה
        await status_message.delete()

    except Exception as e:
        await status_message.edit_text("❌ שגיאה בהורדת הסרטון. ודא שהקישור תקין.")

    finally:
        # ניקוי הקובץ המקומי מהמחשב לאחר השליחה
        if os.path.exists(output_filename):
            os.remove(output_filename)


@dp.message()
async def echo_handler(message: Message):
    await message.answer("שלום! שלח לי קישור של סרטון מטיקטוק ואוריד לך אותו.")


async def main():
    print("הבוט רץ וממתין להודעות...")
    await dp.start_polling(bot, polling_timeout=30)


if __name__ == '__main__':
    asyncio.run(main())