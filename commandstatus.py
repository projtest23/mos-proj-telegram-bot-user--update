from telegram import *
import telegram.ext
from datetime import datetime
import requests
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


def check_registration(user_id):
    try:
        req = requests.get(f"http://{address}/dydx/api/v1/telegramuser/")
        data = req.json()
        for user in data:
            if str(user['user_id']) == str(user_id):
                return ('You have already registered')
    except:
        return ('Something happened, we can not connect to server')
    return ('Enter your username')

def check_not_command(text):
    if(text != "register" and 
        text != "close all positions" and 
        text != "emergency shotdown" and 
        text != "veiw staking reward date" and 
        text != "withdraw" and 
        text != "stop staking" and 
        text != "start staking" and 
        text != "deposit" and 
        text != "total balance" and 
        text != "login"):
        return True
    else:
        return False


def register_status(user_id,msg):
    if 'username' not in reg_log_data[user_id].keys(): 
        reg_log_data[user_id].update({'username':msg})
        return {"k":False,"text":"Input your 1Inch address"}

    elif 'one_inch' not in reg_log_data[user_id].keys():
        reg_log_data[user_id].update({'one_inch':msg})
        return {"k":False,"text":"Input your Uniswap address"}

    elif 'uniswap' not in reg_log_data[user_id].keys():
        reg_log_data[user_id].update({'uniswap':msg})
        return {"k":False,"text":"Input your AtomicWallet address"}

    elif 'atomic' not in reg_log_data[user_id].keys():
        reg_log_data[user_id].update({'atomic':msg})
        return {"k":False,"text":"Enter your password"} 

    elif 'password' not in reg_log_data[user_id].keys():
        reg_log_data[user_id].update({'password':msg})
        keyboard = [[InlineKeyboardButton("Yes",callback_data='register'),
                    InlineKeyboardButton("No",callback_data='again')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = f"""
                Your username: '{reg_log_data[user_id]['username']}'
Your password: '{reg_log_data[user_id]['password']}' 
Your AtomicWallet address: '{reg_log_data[user_id]['atomic']}'
Your Uniswap address: '{reg_log_data[user_id]['uniswap']}'
Your 1Inch address: '{reg_log_data[user_id]['one_inch']}'"""
        command_status[user_id] = ''
        return {"k":True,"text":text, "reply_markup":reply_markup}
    

def login_status(user_id,msg):
    if 'username' not in reg_log_data[user_id].keys():
        reg_log_data[user_id].update({'username':msg})
        return {"text":"Enter your password",'login':False}

    elif 'password' not in reg_log_data[user_id].keys():
        reg_log_data[user_id].update({'password':msg})
        req = requests.get(f"http://{address}/dydx/api/v1/telegramuser/")
        data = req.json()
        for user in data:
            if str(user['user_id'])==str(user_id):
                if not (user['username'] == reg_log_data[user_id]['username'] and user['password'] == reg_log_data[user_id]['password']):
                    reg_log_data['command_status'] = ""
                    return {"text":"Please check your inputs, username and password do not match.",'login':False}
                req = requests.get(f"http://{address}/dydx/api/v1/wallet/")
                data = req.json()
                for user in data:
                    if str(user['telegram_user']) == str(user_id):
                        buttons = [[KeyboardButton("Total Balance")],
                    [KeyboardButton("Deposit")],
                    [KeyboardButton("Start Staking")],
                    [KeyboardButton("Stop Staking")],
                    [KeyboardButton("Withdraw")],
                    [KeyboardButton("Emergency Shutdown")],
                    [KeyboardButton("View Staking Reward Date")],
                    [KeyboardButton("Close All Positions")]]
                        reply_markup=ReplyKeyboardMarkup(buttons)
                        
                        command_status[user_id] = ''
                        return {"login":True,"text":"Welcome!", "reply_markup":reply_markup}
                return {"text":"Your account is not confirmed, please be patient.",'login':False}
        return {"text":"You did not register yet, please register first.",'login':False}


def choosing_wallet(user_id,msg_text):
    req = requests.get(f"http://{address}/dydx/api/v1/wallet/")
    data = req.json()
    keyboard = []
    flag = False
    for user in data:
        if str(user['telegram_user']) == str(user_id):
            if msg_text == 'Deposit':
                command_status[user_id] = "deposit"
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"deposit:{user['name']}")])

            elif msg_text == 'Total Balance':
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"balance:{user['balance']},{user['name']}")])
            
            elif msg_text == 'View Staking Reward Date':
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"wallet_id:{user['id']},{user['name']}")])
            
            elif msg_text == 'Start Staking':
                command_status[user_id] = "start_staking"
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"start_staking:{user['id']},{user['name']}")])
            
            elif msg_text == 'Stop Staking':
                command_status[user_id] = "stop_staking"
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"stop_staking:{user['id']},{user['name']}")])
            
            elif msg_text == 'Withdraw':
                command_status[user_id] = "withdraw"
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"withdraw:{user['id']},{user['name']}")])
            
            elif msg_text == 'Close All Positions':
                command_status[user_id] = "close_positions"
                command_data[user_id] = {'wallet':user['name'],"wallet_id":user['id']}
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"close_positions:{user['id']},{user['name']}")])
            
            elif msg_text == 'Emergency Shutdown':
                command_status[user_id] = "emergency"
                command_data[user_id] = {'wallet':user['name'],"wallet_id":user['id']}
                keyboard.extend([InlineKeyboardButton(f"{user['name']}",callback_data=f"emergency:{user['id']},{user['name']}")])

            flag = True

    if flag:
        reply_markup = InlineKeyboardMarkup([keyboard])
        text = f"""Please choose your wallet"""
        return {"k":True,"text":text, "reply_markup":reply_markup}
    else:
        return {"k":False,"text":'You have no active wallets'}
    

