import telebot
import smtplib
import random
import string
import MetaTrader5 as mt5
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread
import time
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# MetaTrader 5 Connection Settings (from .env file)
login = 5033134663  # Replace with your MT5 login
password = "Ap*i6aAs"  # Replace with your MT5 password
server = "MetaQuotes-Demo"  # Replace with your MT5 server
# Telegram Bot Token (hardcoded as per original code)
bot = telebot.TeleBot("#Replace with your telegram bot Api")

# Email Configuration (untouched)
EMAIL_ADDRESS = '#Replace with Gmail'
EMAIL_PASSWORD = '#Replace with password'
RECIPIENT_EMAIL = '#Replace with Email'

 # Constants
PASSWORD_EXPIRY = 24 * 60 * 60  # 24 hours
FIXED_LOT_SIZE = #set lot size (e.g 0.2)
MAX_DAILY_TRADES = #Set Maximum Trades

# Global Variables
daily_password = None
trade_count = 0  # Counter for daily trades
authorized_users = set()  # Set to manage authorized users

# Utility Functions
def generate_password(length=8):
    """Generate a random password."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def send_password_email(password):
    """Send the daily password via email."""
    subject = "Daily Bot Password"
    body = f"Your password for accessing the bot is: {password}"
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")

def update_password():
    """Generate and send a new password daily."""
    global daily_password
    while True:
        daily_password = generate_password()
        send_password_email(daily_password)
        time.sleep(PASSWORD_EXPIRY)

# Telegram Handlers
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Welcome! Please enter the password to access the bot.")

@bot.message_handler(commands=["help"])
def help_command(message):
    help_text = """
Available Commands:
/start - Start the bot and access password authentication
/account - Check MetaTrader account details
/help - Get a list of available commands and their descriptions
/trades - View the number of trades placed today
"""
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=["account"])
def account(message):
    try:
        if message.chat.id in authorized_users:
            account_info = check_account()
            bot.send_message(message.chat.id, account_info)
        else:
            bot.send_message(message.chat.id, "You are not authorized. Please enter the correct password.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

@bot.message_handler(commands=["trades"])
def trades(message):
    if message.chat.id in authorized_users:
        bot.send_message(message.chat.id, f"Trades placed today: {trade_count}/{MAX_DAILY_TRADES}")
    else:
        bot.send_message(message.chat.id, "You are not authorized. Please enter the correct password.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.chat.id in authorized_users:
        process_signal(message.text)
    else:
        if message.text == daily_password:
            authorized_users.add(message.chat.id)
            bot.send_message(message.chat.id, "Access granted!")
        else:
            bot.send_message(message.chat.id, "Incorrect password. Access denied.")

# Trading Functions
def check_account():
    """Check and return MetaTrader account details."""
    if not mt5.initialize(login=login, password=password, server=server):
        error_code, description = mt5.last_error()
        return f"Failed to initialize MetaTrader: {error_code}, {description}"
    
    account_info = mt5.account_info()
    if account_info is None:
        error_code, description = mt5.last_error()
        return f"Failed to retrieve account info: {error_code}, {description}"
    
    mt5.shutdown()
    return (f"Account Info:\n"
            f"Balance: {account_info.balance}\n"
            f"Equity: {account_info.equity}\n"
            f"Leverage: {account_info.leverage}\n"
            f"Profit: {account_info.profit}\n")



def process_signal(signal):
    """Process incoming trading signals."""
    global trade_count

    print(f"Received signal: {signal}")  # Log the received signal

    if trade_count >= MAX_DAILY_TRADES:
        print("Daily trade limit reached.")
        return
    
    try:
        parts = signal.split()
        if len(parts) < 4:
            print("Invalid signal format.")
            return

        action = parts[0].upper()
        symbol = parts[1]
        sl = float(parts[2].split('=')[1])
        tp = float(parts[3].split('=')[1])

        print(f"Parsed Signal: Action={action}, Symbol={symbol}, SL={sl}, TP={tp}")  # Log parsed components

        if action not in ["BUY", "SELL"]:
            print("Invalid action. Must be 'BUY' or 'SELL'.")
            return

        place_trade(action, symbol, sl, tp)
        trade_count += 1
        print("Trade processed successfully.")  # Log trade success
    except Exception as e:
        print(f"Error processing signal: {e}")

def place_trade(action, symbol, sl, tp):
    """Place a trade in MetaTrader 5."""
    print(f"Placing trade: Action={action}, Symbol={symbol}, SL={sl}, TP={tp}")  # Log trade attempt

    if not mt5.initialize(login=login, password=password, server=server):
        print("Failed to initialize MT5")
        return
    
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        print(f"Symbol {symbol} not found")
        return
    
    if not symbol_info.visible:
        mt5.symbol_select(symbol, True)
    
    # Define order type
    order_type = 0 if action.upper() == "BUY" else 1  # 0 for BUY, 1 for SELL
    price = mt5.symbol_info_tick(symbol).ask if order_type == 0 else mt5.symbol_info_tick(symbol).bid

    print(f"Order type: {order_type}, Price: {price}")  # Log order details

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": FIXED_LOT_SIZE,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 234000,
        "comment": "Telegram Bot Trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    mt5.shutdown()
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order failed, retcode={result.retcode}, message={result.comment}")
    else:
        print(f"Trade placed successfully: {result}")

# Main Execution
if __name__ == "__main__":
    Thread(target=update_password, daemon=True).start()
    bot.polling()
