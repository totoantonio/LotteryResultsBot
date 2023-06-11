import os
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

# Telegram API token from the environment variable
TOKEN = os.environ.get('6193225487:AAE7PXJICy_lUsYjq8iH5ry5sPRWwSrBFaM')

# Command handler for the /start command
def start_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = "Welcome to the Lottery Result Bot! Subscribe to receive real-time lottery results."
    context.bot.send_message(chat_id=chat_id, text=message)

# Command handler for the /subscribe command
def subscribe_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    # Add the chat ID to the list of subscribers
    # Implement your own logic to maintain a list of subscribers
    # You can use a database or a file to store the chat IDs
    # For simplicity, let's assume we have a list called "subscribers" for now
    subscribers.append(chat_id)
    message = "You have been subscribed to receive lottery results."
    context.bot.send_message(chat_id=chat_id, text=message)

# Command handler for the /unsubscribe command
def unsubscribe_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    # Remove the chat ID from the list of subscribers
    # Implement your own logic to remove the chat ID from the subscribers list
    # For simplicity, let's assume we have a list called "subscribers" for now
    if chat_id in subscribers:
        subscribers.remove(chat_id)
    message = "You have been unsubscribed from receiving lottery results."
    context.bot.send_message(chat_id=chat_id, text=message)

# Function to fetch lottery results
def fetch_lottery_results():
    # Implement your logic to fetch real-time lottery results
    # Return the formatted lottery results as a string
    # For this example, let's assume we have fetched results and stored it in the "results" variable
    results = "Lottery Results:\n- Result 1\n- Result 2\n- Result 3"
    return results

# Function to send lottery results to subscribers
def send_lottery_results(context: CallbackContext):
    results = fetch_lottery_results()
    for chat_id in subscribers:
        context.bot.send_message(chat_id=chat_id, text=results)

def main():
    # Create the bot and updater
    bot = Bot(token=TOKEN)
    updater = Updater(bot=bot)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe_command))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe_command))

    # Start the lottery results scheduler
    job_queue = updater.job_queue
    job_queue.run_repeating(send_lottery_results, interval=60, first=0)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    subscribers = []  # List to store subscribers' chat IDs
    main()