def start_staking(user_id, msg,message_id):
    global command_data
    global msg_id
        
    if 'volume' not in command_data[user_id].keys():
        volume = msg
        if not volume.isdigit():
            msg_id=0
            return {"text":"Input error, please use digits only.","stake":False}
        command_data[user_id].update({'volume':volume})
        msg_id = message_id
        return {"text":"Please enter your desire months.","stake":False}
    if 'date' not in command_data[user_id].keys():
        date = msg
        if not date.isdigit():
            msg_id=0
            command_data = {}
            return {"text":"Input error, please use digits only.","stake":False}
            
        command_data[user_id].update({'date':date})
        msg_id = message_id
        return {"text":"Enter your password","stake":False}
    else:
        req = requests.get(f"http://{address}/dydx/api/v1/telegramuser/")
        data = req.json()
        for user in data:
            if str(user['user_id'])==str(user_id):
                if not str(user['password']) == str(msg):
                    reg_log_data['command_status'] = ""
                    return {"text":"Please check your inputs, password is wrong.","stake":False}
                    
        req_data = {
            "wallet": command_data[user_id]['wallet_id'],
            "telegram_user": user_id,
            "staking_volume": int(command_data[user_id]['volume']),
            "staking_date": int(command_data[user_id]['date']),
            "created_date":datetime.now().date()
        }
        req = requests.post(f"http://{address}/dydx/api/v1/staking/",req_data)
        if req.status_code == 201:
            return {"text": "Your request has been recieved. Please wait for the process.","stake":True}
        elif req.status_code == 400:
            return {"text":req.json(),"stake":False}


