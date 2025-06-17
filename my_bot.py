import logging
import re
import io
import subprocess
import sys
import requests
import json
import os
import asyncio
import dateparser
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ConversationHandler, ContextTypes
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = '8095840441:AAH6nl6u5RFmsQq1slt4mb2nC7omBl7YpUI'
API_FOOTBALL_KEY = "INSERISCI_LA_TUA_API_KEY"
REMINDER_FILE = "reminders.json"

# Stati conversazioni
(HOBBY, REGIONE, SUBREGIONE,
 ALLENAMENTO_LIVELLO, UMORE, REMINDER_TEXT) = range(6)

# --- Reminder storage ---
def load_reminders():
    if os.path.exists(REMINDER_FILE):
        with open(REMINDER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_reminders(reminders):
    with open(REMINDER_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)

async def schedule_reminder(context, user_id, reminder_id, data_ora, testo):
    now = datetime.now()
    target = datetime.fromisoformat(data_ora)
    wait = (target - now).total_seconds()
    if wait > 0:
        await asyncio.sleep(wait)
    try:
        await context.bot.send_message(chat_id=user_id, text=f"⏰ Promemoria: {testo}")
        rem = load_reminders()
        if str(user_id) in rem:
            rem[str(user_id)] = [r for r in rem[str(user_id)] if r["id"] != reminder_id]
            save_reminders(rem)
    except Exception as e:
        logging.error(f"Errore invio reminder: {e}")

# --- Reminder handlers ---
async def reminder_start(update, context):
    await update.message.reply_text("Dimmi cosa vuoi che ti ricordi (es: 'Ricordami di prendere il bus alle 18')")
    return REMINDER_TEXT

async def reminder_receive(update, context):
    text = update.message.text
    data_ora = dateparser.parse(text, settings={'PREFER_DATES_FROM':'future'})
    if not data_ora:
        await update.message.reply_text("Non ho capito quando. Prova: 'Ricordami ... alle 18'")
        return REMINDER_TEXT

    user_id = str(update.message.from_user.id)
    reminder_id = str(datetime.now().timestamp()).replace(".", "")
    rem_obj = {"id": reminder_id, "text": text, "datetime": data_ora.isoformat()}
    rems = load_reminders()
    rems.setdefault(user_id, []).append(rem_obj)
    save_reminders(rems)

    # Scheduling reminder without blocking
    asyncio.create_task(schedule_reminder(context, user_id, reminder_id, rem_obj["datetime"], text))
    await update.message.reply_text(f"Promemoria impostato: '{text}' alle {data_ora.strftime('%Y-%m-%d %H:%M')}")
    return ConversationHandler.END

async def mostra_reminder(update, context):
    user_id = str(update.message.from_user.id)
    rems = load_reminders().get(user_id, [])
    if not rems:
        await update.message.reply_text("Non hai promemoria attivi.")
        return
    msg = "I tuoi promemoria:\n" + "\n".join(
        f"- {r['text']} alle {datetime.fromisoformat(r['datetime']).strftime('%Y-%m-%d %H:%M')}"
        for r in rems)
    await update.message.reply_text(msg)

async def cancella_reminder(update, context):
    user_id = str(update.message.from_user.id)
    rems = load_reminders()
    if user_id in rems:
        rems[user_id] = []
        save_reminders(rems)
        await update.message.reply_text("Tutti i promemoria cancellati.")
    else:
        await update.message.reply_text("Non hai promemoria da cancellare.")

# --- Start, menu ---
async def start(update, context):
    await update.message.reply_text("Ciao! Scrivi /menu per iniziare.")

async def menu(update, context):
    kb = [
        [KeyboardButton("📰 Notizie Crypto"), KeyboardButton("⚽ Calcio Serie A")],
        [KeyboardButton("🏋️ Scheda Allenamento"), KeyboardButton("📊 Azioni Preferite")],
        [KeyboardButton("🎭 Analisi Umore"), KeyboardButton("⏰ Reminder Intelligente")],
        [KeyboardButton("🎯 Hobby & Regione")]
    ]
    await update.message.reply_text("Scegli una funzione:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

# --- Crypto ---
async def crypto_menu(update, context):
    kb = [
        [InlineKeyboardButton("Grafico BTC 24h", callback_data="btc_24h")],
        [InlineKeyboardButton("Grafico BTC 7 giorni", callback_data="btc_7d")],
        [InlineKeyboardButton("Imposta Alert Prezzo BTC", callback_data="btc_alert")],
    ]
    await update.message.reply_text("Crypto options:", reply_markup=InlineKeyboardMarkup(kb))

async def btc_chart(update, context):
    q = update.callback_query
    await q.answer()
    period = "1d" if q.data=="btc_24h" else "7d"
    data = yf.download("BTC-USD", period=period, interval="1h", progress=False)
    buf = io.BytesIO()
    data["Close"].plot(title=f"BTC {period}")
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    await q.message.reply_photo(photo=buf)

async def btc_alert(update, context):
    await update.callback_query.message.reply_text("Scrivi importo in $ per alert (funzionalità futura)")

# --- Calcio ---
async def calcio(update, context):
    headers = {"X-Auth-Token": API_FOOTBALL_KEY}
    url = "https://api.football-data.org/v4/competitions/SA/matches"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        await update.message.reply_text(f"Errore calcio: {e}")
        return
    matches = resp.json().get("matches", [])[:5]
    msg = "⚽ Prossime partite Serie A:\n"
    for m in matches:
        utc = m['utcDate']
        msg += f"{m['homeTeam']['name']} vs {m['awayTeam']['name']} — {utc[:10]} {utc[11:16]} UTC\n"
    await update.message.reply_text(msg)

# --- Hobby & Regione ---
async def chiedi_hobby(update, context):
    await update.message.reply_text("Qual è il tuo hobby?")
    return HOBBY

async def ricevi_hobby(update, context):
    hobby = update.message.text
    await update.message.reply_text(f"Anche a me piace {hobby}!")
    kb = [
        [InlineKeyboardButton("Nord", callback_data="nord")],
        [InlineKeyboardButton("Centro", callback_data="centro")],
        [InlineKeyboardButton("Sud", callback_data="sud")],
    ]
    await update.message.reply_text("Da dove vieni?", reply_markup=InlineKeyboardMarkup(kb))
    return REGIONE

async def scegli_regione(update, context):
    q = update.callback_query
    await q.answer()
    if q.data == "sud":
        kb = [
            [InlineKeyboardButton("Sicilia", callback_data="sicilia")],
            [InlineKeyboardButton("Calabria", callback_data="calabria")],
            [InlineKeyboardButton("Napoli", callback_data="napoli")],
        ]
        await q.message.reply_text("Quale zona del Sud?", reply_markup=InlineKeyboardMarkup(kb))
        return SUBREGIONE
    await q.message.reply_text(f"Hai scelto la regione: {q.data}")
    return ConversationHandler.END

async def scegli_subregione(update, context):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text(f"Hai scelto: {q.data}")
    return ConversationHandler.END

# --- Allenamento ---
async def allenamento_start(update, context):
    kb = [
        [InlineKeyboardButton("Principiante", callback_data="principiante")],
        [InlineKeyboardButton("Intermedio", callback_data="intermedio")],
        [InlineKeyboardButton("Avanzato", callback_data="avanzato")],
    ]
    await update.message.reply_text("Livello allenamento:", reply_markup=InlineKeyboardMarkup(kb))
    return ALLENAMENTO_LIVELLO

async def scegli_livello(update, context):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text(f"Hai scelto: {q.data}")
    return ConversationHandler.END

# --- Umore ---
async def umore_start(update, context):
    kb = [
        [KeyboardButton("😄 Felice"), KeyboardButton("😔 Triste")],
        [KeyboardButton("😡 Arrabbiato"), KeyboardButton("😐 Neutro")],
    ]
    await update.message.reply_text("Come ti senti oggi?", reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True, resize_keyboard=True))
    return UMORE

async def ricevi_umore(update, context):
    umore = update.message.text
    await update.message.reply_text(f"Grazie per aver condiviso che ti senti {umore}")
    return ConversationHandler.END

# --- Conversation Handlers definiti una volta sola ---
def get_conversation_handlers():
    hobby_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(🎯 Hobby & Regione)$"), chiedi_hobby)],
        states={
            HOBBY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_hobby)],
            REGIONE: [CallbackQueryHandler(scegli_regione)],
            SUBREGIONE: [CallbackQueryHandler(scegli_subregione)],
        },
        fallbacks=[],
        per_message=False
    )
    allen_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(🏋️ Scheda Allenamento)$"), allenamento_start)],
        states={
            ALLENAMENTO_LIVELLO: [CallbackQueryHandler(scegli_livello)],
        },
        fallbacks=[],
        per_message=False
    )
    umore_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(🎭 Analisi Umore)$"), umore_start)],
        states={
            UMORE: [MessageHandler(filters.Regex("^(😄 Felice|😔 Triste|😡 Arrabbiato|😐 Neutro)$"), ricevi_umore)],
        },
        fallbacks=[],
        per_message=False
    )
    reminder_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(⏰ Reminder Intelligente)$"), reminder_start)],
        states={
            REMINDER_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, reminder_receive)],
        },
        fallbacks=[],
        per_message=False
    )
    return [hobby_conv, allen_conv, umore_conv, reminder_conv]

# --- Main ---
def main():
    if sys.platform.startswith("win") and sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers base
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(MessageHandler(filters.Regex("^📰 Notizie Crypto$"), crypto_menu))
    app.add_handler(MessageHandler(filters.Regex("^⚽ Calcio Serie A$"), calcio))
    app.add_handler(MessageHandler(filters.Regex("^📊 Azioni Preferite$"), btc_chart))  # Puoi migliorare qui
    app.add_handler(MessageHandler(filters.Regex("^📰 Notizie Crypto$"), crypto_menu))

    # Conversation Handlers
    for conv in get_conversation_handlers():
        app.add_handler(conv)

    # CallbackQueryHandler generico per BTC alert (puoi espandere)
    app.add_handler(CallbackQueryHandler(btc_chart, pattern="btc_.*"))

    print("Bot avviato")
    app.run_polling()

if __name__ == "__main__":
    main()
