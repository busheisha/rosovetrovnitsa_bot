import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import messages

from rozovetrovnitsa import create_windrose
from rozovetrovnitsa import create_smartrose
from rozovetrovnitsa import create_temperature
from rozovetrovnitsa import create_rain

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
        file_path = f'bot/files/{update.effective_user.id}.xls.gz'
        third_image_path = f'bot/files/images/{update.effective_user.id}1.jpg'
        second_image_path = f'bot/files/images/{update.effective_user.id}0.jpg'
        first_image_path = f'bot/files/images/{update.effective_user.id}.jpg'
        fourth_image_path = f'bot/files/images/{update.effective_user.id}2.jpg'

        file = await update.message.document.get_file()
        await file.download_to_drive(custom_path=file_path)
        await update.message.reply_photo(create_windrose(file_path, first_image_path))
        await update.message.reply_photo(create_smartrose(file_path, second_image_path))
        await update.message.reply_photo(create_temperature(file_path, third_image_path))
        await update.message.reply_photo(create_rain(file_path, fourth_image_path))
        await update.message.reply_text(text= messages.ROSE_MESSAGE)


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