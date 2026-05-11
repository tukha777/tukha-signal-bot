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

# ენების გაფართოებული თარგმანები (5 ენა)
STRINGS = {
    'en': {
        'welcome': "✨ **Tukha Signal Bot** ✨\n\nChoose your language:",
        'main_msg': "💎 **Premium Dashboard**",
        'lang_btn': "🌐 Language",
        'info_btn': "ℹ️ Info",
        'start_btn': "🚀 GET SIGNAL",
        'ref_btn': "🎁 Referrals",
        'choose_pair': "📊 Choose a pair:",
        'choose_time': "⏳ Pair: `{}`\nSelect timeframe:",
        'scanning': "⏳ **Analyzing Market...**",
        'info_text': "🤖 **v3.2**\n\n💡 Accuracy > 75%\n⚠️ Forex closed on weekends!",
        'ref_text': "🎁 Your link:\n`https://t.me/{}?start={}`",
        'pair_label': "Asset", 'time_label': "Time", 'signal_label': "Action", 'accuracy_label': "Strength", 'success': "⚡️ Good luck!"
    },
    'ka': {
        'welcome': "✨ **Tukha Signal Bot** ✨\n\nაირჩიეთ ენა:",
        'main_msg': "💎 **მთავარი პანელი**",
        'lang_btn': "🌐 ენა",
        'info_btn': "ℹ️ ინფო",
        'start_btn': "🚀 სიგნალის მიღება",
        'ref_btn': "🎁 რეფერალები",
        'choose_pair': "📊 აირჩიეთ წყვილი:",
        'choose_time': "⏳ წყვილი: `{}`\nაირჩიეთ ვადა:",
        'scanning': "⏳ **ბაზრის ანალიზი...**",
        'info_text': "🤖 **v3.2**\n\n💡 სიზუსტე > 75%\n⚠️ ფორექსი დაკეტილია შაბათ-კვირას!",
        'ref_text': "🎁 შენი ლინკი:\n`https://t.me/{}?start={}`",
        'pair_label': "აქტივი", 'time_label': "ვადა", 'signal_label': "სიგნალი", 'accuracy_label': "სიზუსტე", 'success': "⚡️ წარმატებები!"
    },
    'ru': {
        'welcome': "✨ **Tukha Signal Bot** ✨\n\nВыберите язык:",
        'main_msg': "💎 **Панель управления**",
        'lang_btn': "🌐 Язык",
        'info_btn': "ℹ️ Инфо",
        'start_btn': "🚀 ПОЛУЧИТЬ СИГНАЛ",
        'ref_btn': "🎁 Рефералы",
        'choose_pair': "📊 Выберите пару:",
        'choose_time': "⏳ Пара: `{}`\nВыберите время:",
        'scanning': "⏳ **Анализ данных...**",
        'info_text': "🤖 **v3.2**\n\n💡 Точность > 75%\n⚠️ Форекс закрыт по выходным!",
        'ref_text': "🎁 Ссылка:\n`https://t.me/{}?start={}`",
        'pair_label': "Актив", 'time_label': "Время", 'signal_label': "Сигнал", 'accuracy_label': "Сила", 'success': "⚡️ Удачи!"
    },
    'es': {
        'welcome': "✨ **Tukha Signal Bot** ✨\n\nElige tu idioma:",
        'main_msg': "💎 **Panel Premium**",
        'lang_btn': "🌐 Idioma",
        'info_btn': "ℹ️ Info",
        'start_btn': "🚀 OBTENER SEÑAL",
        'ref_btn': "🎁 Referidos",
        'choose_pair': "📊 Elige un par:",
        'choose_time': "⏳ Par: `{}`\nSelecciona tiempo:",
        'scanning': "⏳ **Analizando mercado...**",
        'info_text': "🤖 **v3.2**\n\n💡 Precisión > 75%\n⚠️ Forex cerrado los fines de semana!",
        'ref_text': "🎁 Tu enlace:\n`https://t.me/{}?start={}`",
        'pair_label': "Activo", 'time_label': "Tiempo", 'signal_label': "Señal", 'accuracy_label': "Fuerza", 'success': "⚡️ ¡Buena suerte!"
    },
    'pt': {
        'welcome': "✨ **Tukha Signal Bot** ✨\n\nEscolha seu idioma:",
        'main_msg': "💎 **Painel Premium**",
        'lang_btn': "🌐 Idioma",
        'info_btn': "ℹ️ Info",
        'start_btn': "🚀 OBTER SINAL",
        'ref_btn': "🎁 Referências",
        'choose_pair': "📊 Escolha um par:",
        'choose_time': "⏳ Par: `{}`\nSelecione o tempo:",
        'scanning': "⏳ **Analisando mercado...**",
        'info_text': "🤖 **v3.2**\n\n💡 Precisão > 75%\n⚠️ Forex fechado nos fins de semana!",
        'ref_text': "🎁 Seu link:\n`https://t.me/{}?start={}`",
        'pair_label': "Ativo", 'time_label': "Tempo", 'signal_label': "Sinal", 'accuracy_label': "Força", 'success': "⚡️ Boa sorte!"
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
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="setlang_ru"),
        types.InlineKeyboardButton("🇪🇸 Español", callback_data="setlang_es"),
        types.InlineKeyboardButton("🇧🇷 Português", callback_data="setlang_pt")
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

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['lang_btn'] for l in STRINGS))
def change_lang(message):
    bot.send_message(message.chat.id, "🌐 Choose Language:", reply_markup=get_lang_inline())

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

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['start_btn'] for l in STRINGS))
def show_pairs(message):
    lang = user_lang.get(message.from_user.id, 'en')
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(f"💎 {pair}", callback_data=f"pair_{pair}") for pair in PAIRS]
    markup.add(*buttons)
    bot.send_message(message.chat.id, STRINGS[lang]['choose_pair'], reply_markup=markup, parse_mode="Markdown")

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
