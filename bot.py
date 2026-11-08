import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
import yt_dlp

# טוקן הבוט שלך בטלגרם
TOKEN = "9250009613:AAH-pjKjixUio9ku6K81HTcW9NtVErnunn8"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(F.text.startswith("http"))
async def download_media(message: Message):
    url = message.text.strip()
    status_message = await message.answer("⏳ מוריד את המדיה עבורך, אנא המתן...")
    
    output_filename = "downloaded_media.mp4"
    
    # הגדרות yt-dlp כולל ה-User-Agent למניעת חסימות
    ydl_opts = {
        'outtmpl': output_filename,
        'format': 'best',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
    }
    
    try:
        # הורדת הקובץ
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        # שליחת הקובץ לטלגרם
        video_file = FSInputFile(output_filename)
        await message.answer_video(video_file)
        
        # מחיקת הודעת הטעינה
        await status_message.delete()
        
    except Exception as e:
        await status_message.edit_text("❌ שגיאה בהורדת הקובץ. ודא שהקישור תקין וציבורי.")
        
    finally:
        # ניקוי הקובץ המקומי מהשרת אחרי השליחה
        if os.path.exists(output_filename):
            os.remove(output_filename)

@dp.message()
async def echo_handler(message: Message):
    await message.answer("שלום! שלח לי קישור מכל פלטפורמה נתמכת (טיקטוק, פייסבוק וכו') ואוריד לך אותו.")

async def main():
    print("הבוט התחיל לעבוד...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
