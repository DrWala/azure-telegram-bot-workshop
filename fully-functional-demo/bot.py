import logging
import requests
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

token = "[TELEGRAM BOT TOKEN]"
qnamaker_endpoint = "[QNAMAKER ENDPOINT]"
qnamaker_endpoint_key = "[QNAMAKER ENDPOINT KEY]"
text_analytics_endpoint = "[TEXT ANALYTICS ENDPOINT]"
text_analytics_key = "[TEXT ANALYTICS KEY]"


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text(f'Hi {user.first_name} {user.last_name}!')


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, _: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(f"you said {update.message.text}")


def answer_question(update: Update, _: CallbackContext) -> None:
    incoming_message = update.message.text
    headers = {
        "Authorization": f"EndpointKey {qnamaker_endpoint_key}",
        "Content-Type": "application/json"
    }

    analyse_text(incoming_message)

    data = {
        "question": incoming_message
    }

    response = requests.post(qnamaker_endpoint, headers=headers, json=data)
    json_response = response.json()
    logger.info("JSON response: %s", json_response)
    reply_text = json_response["answers"][0]["answer"]

    update.message.reply_text(reply_text)


def authenticate_client():
    ta_credential = AzureKeyCredential(text_analytics_key)
    text_analytics_client = TextAnalyticsClient(
        endpoint=text_analytics_endpoint,
        credential=ta_credential)
    return text_analytics_client


def analyse_text(text):
    client = authenticate_client()

    documents = [text]
    response = client.analyze_sentiment(documents=documents)[0]
    print("Document Sentiment: {}".format(response.sentiment))
    for idx, sentence in enumerate(response.sentences):
        print("Sentence: {}".format(sentence.text))
        print("Sentence {} sentiment: {}".format(idx + 1, sentence.sentiment))
        print("Sentence score:\nPositive={0:.2f}\nNeutral={1:.2f}\nNegative={2:.2f}\n".format(
            sentence.confidence_scores.positive,
            sentence.confidence_scores.neutral,
            sentence.confidence_scores.negative,
        ))


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text, answer_question))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
