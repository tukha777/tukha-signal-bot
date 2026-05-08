import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread
import os
import time

app = Flask('')
@app.route('/')
def home(): return "Online"

def run():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

TOKEN = '8701731141:AAG-Q6mXdIv65BR-Zqn90ZGMc3M0D1xKwRk'
bot = telebot.TeleBot(TOKEN)

# მენიუში ბრძანების დაყენება
def set_bot_commands():
    bot.set_my_commands([
        types.BotCommand("start", "🚀 Restart & Menu")
    ])

# --- VIP წვდომის მქონე მომხმარებელთა სია ---
ALLOWED_USERS = [8696404791] 

user_lang = {}

STRINGS = {
    'ka': {
        'start': "🚨 **Tukha Signal** ჩართულია!",
        'info_btn': "ℹ️ ინფორმაცია",
        'signal_btn': "🚀 სიგნალის დაწყება",
        'lang_btn': "🌐 ენის შეცვლა",
        'choose_pair': "📊 აირჩიეთ წყვილი:",
        'choose_time': "⏳ აირჩიეთ ვადა:",
        'scanning': "🔍 სკანირება: **{}**...",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nეს ბოტი აანალიზებს ბაზარს რეალურ დროში 20-ზე მეტი ტექნიკური ინდიკატორის გამოყენებით.\n\n💡 **ოქროს წესი:**\nენდეთ მხოლოდ იმ სიგნალებს, რომელთა სიზუსტე **75%-ზე მაღალია**.\n\n⚠️ **ფორექსი არ მუშაობს შაბათ-კვირას!**",
        'accuracy': "🎯 სიზუსტე",
        'pair_label': "💎 წყვილი",
        'time_label': "⏱ ვადა",
        'signal_label': "📊 სიგნალი",
        'success': "✅ წარმატებულ ვაჭრობას გისურვებთ!",
        'paywall': "🚫 **წვდომა შეზღუდულია!**\n\nბოტის სიგნალების გამოსაყენებლად საჭიროა აქტივაცია.\n\n💰 **ფასი:** $30 (1 თვე)\n📩 **გასააქტიურებლად მომწერეთ:** @TukhaTheGreat"
    },
    'en': {
        'start': "🚨 **Tukha Signal** is Online!",
        'info_btn': "ℹ️ Information",
        'signal_btn': "🚀 Start Signal",
        'lang_btn': "🌐 Change Language",
        'choose_pair': "📊 Choose pair:",
        'choose_time': "⏳ Choose timeframe:",
        'scanning': "🔍 Scanning: **{}**...",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nThis bot analyzes the market in real-time using over 20 technical indicators.\n\n💡 **Golden Rule:**\nTrust only signals with an accuracy higher than **75%**.\n\n⚠️ **Forex market is closed on weekends!**",
        'accuracy': "🎯 Accuracy",
        'pair_label': "💎 Pair",
        'time_label': "⏱ Time",
        'signal_label': "📊 Signal",
        'success': "✅ Good luck!",
        'paywall': "🚫 **Access Denied!**\n\nActivation is required to use the signals.\n\n💰 **Price:** $30 (1 Month)\n📩 **Contact for activation:** @TukhaTheGreat"
    },
    'ru': {
        'start': "🚨 **Tukha Signal** Включен!",
        'info_btn': "ℹ️ Информация",
        'signal_btn': "🚀 Запустить сигнал",
        'lang_btn': "🌐 Сменить язык",
        'choose_pair': "📊 Выберите пару:",
        'choose_time': "⏳ Выберите таймфрейм:",
        'scanning': "🔍 Сканирование: **{}**...",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nЭтот бот анализирует рынок в реальном времени, используя более 20 технических индикаторов.\n\n💡 **Золотое правило:**\nДоверяйте только тем сигналам, точность которых выше **75%**.\n\n⚠️ **Форекс не работает по выходным!**",
        'accuracy': "🎯 Точность",
        'pair_label': "💎 Пара",
        'time_label': "⏱ Время",
        'signal_label': "📊 Сигнал",
        'success': "✅ Удачной торговли!",
        'paywall': "🚫 **Доступ ограничен!**\n\nДля использования сигналов требуется активация.\n\n💰 **Цена:** $30 (1 месяц)\n📩 **Для активации пишите:** @TukhaTheGreat"
    }
}

def get_main_keyboard(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(STRINGS[lang]['lang_btn'])
    markup.add(STRINGS[lang]['info_btn'])
    markup.add(STRINGS[lang]['signal_btn'])
    return markup

def get_lang_inline():
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🇬🇪 KA", callback_data="lang_ka"),
          types.InlineKeyboardButton("🇺🇸 EN", callback_data="lang_en"),
          types.InlineKeyboardButton("🇷🇺 RU", callback_data="lang_ru"))
    return m

@bot.message_handler(commands=['start'])
def start(message):
    lang = user_lang.get(message.from_user.id, 'en')
    bot.send_message(message.chat.id, STRINGS[lang]['start'], reply_markup=get_main_keyboard(lang), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in ["🌐 ენის შეცვლა", "🌐 Change Language", "🌐 Сменить язык"])
