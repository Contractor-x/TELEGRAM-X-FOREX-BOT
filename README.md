# Release Notes - Secure Telegram Trading Bot............

## Version 2.0.0

### Description
The **Secure Telegram Trading Bot** is an automated trading solution that connects **Telegram** with **MetaTrader 5 (MT5)** to execute trades based on user-provided signals. Designed with security in mind, it ensures that only authorized users can access and execute trades through a rotating **daily password authentication** system. The bot is ideal for traders looking for a secure and efficient way to automate their trading strategies.

### Overview
This release introduces a **Secure Telegram Trading Bot**, designed to facilitate automated trading on **MetaTrader 5 (MT5)** via Telegram signals. The bot incorporates **secure authentication**, ensuring only authorized users can execute trades.

### Key Features
- **Secure Access Control**: Implements a **daily password** system, sent via **Postmark email API**, to restrict unauthorized access.
- **Automated Trading Execution**: Parses trading signals from Telegram messages and places trades in **MetaTrader 5**.
- **Error Handling & Logging**: Comprehensive **logging system** for tracking execution, errors, and authentication attempts.
- **Multi-threaded Performance**: Utilizes a background thread for **password updates** without disrupting bot operations.

### Technical Details
- **Telegram Bot Integration**: Handles authentication and signal processing via the Telegram bot.
- **MetaTrader 5 API**: Executes buy/sell orders based on Telegram signals with stop-loss (SL) and take-profit (TP) parameters.
- **Secure Credentials Management**: Loads API keys and credentials from **.env files** to maintain security.
- **Automated Password Rotation**: Refreshes passwords every 24 hours to enhance security.
- **Asynchronous Email Notifications**: Sends access credentials through the Postmark API.

### Installation & Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   - Create a `.env` file with the following keys:
     ```ini
     MT5_LOGIN=<your_login>
     MT5_PASSWORD=<your_password>
     MT5_SERVER=<your_server>
     TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
     POSTMARK_API_TOKEN=<your_postmark_api_token>
     EMAIL_ADDRESS=<your_email>
     RECIPIENT_EMAIL=<recipient_email>
     ```
4. Run the bot:
   ```bash
   python bot.py
   ```

### Usage
- **Start the Bot**: Users must send `/start` on Telegram.
- **Authenticate**: Enter the daily password received via email.
- **Send Trading Signals**: Format:
  ```
  BUY EURUSD SL=1.1200 TP=1.1300
  ```
### Contributors
- **@da-Korede**
- **@Contractor-x** 

### License
This project is licensed under **MIT License**.

