from telegram import *
import telegram.ext
from telegram import Update
import messagehandle
import callbackhandle
import cache
from decouple import config

TOKEN = config("TOKEN", default="")
ADMIN_CHAT_ID = config("ADMIN_CHAT_ID", default="")
Programmer_CHAT_ID = config("PROGRAMMER_CHAT_ID", default="")
address = config("ADDRESS", default="")

async def start_command(update:Update,context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    buttons = [[KeyboardButton("Register")],[KeyboardButton("Login")]]

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome!", reply_markup=ReplyKeyboardMarkup(buttons))


if __name__=='__main__':

    app = telegram.ext.Application.builder().token(TOKEN).build()
    #commands
    app.add_handler(telegram.ext.CommandHandler('start',start_command))
    app.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.TEXT,messagehandle.messageHandler))
    app.add_handler(telegram.ext.CallbackQueryHandler(callbackhandle.callback))
    app.run_polling()


