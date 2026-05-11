import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread
import os
import time

# --- Flask Server (Keep Alive) ---
app = Flask('')
@app.route('/')
def home(): return "Tukha Signal is Running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# --- ბოტის მონაცემები ---
TOKEN = '8701731141:AAGaHtQjc49BY4_Kcu1ADsgywLEamb_Cdpk'
bot = telebot.TeleBot(TOKEN)

# ძველი კავშირების გაწყვეტა (Conflict 409-ის თავიდან ასაცილებლად)
try:
    bot.remove_webhook()
    time.sleep(1)
except:
    pass

# მომხმარებლის ენების შესანახი (დროებითი მეხსიერება)
user_lang = {}

PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "EURGBP", 
    "EURJPY", "GBPJPY", "EURAUD", "EURCAD", "AUDJPY", "CADJPY", "GBPAUD", "GBPCAD",
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT",
    "AVAXUSDT", "LINKUSDT", "MATICUSDT", "UNIUSDT", "LTCUSDT", "BCHUSDT", "ATOMUSDT", "XMRUSDT",
    "XAUUSD", "XAGUSD", "EURCHF", "GBPCHF", "AUDCAD", "AUDCHF", "AUDNZD", "CADCHF", "CHFJPY"
]

TIMES = {
    "1 MIN": Interval.INTERVAL_1_MINUTE,
    "5 MIN": Interval.INTERVAL_5_MINUTES,
    "15 MIN": Interval.INTERVAL_15_MINUTES,
    "30 MIN": Interval.INTERVAL_30_MINUTES
}

# ენების თარგმანები
STRINGS = {
    'en': {
        'welcome': "Welcome to **Tukha Signal**! Please choose your language:",
        'main_msg': "Select an option from the menu:",
        'lang_btn': "🌐 Language",
        'info_btn': "ℹ️ Information",
        'start_btn': "🚀 Start Signal",
        'choose_pair': "📊 Choose a pair:",
        'choose_time': "⏳ Pair: **{}**\nChoose timeframe:",
        'scanning': "🔍 Scanning the market...",
        'info_text': "🤖 **Tukha Signal Bot v3.0**\n\nReal-time market analysis.\n\n💡 **Tip:** Trust only signals with accuracy > 75%.",
        'pair_label': "💎 Pair",
        'time_label': "⏱ Time",
        'signal_label': "📊 Signal",
        'accuracy_label': "🎯 Accuracy",
        'success': "✅ Good luck with your trades!"
    },
    'ka': {
        'welcome': "მოგესალმებით **Tukha Signal**-ში! გთხოვთ, აირჩიოთ ენა:",
        'main_msg': "აირჩიეთ სასურველი ღილაკი:",
        'lang_btn': "🌐 ენის შეცვლა",
        'info_btn': "ℹ️ ინფორმაცია",
        'start_btn': "🚀 სიგნალის დაწყება",
        'choose_pair': "📊 აირჩიეთ წყვილი:",
        'choose_time': "⏳ წყვილი: **{}**\nაირჩიეთ ვადა:",
        'scanning': "🔍 ბაზრის სკანირება...",
        'info_text': "🤖 **Tukha Signal Bot v3.0**\n\nბაზრის ანალიზი რეალურ დროში.\n\n💡 **რჩევა:** ენდეთ მხოლოდ იმ სიგნალებს, რომელთა სიზუსტე 75%-ზე მაღალია.",
        'pair_label': "💎 წყვილი",
        'time_label': "⏱ ვადა",
        'signal_label': "📊 სიგნალი",
        'accuracy_label': "🎯 სიზუსტე",
        'success': "✅ წარმატებულ ვაჭრობას გისურვებთ!"
    },
    'ru': {
        'welcome': "Добро пожаловать в **Tukha Signal**! Пожалуйста, выберите язык:",
        'main_msg': "Выберите опцию из меню:",
        'lang_btn': "🌐 Сменить язык",
        'info_btn': "ℹ️ Информация",
        'start_btn': "🚀 Запустить сигнал",
        'choose_pair': "📊 Выберите пару:",
        'choose_time': "⏳ Пара: **{}**\nВыберите таймфрейм:",
        'scanning': "🔍 Сканирование рынка...",
        'info_text': "🤖 **Tukha Signal Bot v3.0**\n\nАнализ рынка в реальном времени.\n\n💡 **Совет:** Доверяйте только сигналам с точностью > 75%.",
        'pair_label': "💎 Пара",
        'time_label': "⏱ Время",
        'signal_label': "📊 Сигнал",
        'accuracy_label': "🎯 Точность",
        'success': "✅ Желаем удачной торговли!"
    }
}

