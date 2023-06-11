import os
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = os.environ.get('6193225487:AAE7PXJICy_lUsYjq8iH5ry5sPRWwSrBFaM')

def start_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = "Welcome to the Lottery Result Bot! Subscribe to receive real-time lottery results."
    context.bot.send_message(chat_id=chat_id, text=message)

def unknown_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = "Sorry, I didn't understand that command."
    context.bot.send_message(chat_id=chat_id, text=message)

def main():
    bot = Bot(token='6193225487:AAE7PXJICy_lUsYjq8iH5ry5sPRWwSrBFaM')
    updater = Updater(bot=bot, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", start_command))
    dispatcher.add_handler(CommandHandler("unknown", unknown_command))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
