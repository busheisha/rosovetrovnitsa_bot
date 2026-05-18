import asyncio
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import messages

from rozovetrovnitsa import *
from decouple import config

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

REPROACH_USER_IDS = {
    int(uid.strip())
    for uid in config("REPROACH_LIST", default="").split(",")
    if uid.strip()
}


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
    reproach = user_id in REPROACH_USER_IDS

    input_file_path = f'bot/files/{user_id}.xls.gz'
    windrose_path = f'bot/files/images/{user_id}_windrose.jpg'
    temperature_path = f'bot/files/images/{user_id}_temperature.jpg'
    rain_path = f'bot/files/images/{user_id}_rain.jpg'

    try:
        file = await update.message.document.get_file()
        await file.download_to_drive(custom_path=input_file_path)
        is_valid, message = validate_meteo_file(input_file_path)
        if not is_valid:
            await update.message.reply_text(message)
            if os.path.exists(input_file_path):
                os.remove(input_file_path)
            return

        if reproach:
            await update.message.reply_text(messages.REPROACH_MESSAGE)
            await asyncio.sleep(20)

        try:
            await update.message.reply_photo(
                create_combined_rose(input_file_path, windrose_path)
            )
        except Exception as e:
            logging.warning("reply_photo (роза ветров): %s", e)
            await update.message.reply_text(
                "Извините, я почему-то не смогла отправить розу ветров. Может быть, в архиве не было ветра? Проверьте, пожалуйста, что он именно с метеостанции/из аэропорта, а не с метеодатчика🫠"
            )

        if reproach:
            await asyncio.sleep(10)

        try:
            await update.message.reply_photo(
                create_temperature(input_file_path, temperature_path)
            )
        except Exception as e:
            logging.warning("reply_photo (температура): %s", e)
            await update.message.reply_text(
                "Почему-то я не смогла сделать график температуры((Хз почему, напишите Бушейше."
            )

        if reproach:
            await asyncio.sleep(10)

        try:
            await update.message.reply_photo(create_rain(input_file_path, rain_path))
        except Exception as e:
            logging.warning("reply_photo (осадки): %s", e)
            await update.message.reply_text(
                "Что-то не ладится с графиком осадков... Надеюсь, он был Вам не очень нужен -- в любом случае, если что, напишите Бушейше."
            )
        try:
            await update.message.reply_text(text=tell_verdict(input_file_path))
        except Exception:
            await update.message.reply_text(
                "Что-то не ладится с эффективными температурами... Надеюсь, они Вам не очень нужны -- в любом случае, если что, напишите Бушейше."
            )
        await update.message.reply_text(text=messages.ROSE_MESSAGE)
    except Exception as e:
        await update.message.reply_text(text=f"❌ Ошибка при обработке файла: {e}")
        if os.path.exists(input_file_path):
            os.remove(input_file_path)



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