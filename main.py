import logging
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext, JobQueue
from datetime import datetime, timedelta

# Define your bot's token and the channel ID here
TOKEN = '6233157191:AAHoYxfToEUoCKVvV8caOoav2bqnM1lkXWo'
CHANNEL_ID = -1001709730026 # Replace with your channel ID

# Define the password for authentication
correct_password = '12345pass'

# Dictionary to store user data
user_data = {}
authorized_users = set()
login_time = {}

# Enable logging for debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Define the states for the conversation
LOGIN, AUTHORIZED = range(2)

# Function to start the conversation
def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id in authorized_users:
        update.message.reply_text("You are already logged in.")
        return AUTHORIZED
    else:
        update.message.reply_text("Welcome to the login system. Please use /login to log in.")
        return LOGIN

# Function to handle the login command
def login(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id in authorized_users:
        update.message.reply_text("You are already logged in.")
        return AUTHORIZED

    update.message.reply_text("Please enter the password to log in:")
    return LOGIN

# Function to handle the password
def handle_password(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    password = update.message.text

    if password == correct_password:
        authorized_users.add(user_id)
        login_time[user_id] = datetime.now()

        context.job_queue.run_once(logout_user, timedelta(hours=24), context=user_id)

        # Send user details to the specified channel
        user = update.message.from_user
        message = f"New login: {user.first_name} {user.last_name} (@{user.username})\nUser ID: {user.id}"
        context.bot.send_message(CHANNEL_ID, message)

        update.message.reply_text("Login successful. You are now logged in for 24 hours.")
        return AUTHORIZED
    else:
        update.message.reply_text("Login failed. Please try again.")
        return LOGIN

# Function to handle authorized actions
def authorized(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id in authorized_users:
        update.message.reply_text("You are authorized to perform actions now.")
    else:
        update.message.reply_text("You need to log in first using /login.")

# Function to log out a user
def logout_user(context):
    user_id = context.job.context
    authorized_users.discard(user_id)
    del login_time[user_id]

# Function to display user details
def about(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id in authorized_users:
        login_time_str = login_time.get(user_id)
        if login_time_str:
            login_time_str = login_time_str.strftime("%Y-%m-%d %H:%M:%S")
        else:
            login_time_str = "N/A"

        user = update.message.from_user
        details = f"User ID: {user.id}\nLast Login Time: {login_time_str}\n"
        update.message.reply_text(details, parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text("You need to log in first using /login.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('login', login))
    dp.add_handler(CommandHandler('about', about))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_password))
    dp.add_handler(CommandHandler('authorized', authorized))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