def get_main_keyboard(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(STRINGS[lang]['lang_btn'])
    markup.row(STRINGS[lang]['info_btn'])
    markup.row(STRINGS[lang]['start_btn'])
    return markup

def get_lang_inline():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🇺🇸 English", callback_data="setlang_en"),
        types.InlineKeyboardButton("🇬🇪 ქართული", callback_data="setlang_ka"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="setlang_ru")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, STRINGS['en']['welcome'], reply_markup=get_lang_inline())

@bot.callback_query_handler(func=lambda call: call.data.startswith("setlang_"))
def set_language(call):
    lang = call.data.split("_")[1]
    user_lang[call.from_user.id] = lang
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, STRINGS[lang]['main_msg'], reply_markup=get_main_keyboard(lang))

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['lang_btn'] for l in STRINGS))
def change_lang(message):
    bot.send_message(message.chat.id, "Choose Language / აირჩიეთ ენა:", reply_markup=get_lang_inline())

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['info_btn'] for l in STRINGS))
def info(message):
    lang = user_lang.get(message.from_user.id, 'en')
    bot.send_message(message.chat.id, STRINGS[lang]['info_text'], parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['start_btn'] for l in STRINGS))
def show_pairs(message):
    lang = user_lang.get(message.from_user.id, 'en')
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(pair, callback_data=f"pair_{pair}") for pair in PAIRS]
    markup.add(*buttons)
    bot.send_message(message.chat.id, STRINGS[lang]['choose_pair'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pair_"))
def callback_pair(call):
    lang = user_lang.get(call.from_user.id, 'en')
    selected_pair = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(t, callback_data=f"time_{selected_pair}_{t}") for t in TIMES.keys()]
    markup.add(*buttons)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text=STRINGS[lang]['choose_time'].format(selected_pair), reply_markup=markup, parse_mode="Markdown")

def get_live_analysis(pair, interval):
    try:
        is_crypto = "USDT" in pair
        screener = "crypto" if is_crypto else "forex"
        exchange = "BINANCE" if is_crypto else "FX_IDC"
        analysis = TA_Handler(symbol=pair, screener=screener, exchange=exchange, interval=interval, timeout=10).get_analysis()
        summary = analysis.summary['RECOMMENDATION']
        buy, sell, neutral = analysis.summary['BUY'], analysis.summary['SELL'], analysis.summary['NEUTRAL']
        accuracy = max(buy, sell) / (buy + sell + neutral) * 100
        return summary, round(accuracy, 1)
    except:
        return "NEUTRAL", 0

@bot.callback_query_handler(func=lambda call: call.data.startswith("time_"))
def callback_signal(call):
    lang = user_lang.get(call.from_user.id, 'en')
    data = call.data.split("_")
    pair, time_label = data[1], data[2]
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=STRINGS[lang]['scanning'])
    
    recommendation, accuracy = get_live_analysis(pair, TIMES[time_label])
    
    icon = "🚀 STRONG BUY" if "STRONG_BUY" in recommendation else "📈 BUY" if "BUY" in recommendation else "🆘 STRONG SELL" if "STRONG_SELL" in recommendation else "📉 SELL" if "SELL" in recommendation else "⚖️ NEUTRAL"
    
    result_text = (
        f"🚨 **Tukha Signal LIVE** 🚨\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💎 {STRINGS[lang]['pair_label']}: `{pair}`\n"
        f"⏱ {STRINGS[lang]['time_label']}: `{time_label}`\n"
        f"📊 {STRINGS[lang]['signal_label']}: **{icon}**\n"
        f"🎯 {STRINGS[lang]['accuracy_label']}: `{accuracy}%`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{STRINGS[lang]['success']}"
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=result_text, parse_mode="Markdown")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
