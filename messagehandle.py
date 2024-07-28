from telegram import *
import telegram.ext
from telegram import Update
import re
import cache
import commandstatus
from decouple import config


TOKEN = config("TOKEN", default="")
ADMIN_CHAT_ID = config("ADMIN_CHAT_ID", default="")
Programmer_CHAT_ID = config("PROGRAMMER_CHAT_ID", default="")
address = config("ADDRESS", default="")

msg_id = cache.msg_id
reg_log_data= cache.reg_log_data
command_status = cache.command_status
command_data = cache.command_data

async def messageHandler(update: Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    global msg_id
    global reg_log_data
    global command_status
    global command_data
    
    user_id = update.message.chat_id
    if str(user_id) == str(ADMIN_CHAT_ID):
        text = update.message.reply_to_message.text
        pattern = r"user_id:'(\d+)'"
        # Search for the pattern in the text
        match = re.search(pattern, text)

        # Check if a match is found and extract the user_id
        if match:
            user_user_id = match.group(1)
            await context.bot.send_message(chat_id=user_user_id,text=update.message.text)
            return

    # command register
    if "Register" == update.message.text:
        msg_id = update.message.message_id
        command_status[user_id] = 'register'
        reg_log_data[user_id] = {}
        text = commandstatus.check_registration(user_id=user_id)
        await update.message.reply_text(text)

    # command login
    elif "Login" == update.message.text:
        msg_id = update.message.message_id
        reg_log_data[user_id] = {}
        command_status[user_id] = 'login'
        await update.message.reply_text('Enter your username')

    # command total balance or deposit
    elif (update.message.text == 'Total Balance' 
        or update.message.text == 'Deposit' 
        or update.message.text == 'Start Staking'
        or update.message.text == 'Stop Staking'
        or update.message.text == 'View Staking Reward Date'
        or update.message.text == 'Close All Positions'
        or update.message.text == 'Emergency Shutdown'
        or update.message.text == 'Withdraw'):

        msg_id = update.message.message_id + 1
        reg = commandstatus.choosing_wallet(user_id=user_id,msg_text=update.message.text)
        if not reg:
            return
        if reg['k'] == False:
            await update.message.reply_text(reg['text'])
        else:
            await update.message.reply_text(text=reg["text"], reply_markup=reg["reply_markup"])

    
    # continue message(input email or password of others)
    elif (update.message.message_id==msg_id+2 and commandstatus.check_not_command(update.message.text)):
        msg = update.message.text
        if len(msg)==0:
            await update.message.reply_text('Please check your input')
            return
        msg_id = update.message.message_id

        # continue message when writing register inputs
        if command_status[user_id] == 'register':
            reg = commandstatus.register_status(user_id=user_id,msg=msg)
            if not reg:
                return
            if reg['k'] == False:
                await update.message.reply_text(reg['text'])
            else:
                await update.message.reply_text(text=reg["text"], reply_markup=reg["reply_markup"], protect_content=True)

        # continue message when writing login inputs
        elif command_status[user_id] == 'login':
            reg = commandstatus.login_status(user_id=user_id,msg=msg)
            if not reg:
                return
            if reg['login'] == False:
                await update.message.reply_text(reg['text'])
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=reg["text"], reply_markup=reg["reply_markup"])

        # continue message when writing start staking inputs
        elif command_status[user_id] == 'start_staking':
            message_id = update.message.id
            reg = commandstatus.start_staking(user_id=user_id,msg=msg,message_id=message_id)
            if not reg:
                return
            if reg['stake'] == False:
                await update.message.reply_text(reg['text'])
            else:
                await update.message.reply_text(reg["text"])
                text = f"user has been staked with user_id:'{user_id}' wallet: '{command_data[user_id]['wallet']}' and volume: '{command_data[user_id]['volume']}' and date: {command_data[user_id]['date']}"
                await context.bot.send_message(chat_id = ADMIN_CHAT_ID,text=text)
        
        # continue message when writing stop staking inputs
        elif command_status[user_id] == 'stop_staking':
            message_id = update.message.id
            reg = commandstatus.stop_staking(user_id=user_id,msg=msg,message_id=message_id)
            if not reg:
                return
            if reg['k'] == False:
                await update.message.reply_text(reg['text'])
            else:
                await update.message.reply_text(text=reg["text"], reply_markup=reg["reply_markup"], protect_content=True)
        
        elif command_status[user_id] == 'close_positions':
            message_id = update.message.id
            reg = commandstatus.close_positions(user_id=user_id,msg=msg,message_id=message_id)
            if not reg:
                return
            if reg['k'] == False:
                await update.message.reply_text(reg['text'])
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=reg["text"], reply_markup=reg["reply_markup"])
        
        elif command_status[user_id] == 'emergency':
            message_id = update.message.id
            reg = commandstatus.emergency_shotdown(user_id=user_id,msg=msg,message_id=message_id)
            if not reg:
                return
            if reg['k'] == False:
                await update.message.reply_text(reg['text'])
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=reg["text"], reply_markup=reg["reply_markup"])

        elif command_status[user_id] == 'withdraw':
            message_id = update.message.id
            reg = commandstatus.withdraw(user_id=user_id,msg=msg,message_id=message_id)
            if not reg:
                return
            if reg['withdraw'] == False:
                await update.message.reply_text(reg['text'])
            else:
                await update.message.reply_text(reg['text'])
                text = f"withdraw with user_id:'{user_id}' wallet: '{command_data[user_id]['wallet']}' and volume: '{command_data[user_id]['volume']}'"
                await context.bot.send_message(chat_id = ADMIN_CHAT_ID,text=text)
            
            



