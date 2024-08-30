import logging
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # PEP 396 tuple

if __version_info__ < (20, 0, 0, 'alpha', 1):
    raise RuntimeError(f'This example is not compatible with your current PTB version {TG_VER}. To view the '
                       f'{TG_VER} version of this example, visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html')

from telegram import Update, Chat
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from models.gpt_model import GPTModel
from config import TELEGRAM_BOT_TOKEN, BOT_USERNAME
from telegram.error import TimedOut

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

gpt_model = GPTModel()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! I am your memory bot. Start chatting with me!')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    chat_type = update.message.chat.type
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    message = update.message

    logger.info(f"Received message in chat type: {chat_type}")
    logger.info(f"Message text: {user_text}")

    if message.from_user.name != BOT_USERNAME:
        logger.info(f"Updating training data from user: {user_id}")
        gpt_model.update_training_data(f'{message.from_user.name}: {user_text}')
        log_conversation(user_id, user_text)

    if chat_type in [Chat.GROUP, Chat.SUPERGROUP]:
        mentioned_bot = BOT_USERNAME in user_text
        if mentioned_bot:
            logger.info(f"Bot mentioned in group chat: {chat_id}")

            bot_response = gpt_model.generate_response(user_text.replace(f"{BOT_USERNAME}", '').strip())

            await update.message.reply_text(bot_response['message'])
        else:
            logger.info(f"Bot not mentioned in group chat: {chat_id}")

    elif chat_type == Chat.PRIVATE:
        logger.info(f"Message received in private chat: {chat_id}")

        bot_response = gpt_model.generate_response(user_text.strip())

        await update.message.reply_text(bot_response)

def log_conversation(user_id, message):
    with open('data/conversations.log', 'a') as log_file:
        log_file.write(f'{user_id}: {message}\n')

def main():
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

    application.add_handler(CommandHandler('start', start))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    try:
        application.run_polling(poll_interval=1.0)
    except TimedOut:
        logger.error("Timed out while trying to connect to Telegram. Please check your network connection and try again.")

if __name__ == '__main__':
    main()
