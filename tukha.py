import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread
import os
import time

# --- Flask Server ---
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

# 🛑 ჩაწერე აქ შენი და იმ იუზერების ID, ვისაც VIP წვდომა აქვთ
ALLOWED_USERS = [8696404791, 8711448963] 

try:
    bot.remove_webhook()
    time.sleep(1)
except:
    pass

user_lang = {}

PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY", "AUDUSD", "USDCAD", "BTCUSDT"]

TIMES = {
    "1 MIN": Interval.INTERVAL_1_MINUTE,
    "5 MIN": Interval.INTERVAL_5_MINUTES,
    "15 MIN": Interval.INTERVAL_15_MINUTES,
    "30 MIN": Interval.INTERVAL_30_MINUTES
}

STRINGS = {
    'en': {
        'welcome': "✨ **Tukha Signal Bot** ✨\n\nChoose your language:",
        'main_msg': "💎 **Main Menu**",
        'lang_btn': "🌐 Language",
        'info_btn': "ℹ️ Information",
        'start_btn': "🚀 Start Signal",
        'ref_btn': "🎁 Invite Friends",
        'paywall': "🚫 **Access Denied!**\n\nActivation is required to use the signals.\n\n💰 **Price:** $30 (1 Month)\n📩 **Contact:** @TukhaTheGreat",
        'choose_pair': "📊 Choose a pair:",
        'choose_time': "⏳ Pair: `{}`\nChoose timeframe:",
        'scanning': "🔍 Scanning...",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nThe bot analyzes Forex and major Crypto pairs in real-time.\n\n💡 **Golden Rule:**\nTrust only signals with accuracy higher than 75%.\n\n⚠️ **Forex does not work on weekends!**",
        'ref_text': "🎁 Your referral link:\n`https://t.me/{}?start={}`",
        'pair_label': "Asset", 'time_label': "Time", 'signal_label': "Signal", 'accuracy_label': "Accuracy", 'success': "✅ Good luck!"
    },
    'ka': {
        'welcome': "✨ **Tukha Signal Bot** ✨\n\nაირჩიეთ ენა:",
        'main_msg': "💎 **მთავარი მენიუ**",
        'lang_btn': "🌐 ენა",
        'info_btn': "ℹ️ ინფორმაცია",
        'start_btn': "🚀 სიგნალის დაწყება",
        'ref_btn': "🎁 მეგობრების მოწვევა",
        'paywall': "🚫 **წვდომა შეზღუდულია!**\n\nსიგნალების გამოსაყენებლად საჭიროა VIP აქტივაცია.\n\n💰 **ფასი:** $30 (1 თვე)\n📩 **გასააქტიურებლად:** @TukhaTheGreat",
        'choose_pair': "📊 აირჩიეთ წყვილი:",
        'choose_time': "⏳ წყვილი: `{}`\nაირჩიეთ ვადა:",
        'scanning': "🔍 სკანირება...",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nბოტი აანალიზებს ფორექსსა და მთავარ კრიპტო წყვილებს რეალურ დროში.\n\n💡 **ოქროს წესი:**\nენდეთ მხოლოდ იმ სიგნალებს, რომელთა სიზუსტე 75%-ზე მაღალია.\n\n⚠️ **ფორექსი არ მუშაობს შაბათ-კვირას!**",
        'ref_text': "🎁 შენი ლინკი:\n`https://t.me/{}?start={}`",
        'pair_label': "აქტივი", 'time_label': "ვადა", 'signal_label': "სიგნალი", 'accuracy_label': "სიზუსტე", 'success': "✅ წარმატებულ ვაჭრობას გისურვებთ!"
    },
    'ru': {
        'welcome': "✨ **Tukha Signal Bot** ✨\n\nВыберите язык:",
        'main_msg': "💎 **Главное меню**",
        'lang_btn': "🌐 Язык",
        'info_btn': "ℹ️ Информация",
        'start_btn': "🚀 Запустить сигнал",
        'ref_btn': "🎁 Пригласить друзей",
        'paywall': "🚫 **Доступ ограничен!**\n\nДля использования сигналов нужна VIP активация.\n\n💰 **Цена:** $30 (1 месяц)\n📩 **Контакт:** @TukhaTheGreat",
        'choose_pair': "📊 Выберите пару:",
        'choose_time': "⏳ Пара: `{}`\nВыберите таймфрейм:",
        'scanning': "🔍 Сканирование...",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nБот анализирует Форекс и Крипто в реальном времени.\n\n💡 **Золотое правило:**\nДоверяйте сигналам выше 75%.",
        'ref_text': "🎁 Ссылка:\n`https://t.me/{}?start={}`",
        'pair_label': "Актив", 'time_label': "Время", 'signal_label': "Сигнал", 'accuracy_label': "Точность", 'success': "✅ Удачи!"
    }
}

