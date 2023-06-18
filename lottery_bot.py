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

            # Store the results in the dictionary
            results[game_name] = {
                'Result': result,
                'Jackpot': jackpot,
                'Winners': winners,
                'Jackpot Date': jackpot_date
            }

        return results

# Create an instance of PCSOLotto
lotto = PCSOLotto()

def start(update, context):
    """Handler for the /start command."""
    # Define the reply keyboard options
    options = [['/selection', '/games']]
    reply_markup = ReplyKeyboardMarkup(options, one_time_keyboard=True)

    # Send the start message
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to PCSO Lottery Bot! Please select an option:",
        reply_markup=reply_markup
    )

    # Return the corresponding state
    return 0

def selection(update, context):
    """Handler for the /selection command."""
    # Define the reply keyboard options
    options = [
        ['/ultra', '/grand'],
        ['/super', '/mega'],
        ['/lotto', '/6d'],
        ['/4d', '/3d'],
        ['/2d', '/back']
    ]
    reply_markup = ReplyKeyboardMarkup(options, one_time_keyboard=True)

    # Send the selection message
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Please select a game:",
        reply_markup=reply_markup
    )

    # Return the corresponding state
    return 1

def select_game(update, context):
    """Handler for selecting a game."""
    game_name = update.message.text.lower()

    if game_name in lotto.games_list.values():
        # Game is valid, proceed with retrieving the results
        game_id = list(lotto.games_list.keys())[list(lotto.games_list.values()).index(game_name)]

        # Get the current month and year
        now = datetime.now()
        start_month = now.month
        start_year = now.year

        # Get the previous month and year
        previous_month = now.month - 1 if now.month > 1 else 12
        previous_year = now.year if now.month > 1 else now.year - 1

        # Scrape the results for the current and previous month
        results_current_month = lotto.scrape_results(start_month, start_year, start_month, start_year)
        results_previous_month = lotto.scrape_results(previous_month, previous_year, previous_month, previous_year)

        # Prepare the message for the results
        message = f"Results for {game_name}:\n"

        if results_current_month:
            message += f"\nCurrent Month ({calendar.month_name[start_month]} {start_year}):\n"
            message += format_results(results_current_month.get(game_name))

        if results_previous_month:
            message += f"\nPrevious Month ({calendar.month_name[previous_month]} {previous_year}):\n"
            message += format_results(results_previous_month.get(game_name))

        # Send the results message
        context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='HTML')

    else:
        # Game is not valid, send an error message
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Invalid game selection. Please try again.",
            reply_markup=ReplyKeyboardRemove()
        )

    # Return to the selection state
    return 1

def format_results(result):
    """Formats the lottery results into a readable format."""
    if result:
        table = PrettyTable()
        table.field_names = ["Result", "Jackpot", "Winners", "Jackpot Date"]
        table.add_row(
            [result['Result'], result['Jackpot'], result['Winners'], result['Jackpot Date']]
        )
        return f"<pre>{table}</pre>"
    else:
        return "No results found."

def games(update, context):
    """Handler for the /games command."""
    game_list = "\n".join(lotto.games_list.values())
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="<b>Games Available</b>\n" + game_list,
        parse_mode='HTML'
    )

def unrecognized(update, context):
    """Handler for unrecognized messages."""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Unrecognized command. The menu is always accessible in the message bar."
    )

def error(update, context):
    """Handler for errors."""
    print(f"Update {update} caused error {context.error}")

# Create the conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        0: [CommandHandler('selection', selection)],
        1: [MessageHandler(Filters.text, select_game)]
    },
    fallbacks=[CommandHandler('start', start)]  # Add a fallback command handler for unexpected input
)

def main():
    """Starts the bot and adds the conversation handler."""
    # Get the Telegram bot token from environment variables
    token = os.getenv('TOKEN')

    # Create an updater and pass the token
    updater = Updater(token=token, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add the conversation handler to the dispatcher
    dispatcher.add_handler(conv_handler)

    # Add the games command handler
    dispatcher.add_handler(CommandHandler('games', games))

    # Add the unrecognized message handler
    dispatcher.add_handler(MessageHandler(Filters.all, unrecognized))

    # Add the error handler
    dispatcher.add_error_handler(error)

    # Start the bot
    updater.start_polling()

    # Run the bot until Ctrl+C is pressed
    updater.idle()

# Run the main function
if __name__ == '__main__':
    main()
