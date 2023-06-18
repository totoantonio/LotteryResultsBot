from bs4 import BeautifulSoup
import calendar
from datetime import datetime, timedelta
import requests
from prettytable import PrettyTable
import os
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler, Updater

# Load environment variables from .env file
load_dotenv()

class PCSOLotto:
    def __init__(self, link='https://www.pcso.gov.ph/SearchLottoResult.aspx'):
        self.link = link
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'
        }
        self.games_list = {
            58: 'Ultra Lotto 6/58',
            55: 'Grand Lotto 6/55',
            49: 'Superlotto 6/49',
            45: 'Megalotto 6/45',
            42: 'Lotto 6/42',
            6: '6D Lotto',
            4: '4D Lotto',
            33: '3D Lotto 2PM',
            32: '3D Lotto 5PM',
            31: '3D Lotto 9PM',
            23: '2D Lotto 11AM',
            22: '2D Lotto 4PM',
            21: '2D Lotto 9PM'
        }

    def download_page(self):
        '''Retrieves the BeautifulSoup4 object that contains the page HTML'''
        with requests.Session() as session:
            response = session.get(self.link, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup

    def scrape_results(self, start_month, start_year, end_month, end_year):
        """Scrapes the lottery results for the given date range."""
        # Format the start and end dates
        start_date = f'{start_month:02d}-01-{start_year}'
        end_date = f'{end_month:02d}-{calendar.monthrange(end_year, end_month)[1]}-{end_year}'

        # Prepare the request payload
        payload = {
            'ddlStartMonth': start_month,
            'ddlStartYear': start_year,
            'ddlEndMonth': end_month,
            'ddlEndYear': end_year,
            'btnSearch': 'Search'
        }

        # Send a POST request to retrieve the page with the results
        response = requests.post(self.link, headers=self.headers, data=payload)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table containing the results
        table = soup.find('table', {'class': 'Grid search-lotto-result-table'})

        if table is None:
            # Handle case when table is not found
            print('Table not found.')
            return {}

        rows = table.find_all('tr')

        # Initialize an empty dictionary to store the results
        results = {}

        # Iterate over the table rows, skipping the header row
        for row in rows[1:]:
            columns = row.find_all('td')
            game_name = columns[0].text.strip()
            result = columns[1].text.strip()
            jackpot = columns[3].text.strip()
            winners = columns[4].text.strip()
            jackpot_date = columns[2].text.strip()

            # Store the result in the dictionary
            results[game_name] = {
                'Result': result,
                'Jackpot': jackpot,
                'Winners': winners,
                'Jackpot Date': jackpot_date
            }

        return results


def start(update, context):
    """Handler for the /start command."""
    username = update.effective_user.username
    reply_keyboard = [[game] for game in lotto.games_list.values()]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hello, {username}! I am Capt. Jack Pott. I can give Lotto Results for today, yesterday, or 3 days ago. Choose a game from the menu.", reply_markup=markup)
    return 0

def select_game(update, context):
    """Handler for selecting a game from the menu."""
    game_name = update.message.text

    # Check if the selected game is "/start" command
    if game_name == "/start":
        return start(update, context)  # Redirect to the start function

    # Check if the selected game is "/games" command
    if game_name == "/games":
        return games(update, context)  # Redirect to the games function

    # Check if the selected game is a valid game
    if game_name in lotto.games_list.values():
        game_id = list(lotto.games_list.keys())[list(lotto.games_list.values()).index(game_name)]
        results = lotto.scrape_results(today.month, today.year, today.month, today.year)
        if not results:
            results = lotto.scrape_results(yesterday.month, yesterday.year, yesterday.month, yesterday.year)
            if not results:
                results = lotto.scrape_results(three_days_ago.month, three_days_ago.year, three_days_ago.month, three_days_ago.year)

        if results:
            for game, result in results.items():  # Iterate over dictionary items instead of keys
                if game == game_name:
                    message = f"<b>{game}</b>\n\n"
                    message += f"<pre>Combinations: {result['Result']}</pre>\n"
                    message += f"<pre>Draw Date: {result['Jackpot Date']}</pre>\n"
                    message += f"<pre>Jackpot (₱): {result['Jackpot']}</pre>\n"
                    message += f"<pre>Winners: {result['Winners']}</pre>\n"
                    break
            else:
                message = f"No results found for {game_name}."
        else:
            message = f"No results found for {game_name}."
    else:
        message = f"Invalid game. Please select a game from the menu."

    # Send the result message
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='HTML')
    
    # Show the game menu again
    reply_keyboard = [[game] for game in lotto.games_list.values()]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text="This is a Beta (β) Release. Bugs are expected. Please report them by sending a message to @alfiesuperhalk", reply_markup=markup)

    return 0

def games(update, context):
    """Handler for the /games command."""
    game_list = "\n".join(lotto.games_list.values())
    message = "<b>Games Available</b>\n\n" + game_list + "\n\nTo get the result, choose from the game menu."
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='HTML')


# Create the PCSO Lotto instance
lotto = PCSOLotto()

# Set up the Telegram bot
telegram_token = os.getenv('TOKEN')
updater = Updater(token=telegram_token, use_context=True)

# Get today's date
today = datetime.now().date()
yesterday = today - timedelta(days=1)
three_days_ago = today - timedelta(days=3)

# Create the conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        0: [MessageHandler(Filters.text, select_game)]
    },
    fallbacks=[ConversationHandler.END]  # Add ConversationHandler.END as the fallback state
)

# Add the conversation handler to the updater
updater.dispatcher.add_handler(conv_handler)

# Add the /games command handler
updater.dispatcher.add_handler(CommandHandler('games', games))

# Start the bot
updater.start_polling()
updater.idle()
