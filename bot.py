import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
import yt_dlp

TOKEN = "9250009613:AAH-pjKjixUio9ku6K81HTcW9NtVErnunn8"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# מילון זמני לשמירת הקישורים לפי משתמש בזמן שהם בוחרים איכות
user_links = {}

@dp.message(F.text.startswith("http"))
async def ask_quality(message: Message):
    url = message.text.strip()
    user_id = message.from_user.id
    user_links[user_id] = url
    
    # יצירת מקלדת כפתורים לבחירת איכות
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 איכות גבוהה (Best)", callback_data="quality_best")],
        [InlineKeyboardButton(text="📱 איכות נמוכה (Mobile/Low)", callback_data="quality_low")],
        [InlineKeyboardButton(text="🎵 קובץ אודיו בלבד (MP3)", callback_data="quality_audio")]
    ])
    
    await message.answer("בחר את איכות ההורדה הרצויה:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("quality_"))
async def process_quality_choice(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_links:
        await callback.message.edit_text("❌ פג תוקף הבקשה. אנא שלח את הקישור מחדש.")
        return
        
    url = user_links[user_id]
    choice = callback.data.split("_")[1]
    
    await callback.message.edit_text("⏳ מוריד את הקובץ לפי ההגדרה שבחרת, אנא המתן...")
    
    # הגדרות בהתאם לבחירת המשתמש
    if choice == "best":
        output_filename = "downloaded_media.mp4"
        ydl_opts = {
            'outtmpl': output_filename,
            'format': 'best',
            'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
        }
    elif choice == "low":
        output_filename = "downloaded_media.mp4"
        ydl_opts = {
            'outtmpl': output_filename,
            'format': 'worst',
            'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
        }
    else:  # audio
        output_filename = "downloaded_audio.mp3"
        ydl_opts = {
            'outtmpl': 'downloaded_audio.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if choice == "audio":
                # מציאת שם הקובץ המדויק שנוצר עבור האודיו
                filename = ydl.prepare_filename(info)
                output_filename = os.path.splitext(filename)[0] + ".mp3"
                
            file_to_send = FSInputFile(output_filename)
            
            if choice == "audio":
                await callback.message.answer_audio(file_to_send)
            else:
                await callback.message.answer_video(file_to_send)
                
            await callback.message.delete()
            
    except Exception as e:
        await callback.message.edit_text("❌ שגיאה בהורדת הקובץ. ודא שהקישור תקין וציבורי.")
        
    finally:
        if os.path.exists(output_filename):
            os.remove(output_filename)
        if user_id in user_links:
            del user_links[user_id]

@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("שלום! שלח לי קישור מכל פלטפורמה נתמכת ואתן לך לבחור את איכות ההורדה.")

@dp.message()
async def echo_handler(message: Message):
    await message.answer("שלום! שלח לי קישור תקין (המתחיל ב-http) כדי להתחיל בהורדה.")

async def main():
    print("הבוט התחיל לעבוד...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