def close_positions(user_id, msg,message_id):
    global command_data
    global msg_id
    req = requests.get(f"http://{address}/dydx/api/v1/telegramuser/")
    data = req.json()
    for user in data:
        if str(user['user_id'])==str(user_id):
            if not str(user['password']) == str(msg):
                reg_log_data['command_status'] = ""
                return {"text":"Please check your inputs, password is wrong","k":False}
            break
    
    keyboard = [[InlineKeyboardButton("Yes",callback_data='close_yes'),
                    InlineKeyboardButton("No",callback_data='close_no')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Are you sure you want to close all positions? This might cause you to loose your money!"
    return {"k":True,"text":text, "reply_markup":reply_markup}


def emergency_shotdown(user_id, msg,message_id):
    global command_data
    global msg_id
    req = requests.get(f"http://{address}/dydx/api/v1/telegramuser/")
    data = req.json()
    for user in data:
        if str(user['user_id'])==str(user_id):
            if not str(user['password']) == str(msg):
                reg_log_data['command_status'] = ""
                return {"text":"Please check your inputs, password is wrong","k":False}
            break
    
    keyboard = [[InlineKeyboardButton("Yes",callback_data='shotdown_yes'),
                    InlineKeyboardButton("No",callback_data='shotdown_no')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Are you sure you want to shut down the robot? Your open positions will be closed and this might cause you to loose your money!"
    return {"k":True,"text":text, "reply_markup":reply_markup}


def stop_staking(user_id, msg,message_id):
    global command_data
    global msg_id
    req = requests.get(f"http://{address}/dydx/api/v1/telegramuser/")
    data = req.json()
    for user in data:
        if str(user['user_id'])==str(user_id):
            if not str(user['password']) == str(msg):
                reg_log_data['command_status'] = ""
                return {"text":"Please check your inputs, password is wrong","k":False}
            break
    req = requests.get(f"http://{address}/dydx/api/v1/staking/")
    data = req.json()
    keyboard = []
    stakes_list = []
    for stake in data:
        if str(stake['wallet']) == str(command_data[user_id]['wallet_id']):
            stakes_list.append(stake)
    
    text = """Please choose your stake"""              
    if len(stakes_list)== 0:
        text = "You have no active stake!"
    else:
        for s in range(len(stakes_list)):
            keyboard.extend([InlineKeyboardButton(f"{s+1}",callback_data=f"choose_stake:{stakes_list[s]['staking_volume']},{stakes_list[s]['days_left']}")])
            text += f"""
{s+1}. Amount: {stakes_list[s]['staking_volume']:,.2f} , Days left: {stakes_list[s]['days_left']}"""
    reply_markup = InlineKeyboardMarkup([keyboard])
    
    return {"k":True,"text":text, "reply_markup":reply_markup}



def withdraw(user_id, msg,message_id):
    global command_data
    global msg_id
        
    if 'password' not in command_data[user_id].keys():
        req = requests.get(f"http://{address}/dydx/api/v1/telegramuser/")
        data = req.json()
        for user in data:
            if str(user['user_id'])==str(user_id):
                if not str(user['password']) == str(msg):
                    reg_log_data['command_status'] = ""
                    return {"text":"Please check your inputs, password is wrong","withdraw":False}
        command_data[user_id].update({'password':msg})
        msg_id = message_id
        return {"text":"Please enter your desire amount.","withdraw":False}
    
    if 'volume' not in command_data[user_id].keys():
        volume = msg
        if not volume.isdigit():
            msg_id=0
            return {"text":"Input error, please use digits only.","withdraw":False}
         
        command_data[user_id].update({'volume':volume})
        msg_id = message_id
        req = requests.get(f"http://{address}/dydx/api/v1/wallet/")
        wallets = req.json()
        req_stake = requests.get(f"http://{address}/dydx/api/v1/staking/")
        stakes = req_stake.json()
        req_stake = requests.get(f"http://{address}/dydx/api/v1/staking/")
        stakes = req_stake.json()
        req_position = requests.get(f"http://{address}/dydx/api/v1/allpositions/")
        positions = req_position.json()
        balance = 0
        
        for wallet in wallets:
            if str(wallet['id']) == str(command_data[user_id]['wallet_id']):
                balance = wallet['balance']
        all_stake = 0
        for stake in stakes:
            if str(stake['wallet']) == str(command_data[user_id]['wallet_id']):
                all_stake += stake['staking_volume']
        free_margin = balance - all_stake
        if (free_margin)<float(volume):
            return {"text":f"Your request is bigger than your free margin.","withdraw":False}
        for stake in stakes:
            if str(stake['wallet']) == str(command_data[user_id]['wallet_id']):
                all_stake += stake['staking_volume']
        for pos in positions:
            if str(pos['wallet']) == str(command_data[user_id]['wallet_id']):
                return {"text":f"You have open positions, it would be better to not to withdraw, if you are willing to withdraw at any cost, please contact us.","withdraw":False}
        new_balance = balance - float(volume)
        post_body = {
            "balance": new_balance
        }
        req = requests.patch(f"http://{address}/dydx/api/v1/wallet/{command_data[user_id]['wallet_id']}/",post_body)
        if req.status_code == 200:
            return {"text":"Your request has been recieved. Please wait for the process.","withdraw":True}
        else:
            return {"text":"Something happened, we can not connect to server","withdraw":False}