def get_main_keyboard(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(STRINGS[lang]['lang_btn'], STRINGS[lang]['info_btn'])
    markup.row(STRINGS[lang]['start_btn'])
    markup.row(STRINGS[lang]['ref_btn'])
    return markup

def get_lang_inline():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇺🇸 English", callback_data="setlang_en"),
        types.InlineKeyboardButton("🇬🇪 ქართული", callback_data="setlang_ka"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="setlang_ru")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, STRINGS['en']['welcome'], reply_markup=get_lang_inline(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("setlang_"))
def set_language(call):
    lang = call.data.split("_")[1]
    user_lang[call.from_user.id] = lang
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, STRINGS[lang]['main_msg'], reply_markup=get_main_keyboard(lang), parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['start_btn'] for l in STRINGS))
def show_pairs(message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, 'en')
    
    # 🛑 შემოწმება: არის თუ არა მომხმარებელი დაშვებული
    if user_id not in ALLOWED_USERS:
        bot.send_message(message.chat.id, STRINGS[lang]['paywall'], parse_mode="Markdown")
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(f"💎 {pair}", callback_data=f"pair_{pair}") for pair in PAIRS]
    markup.add(*buttons)
    bot.send_message(message.chat.id, STRINGS[lang]['choose_pair'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['info_btn'] for l in STRINGS))
def info(message):
    lang = user_lang.get(message.from_user.id, 'en')
    bot.send_message(message.chat.id, STRINGS[lang]['info_text'], parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['ref_btn'] for l in STRINGS))
def referral(message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, 'en')
    bot_username = bot.get_me().username
    bot.send_message(user_id, STRINGS[lang]['ref_text'].format(bot_username, user_id), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("pair_"))
def callback_pair(call):
    lang = user_lang.get(call.from_user.id, 'en')
    selected_pair = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(f"⏱ {t}", callback_data=f"time_{selected_pair}_{t}") for t in TIMES.keys()]
    markup.add(*buttons)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text=STRINGS[lang]['choose_time'].format(selected_pair), reply_markup=markup, parse_mode="Markdown")

def get_live_analysis(pair, interval):
    try:
        is_crypto = "USDT" in pair
        screener = "crypto" if is_crypto else "forex"
        exchange = "BINANCE" if is_crypto else "OANDA"
        analysis = TA_Handler(symbol=pair, screener=screener, exchange=exchange, interval=interval, timeout=10).get_analysis()
        summary = analysis.summary['RECOMMENDATION']
        buy, sell, neutral = analysis.summary['BUY'], analysis.summary['SELL'], analysis.summary['NEUTRAL']
        total = buy + sell + neutral
        accuracy = max(buy, sell) / total * 100 if total > 0 else 0
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
        f"🌟 **TUKHA SIGNAL LIVE** 🌟\n"
        f"──────────────────\n"
        f"💎 {STRINGS[lang]['pair_label']}: `{pair}`\n"
        f"⏱ {STRINGS[lang]['time_label']}: `{time_label}`\n"
        f"📊 {STRINGS[lang]['signal_label']}: **{icon}**\n"
        f"🎯 {STRINGS[lang]['accuracy_label']}: `{accuracy}%`\n"
        f"──────────────────\n"
        f"{STRINGS[lang]['success']}"
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=result_text, parse_mode="Markdown")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
bot.remove_webhook()
time.sleep(2)
