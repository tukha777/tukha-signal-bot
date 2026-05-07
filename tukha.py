import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread
import os
import time

# --- Render-ისთვის საჭირო ვებ-სერვერი (Keep Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "Tukha Signal is Running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
# --------------------------------------------------

TOKEN = '8701731141:AAFbvNGRGCuw_srFMgfOPFO_XmK_lMJxK1U'
bot = telebot.TeleBot(TOKEN)

PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "EURGBP", 
    "EURJPY", "GBPJPY", "EURAUD", "EURCAD", "AUDJPY", "CADJPY", "GBPAUD", "GBPCAD",
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT",
    "AVAXUSDT", "LINKUSDT", "MATICUSDT", "UNIUSDT", "LTCUSDT", "BCHUSDT", "ATOMUSDT", "XMRUSDT",
    "XAUUSD", "XAGUSD", "EURCHF", "GBPCHF", "AUDCAD", "AUDCHF", "AUDNZD", "CADCHF", "CHFJPY"
]

TIMES = {
    "1 MIN": Interval.INTERVAL_1_MINUTE,
    "3 MIN": Interval.INTERVAL_1_MINUTE, 
    "5 MIN": Interval.INTERVAL_5_MINUTES,
    "15 MIN": Interval.INTERVAL_15_MINUTES,
    "30 MIN": Interval.INTERVAL_30_MINUTES
}

# --- გაძლიერებული ანალიზის ფუნქცია ---
def get_live_analysis(pair, interval):
    try:
        # ბირჟების და სკრინერების დინამიური განსაზღვრა
        if "USDT" in pair:
            exch = "BINANCE"
            scr = "crypto"
        elif any(x in pair for x in ["XAU", "XAG", "EUR", "GBP", "USD", "JPY", "AUD"]):
            # ფორექსის წყვილებისთვის OANDA ან FX_IDC უფრო სტაბილურია სერვერზე
            exch = "OANDA"
            scr = "forex"
        else:
            exch = "FX_IDC"
            scr = "forex"

        handler = TA_Handler(
            symbol=pair,
            screener=scr,
            exchange=exch,
            interval=interval,
            timeout=15  # მეტი დრო სერვერისთვის
        )
        
        analysis = handler.get_analysis()
        
        summary = analysis.summary['RECOMMENDATION']
        buy = analysis.summary['BUY']
        sell = analysis.summary['SELL']
        neutral = analysis.summary['NEUTRAL']
        
        total = buy + sell + neutral
        
        # თუ პირველმა ცდამ 0 მოგვცა, ვცადოთ რეზერვი
        if total == 0:
            handler.exchange = "FX_IDC" if exch == "OANDA" else "OANDA"
            analysis = handler.get_analysis()
            buy = analysis.summary['BUY']
            sell = analysis.summary['SELL']
            neutral = analysis.summary['NEUTRAL']
            summary = analysis.summary['RECOMMENDATION']
            total = buy + sell + neutral

        if total == 0:
            return "NO DATA", 0
        
        accuracy = max(buy, sell) / total * 100
        return summary.replace("_", " "), round(accuracy, 1)
        
    except Exception as e:
        print(f"ანალიზის შეცდომა: {e}")
        return "TRY AGAIN", 0

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🚀 სიგნალის დაწყება")
    btn2 = types.KeyboardButton("ℹ️ ინფორმაცია")
    markup.add(btn1, btn2)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "მოგესალმებით **Tukha Signal**-ში! 🚀\nგამოიყენეთ ქვედა მენიუ მართვისთვის.", 
                     reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🚀 სიგნალის დაწყება")
def show_pairs(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(pair, callback_data=f"pair_{pair}") for pair in PAIRS]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "📊 აირჩიეთ სავაჭრო წყვილი:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "ℹ️ ინფორმაცია")
def info(message):
    info_text = (
        "🤖 **Tukha Signal Bot v3.1**\n\n"
        "ეს ბოტი აანალიზებს ბაზარს რეალურ დროში 20-ზე მეტი ტექნიკური ინდიკატორის გამოყენებით (RSI, Stoch, EMA და ა.შ.).\n\n"
        "💡 **რჩევა:**\n"
        "1. ენდეთ მხოლოდ **Strong** სიგნალებს.\n"
        "2. ოპტიმალური სიზუსტე: **>75%**.\n"
        "3. ფორექსი არ მუშაობს შაბათ-კვირას!"
    )
    bot.send_message(message.chat.id, info_text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("pair_"))
def callback_pair(call):
    selected_pair = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(t, callback_data=f"time_{selected_pair}_{t}") for t in TIMES.keys()]
    markup.add(*buttons)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text=f"⏳ წყვილი: **{selected_pair}**\nაირჩიეთ ვადა:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("time_"))
def callback_signal(call):
    data = call.data.split("_")
    pair, time_label = data[1], data[2]
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🔍 ბაზრის სკანირება...")
    
    recommendation, accuracy = get_live_analysis(pair, TIMES[time_label])
    
    if "BUY" in recommendation:
        icon = "🚀 STRONG BUY" if "STRONG" in recommendation else "📈 BUY"
    elif "SELL" in recommendation:
        icon = "🆘 STRONG SELL" if "STRONG" in recommendation else "📉 SELL"
    else:
        icon = "⚖️ NEUTRAL"
    
    result_text = (
        f"🚨 **Tukha Signal LIVE** 🚨\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💎 წყვილი: `{pair}`\n"
        f"⏱ ვადა: `{time_label}`\n"
        f"📊 სიგნალი: **{icon}**\n"
        f"🎯 სიზუსტე: `{accuracy}%`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"✅ წარმატებულ ვაჭრობას გისურვებთ!"
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=result_text, parse_mode="Markdown")

if __name__ == "__main__":
    keep_alive()
    print("Tukha Signal ბოტი ჩაირთვა...")
    bot.polling(none_stop=True)