def show_lang_selection(message):
    bot.send_message(message.chat.id, "Choose Language / აირჩიეთ ენა:", reply_markup=get_lang_inline())

@bot.callback_query_handler(func=lambda c: c.data.startswith("lang_"))
def set_lang(call):
    lang = call.data.split("_")[1]
    user_lang[call.from_user.id] = lang
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, STRINGS[lang]['start'], reply_markup=get_main_keyboard(lang), parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['info_btn'] for l in STRINGS))
def info(message):
    lang = user_lang.get(message.from_user.id, 'en')
    bot.send_message(message.chat.id, STRINGS[lang]['info_text'], parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['signal_btn'] for l in STRINGS))
def show_pairs(message):
    lang = user_lang.get(message.from_user.id, 'en')
    if message.from_user.id not in ALLOWED_USERS:
        bot.send_message(message.chat.id, STRINGS[lang]['paywall'], parse_mode="Markdown")
        return
    markup = types.InlineKeyboardMarkup(row_width=3)
    btns = [types.InlineKeyboardButton(p, callback_data=f"p_{p}") for p in ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "XAUUSD", "XAGUSD"]]
    markup.add(*btns)
    bot.send_message(message.chat.id, STRINGS[lang]['choose_pair'], reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("p_"))
def pick_time(call):
    lang = user_lang.get(call.from_user.id, 'en')
    pair = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    times = {"1 MIN": Interval.INTERVAL_1_MINUTE, "5 MIN": Interval.INTERVAL_5_MINUTES, "15 MIN": Interval.INTERVAL_15_MINUTES, "30 MIN": Interval.INTERVAL_30_MINUTES}
    btns = [types.InlineKeyboardButton(t, callback_data=f"s_{pair}_{t}") for t in times.keys()]
    markup.add(*btns)
    bot.edit_message_text(f"💎 {STRINGS[lang]['pair_label']}: **{pair}**\n{STRINGS[lang]['choose_time']}", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("s_"))
def get_signal(call):
    lang = user_lang.get(call.from_user.id, 'en')
    _, pair, t_label = call.data.split("_")
    bot.edit_message_text(STRINGS[lang]['scanning'].format(pair), call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    res, acc = get_live_analysis(pair, t_label) 
    icon = "🚀 STRONG BUY" if "STRONG BUY" in res else "📈 BUY" if "BUY" in res else "🆘 STRONG SELL" if "STRONG SELL" in res else "📉 SELL" if "SELL" in res else "⚖️ NEUTRAL"
    txt = (f"🚨 **Tukha Signal LIVE** 🚨\n━━━━━━━━━━━━━━━\n"
           f"💎 {STRINGS[lang]['pair_label']}: `{pair}`\n⏱ {STRINGS[lang]['time_label']}: `{t_label}`\n"
           f"📊 {STRINGS[lang]['signal_label']}: **{icon}**\n🎯 {STRINGS[lang]['accuracy']}: `{acc}%`\n"
           f"━━━━━━━━━━━━━━━\n{STRINGS[lang]['success']}")
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

def get_live_analysis(pair, t_label):
    times = {"1 MIN": Interval.INTERVAL_1_MINUTE, "5 MIN": Interval.INTERVAL_5_MINUTES, "15 MIN": Interval.INTERVAL_15_MINUTES, "30 MIN": Interval.INTERVAL_30_MINUTES}
    interval = times[t_label]

    if "USDT" in pair:
        options = [{"scr": "crypto", "exch": "BINANCE"}, {"scr": "crypto", "exch": "BYBIT"}]
    elif pair in ["XAUUSD", "XAGUSD"]:
        # დამატებულია 'cfd' სკრინერი და TVC/OANDA ბირჟები ოქროსთვის
        options = [
            {"scr": "cfd", "exch": "TVC"}, 
            {"scr": "forex", "exch": "OANDA"},
            {"scr": "cfd", "exch": "OANDA"}
        ]
    else:
        options = [{"scr": "forex", "exch": "FX_IDC"}, {"scr": "forex", "exch": "OANDA"}]

    for opt in options:
        try:
            h = TA_Handler(symbol=pair, screener=opt["scr"], exchange=opt["exch"], interval=interval, timeout=10)
            h.headers = {'User-Agent': 'Mozilla/5.0'}
            a = h.get_analysis()
            b, s, n = a.summary.get('BUY', 0), a.summary.get('SELL', 0), a.summary.get('NEUTRAL', 0)
            total = b + s + n
            if total > 0:
                return a.summary.get('RECOMMENDATION', 'NEUTRAL').replace("_", " "), round(max(b, s) / total * 100, 1)
        except: continue
    return "NEUTRAL", 0

if __name__ == "__main__":
    set_bot_commands() # მენიუს ღილაკის გააქტიურება
    keep_alive()
    bot.polling(none_stop=True)
