import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread
import os
import time

# --- სერვერის სიცოცხლის შესანარჩუნებელი კოდი ---
app = Flask('')
@app.route('/')
def home(): return "ბოტი მუშაობს!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()
# --------------------------------------------

TOKEN = '8701731141:AAFbvNGRGCuw_srFMgfOPFO_XmK_lMJxK1U'
bot = telebot.TeleBot(TOKEN)

# ყველა წყვილი
PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT",
    "XAUUSD", "XAGUSD"
]

TIMES = {
    "1 MIN": Interval.INTERVAL_1_MINUTE,
    "5 MIN": Interval.INTERVAL_5_MINUTES,
    "15 MIN": Interval.INTERVAL_15_MINUTES,
    "30 MIN": Interval.INTERVAL_30_MINUTES
}

# --- გაუმჯობესებული ანალიზის ფუნქცია (მხოლოდ ეს ნაწილი შეიცვალა შიგნით) ---
def get_live_analysis(pair, interval):
    # ბირჟების სია სადაც შეიძლება იყოს წყვილი
    options = [
        {"scr": "crypto" if "USDT" in pair else "forex", "exch": "BINANCE" if "USDT" in pair else "FX_IDC"},
        {"scr": "crypto" if "USDT" in pair else "forex", "exch": "BITSTAMP" if "USDT" in pair else "OANDA"},
        {"scr": "america" if not "USDT" in pair else "crypto", "exch": "SAXO" if not "USDT" in pair else "COINBASE"}
    ]
    
    for opt in options:
        try:
            handler = TA_Handler(
                symbol=pair,
                screener=opt["scr"],
                exchange=opt["exch"],
                interval=interval,
                timeout=10
            )
            # Headers ბლოკის ასარიდებლად
            handler.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            analysis = handler.get_analysis()
            buy = analysis.summary.get('BUY', 0)
            sell = analysis.summary.get('SELL', 0)
            neutral = analysis.summary.get('NEUTRAL', 0)
            total = buy + sell + neutral
            
            if total > 0:
                accuracy = max(buy, sell) / total * 100
                rec = analysis.summary.get('RECOMMENDATION', 'NEUTRAL').replace("_", " ")
                return rec, round(accuracy, 1)
        except:
            continue 
            
    return "NEUTRAL", 0

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 სიგნალის დაწყება", "ℹ️ ინფორმაცია")
    bot.send_message(message.chat.id, "🚨 **Tukha Signal** ჩართულია!", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "ℹ️ ინფორმაცია")
def info(message):
    text = (
        "🤖 **Tukha Signal Bot v3.1**\n\n"
        "ეს ბოტი აანალიზებს ბაზარს რეალურ დროში 20-ზე მეტი ტექნიკური ინდიკატორის გამოყენებით.\n\n"
        "💡 **ოქროს წესი:**\n"
        "ენდეთ მხოლოდ იმ სიგნალებს, რომელთა სიზუსტე **75%-ზე მაღალია**.\n\n"
        "⚠️ **ფორექსი არ მუშაობს შაბათ-კვირას!**"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🚀 სიგნალის დაწყება")
def show_pairs(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    btns = [types.InlineKeyboardButton(p, callback_data=f"p_{p}") for p in PAIRS]
    markup.add(*btns)
    bot.send_message(message.chat.id, "📊 აირჩიეთ სავაჭრო წყვილი:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("p_"))
def pick_time(call):
    pair = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(t, callback_data=f"s_{pair}_{t}") for t in TIMES.keys()]
    markup.add(*btns)
    bot.edit_message_text(f"💎 წყვილი: **{pair}**\n⏳ აირჩიეთ ვადა:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("s_"))
def get_signal(call):
    _, pair, t_label = call.data.split("_")
    bot.edit_message_text(f"🔍 ბაზრის სკანირება: **{pair}**...", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    
    res, acc = get_live_analysis(pair, TIMES[t_label])
    
    if "BUY" in res:
        icon = "🚀 STRONG BUY" if "STRONG" in res else "📈 BUY"
    elif "SELL" in res:
        icon = "🆘 STRONG SELL" if "STRONG" in res else "📉 SELL"
    else:
        icon = "⚖️ NEUTRAL"
    
    result_text = (
        f"🚨 **Tukha Signal LIVE** 🚨\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💎 წყვილი: `{pair}`\n"
        f"⏱ ვადა: `{t_label}`\n"
        f"📊 სიგნალი: **{icon}**\n"
        f"🎯 სიზუსტე: `{acc}%`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"✅ წარმატებულ ვაჭრობას გისურვებთ!"
    )
    bot.edit_message_text(result_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

# --- გაშვების და ავტომატური აღდგენის ლოგიკა ---
if __name__ == "__main__":
    keep_alive()
    print("Tukha Signal ბოტი ჩაირთვა...")
    
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"ბოტი დროებით გაჩერდა შეცდომის გამო: {e}")
            time.sleep(5)
