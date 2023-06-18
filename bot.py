import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from PCSOLotto_Webscraper.PCSOLottoWebscraper import PCSOLottoWebscraper
from PCSOLotto import PCSOLotto

# Load environment variables
load_dotenv()

telegram_token = os.getenv("TOKEN")

# Initialize the PCSOLottoWebscraper
lotto_webscraper = PCSOLottoWebscraper()

# Define the /start command handler
def start(update: Update, context):
    # Greet the user with their username
    user = update.message.from_user
    welcome_message = f"Hello, {user.username}! Welcome to our bot. \n\nWe are able to generate PCSO Lotto Results. " \
                      f"You can also receive daily result updates from us. \n\nLet's have fun with the lotto! \n\n" \
                      f"\u00A9 Alfie Superhalk"
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

# Define the /results command handler
def results(update: Update, context):
    # Get the latest PCSO lotto results
    latest_results = lotto_webscraper.get_latest_results()

    # Send the results as a message
    context.bot.send_message(chat_id=update.effective_chat.id, text=latest_results)

# Define the chat handler
def chat(update: Update, context):
    # Get the user's message
    message = update.message.text

    # Echo the user's message
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def main():
    # Create the Updater and pass in the bot's token
    updater = Updater(token=telegram_token, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the /start command handler
    dispatcher.add_handler(CommandHandler("start", start))

    # Register the /results command handler
    dispatcher.add_handler(CommandHandler("results", results))

    # Register the chat handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, chat))

    # Start the bot
    updater.start_polling()

    # Run the bot until Ctrl-C is pressed
    updater.idle()

if __name__ == '__main__':
    main()
