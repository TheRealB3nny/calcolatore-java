import logging
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Token del bot Telegram
BOT_TOKEN = '8095840441:AAH6nl6u5RFmsQq1slt4mb2nC7omBl7YpUI'   # Sostituisci con il token del tuo bot

# Imposta il logging per monitorare eventuali errori
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Funzione per ottenere il valore attuale del Bitcoin da CoinGecko
def get_bitcoin_value():
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd')
        data = response.json()
        return data['bitcoin']['usd']
    except Exception as e:
        logger.error(f"Errore nel recupero del valore del Bitcoin: {e}")
        return None

# Funzione di avvio
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Andamento Bitcoin", callback_data="andamento_bitcoin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Ciao! 👋 Sono il tuo bot che ti tiene aggiornato sul valore del Bitcoin. Cosa vuoi fare?",
        reply_markup=reply_markup
    )

# Funzione per inviare il valore del Bitcoin
async def andamento_bitcoin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bitcoin_value = get_bitcoin_value()
    if bitcoin_value:
        await update.callback_query.edit_message_text(
            f"💰 Il valore attuale del Bitcoin è: ${bitcoin_value} USD.\n\n"
            "Puoi monitorarlo in tempo reale cliccando sul link qui sotto.\n"
            "🔗 [Vai a CoinGecko](https://www.coingecko.com/en/coins/bitcoin)"
        )
    else:
        await update.callback_query.edit_message_text(
            "⚠️ Impossibile ottenere il valore attuale del Bitcoin. Riprova più tardi."
        )

# Funzione per avviare il bot
def main():
    # Crea il bot
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Aggiungi i gestori per le risposte
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(andamento_bitcoin, pattern="^andamento_bitcoin$"))

    # Avvia il bot
    print("Bot in esecuzione...")
    application.run_polling()

if __name__ == "__main__":
    main()
