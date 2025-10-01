import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import messages

from rozovetrovnitsa import *
from decouple import config

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(messages.START_MESSAGE)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(messages.HELP_MESSAGE)


async def rose(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        
        # Пути к файлам
        input_file_path = f'bot/files/{user_id}.xls.gz'
        windrose_path = f'bot/files/images/{user_id}_windrose.jpg'
        temperature_path = f'bot/files/images/{user_id}_temperature.jpg'
        rain_path = f'bot/files/images/{user_id}_rain.jpg'
        
        # Закомментированные пути для раздельных роз
        # simple_windrose_path = f'bot/files/images/{user_id}_simple_windrose.jpg'
        # smart_windrose_path = f'bot/files/images/{user_id}_smart_windrose.jpg'

        file = await update.message.document.get_file()
        await file.download_to_drive(custom_path=input_file_path)
        
        await update.message.reply_photo(create_combined_rose(input_file_path, windrose_path))
        # await update.message.reply_photo(create_windrose(input_file_path, simple_windrose_path))
        # await update.message.reply_photo(create_smartrose(input_file_path, smart_windrose_path))
        await update.message.reply_photo(create_temperature(input_file_path, temperature_path))
        await update.message.reply_photo(create_rain(input_file_path, rain_path))
        
        await update.message.reply_text(text=messages.ROSE_MESSAGE)


def main() -> None:
    """Start the bot."""
    TOKEN = config('TG_TOKEN')

    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.Document.ALL, rose))


    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()