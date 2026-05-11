import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread
import os
import datetime

app = Flask('')
@app.route('/')
def home(): return "Online"

def run():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# --- მონაცემები ---
TOKEN = '8701731141:AAEGU30fsTusslDUtgvWFmgvnGJW20M1368'
ADMIN_IDS = [8696404791, 8711448963]
ALLOWED_USERS = [8696404791, 8711448963]
user_data = {}
user_lang = {}

bot = telebot.TeleBot(TOKEN)

STRINGS = {
    'ka': {
        'start': "🚨 **Tukha Signal** ჩართულია!",
        'info_btn': "ℹ️ ინფორმაცია",
        'signal_btn': "🚀 სიგნალის დაწყება",
        'lang_btn': "🌐 ენის შეცვლა",
        'ref_btn': "🎁 მოიწვიე მეგობარი და მიიღე VIP",
        'choose_pair': "📊 აირჩიეთ წყვილი:",
        'choose_time': "⏳ აირჩიეთ ვადა:",
        'scanning': "🔍 სკანირება: **{}**...",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nბოტი აანალიზებს ბირჟებს რეალურ დროში.\n\n💡 **ოქროს წესი:**\nენდეთ მხოლოდ იმ სიგნალებს, რომელთა სიზუსტე **75%-ზე მაღალია**.\n\n⚠️ **ფორექსი არ მუშაობს შაბათ-კვირას!**",
        'accuracy': "🎯 სიზუსტე",
        'pair_label': "💎 წყვილი",
        'time_label': "⏱ ვადა",
        'signal_label': "📊 სიგნალი",
        'success': "✅ წარმატებულ ვაჭრობას გისურვებთ!",
        'paywall': "🚫 **წვდომა შეზღუდულია!**\n\nბოტის გამოსაყენებლად საჭიროა VIP აქტივაცია.\n\n💰 **ფასი:** $30 (1 თვე)\n📩 **გასააქტიურებლად:** @TukhaTheGreat",
        'ref_msg': "🎁 **მოიწვიე მეგობარი და მიიღე VIP!**\n\nშენი ლინკი:\n`https://t.me/{}?start={}`",
        'ref_bonus': "🎁 გილოცავთ! თქვენმა რეფერალმა შეიძინა VIP. დაგერიცხათ +14 დღე!"
    },
    'en': {
        'start': "🚨 **Tukha Signal** is Online!",
        'info_btn': "ℹ️ Information",
        'signal_btn': "🚀 Start Signal",
        'lang_btn': "🌐 Change Language",
        'ref_btn': "🎁 Invite Friend & Get VIP",
        'choose_pair': "📊 Choose pair:",
        'choose_time': "⏳ Choose timeframe:",
        'scanning': "🔍 Scanning: **{}**...",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nReal-time analysis for Forex and Crypto.\n\n💡 **Golden Rule:**\nTrust signals with accuracy > **75%**.\n\n⚠️ **Forex market is closed on weekends!**",
        'accuracy': "🎯 Accuracy",
        'pair_label': "💎 Pair",
        'time_label': "⏱ Time",
        'signal_label': "📊 Signal",
        'success': "✅ Good luck!",
        'paywall': "🚫 **Access Denied!**\n\nActivation is required.\n\n💰 **Price:** $30 (1 Month)\n📩 **Contact:** @TukhaTheGreat",
        'ref_msg': "🎁 **Invite a friend & Get VIP!**\n\nYour link:\n`https://t.me/{}?start={}`",
        'ref_bonus': "🎁 Congratulations! Your referral purchased VIP. You received +14 days!"
    },
    'ru': {
        'start': "🚨 **Tukha Signal** Включен!",
        'info_btn': "ℹ️ Информация",
        'signal_btn': "🚀 Запустить сигнал",
        'lang_btn': "🌐 Сменить язык",
        'ref_btn': "🎁 Пригласить друга и получить VIP",
        'choose_pair': "📊 Выберите пару:",
        'choose_time': "⏳ Выберите таймфрейм:",
        'scanning': "🔍 Сканирование: **{}**...",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nБот анализирует рынок в реальном времени.\n\n💡 **Золотое правило:**\nДоверяйте сигналам с точностью выше **75%**.\n\n⚠️ **Форекс не работает по выходным!**",
        'accuracy': "🎯 Точность",
        'pair_label': "💎 Пара",
        'time_label': "⏱ Время",
        'signal_label': "📊 Сигнал",
        'success': "✅ Удачной торговли!",
        'paywall': "🚫 **Доступ ограничен!**\n\nТребуется VIP активация.\n\n💰 **Цена:** $30 (1 месяц)\n📩 **Контакт:** @TukhaTheGreat",
        'ref_msg': "🎁 **Пригласи друга и получи VIP!**\n\nТвоя ссылка:\n`https://t.me/{}?start={}`",
        'ref_bonus': "🎁 Поздравляем! Ваш реферал купил VIP. Вам начислено +14 дней!"
    }
}

def get_main_keyboard(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(STRINGS[lang]['lang_btn'])
    markup.row(STRINGS[lang]['info_btn'])
    markup.row(STRINGS[lang]['signal_btn'])
    markup.row(STRINGS[lang]['ref_btn'])
    return markup

def get_lang_inline():
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🇬🇪 KA", callback_data="lang_ka"),
          types.InlineKeyboardButton("🇺🇸 EN", callback_data="lang_en"),
          types.InlineKeyboardButton("🇷🇺 RU", callback_data="lang_ru"))
    return m

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()
    if user_id not in user_data:
        parent_id = None
        if len(args) > 1:
            try:
                parent_id = int(args[1])
                if parent_id == user_id: parent_id = None
            except: parent_id = None
        user_data[user_id] = {'expiry': None, 'referred_by': parent_id}
    lang = user_lang.get(user_id, 'ka')
    bot.send_message(message.chat.id, STRINGS[lang]['start'], reply_markup=get_main_keyboard(lang), parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['lang_btn'] for l in STRINGS))
def show_lang_selection(message):
    bot.send_message(message.chat.id, "Choose Language / აირჩიეთ ენა:", reply_markup=get_lang_inline())

@bot.callback_query_handler(func=lambda c: c.data.startswith("lang_"))
def set_lang(call):
    lang = call.data.split("_")[1]
    user_lang[call.from_user.id] = lang
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, STRINGS[lang]['start'], reply_markup=get_main_keyboard(lang), parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['info_btn'] for l in STRINGS))
def info_handler(message):
    lang = user_lang.get(message.from_user.id, 'ka')
    bot.send_message(message.chat.id, STRINGS[lang]['info_text'], parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['ref_btn'] for l in STRINGS))
def show_referral(message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, 'ka')
    bot_username = bot.get_me().username
    bot.send_message(user_id, STRINGS[lang]['ref_msg'].format(bot_username, user_id), parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['signal_btn'] for l in STRINGS))
def show_pairs(message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, 'ka')
    now = datetime.datetime.now()
    expiry = user_data.get(user_id, {}).get('expiry')
    if user_id not in ALLOWED_USERS and (not expiry or (expiry and expiry < now)):
        bot.send_message(message.chat.id, STRINGS[lang]['paywall'], parse_mode="Markdown")
        return
    markup = types.InlineKeyboardMarkup(row_width=3)
    btns = [types.InlineKeyboardButton(p, callback_data=f"p_{p}") for p in [
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
        "BTCUSDT", "ETHUSDT"
    ]]
    markup.add(*btns)
    bot.send_message(message.chat.id, STRINGS[lang]['choose_pair'], reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("p_"))
def pick_time(call):
    lang = user_lang.get(call.from_user.id, 'ka')
    pair = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    times = ["1 MIN", "5 MIN", "15 MIN", "30 MIN"]
    btns = [types.InlineKeyboardButton(t, callback_data=f"s_{pair}_{t}") for t in times]
    markup.add(*btns)
    bot.edit_message_text(f"💎 {pair}\n{STRINGS[lang]['choose_time']}", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("s_"))
def get_signal(call):
    lang = user_lang.get(call.from_user.id, 'ka')
    _, pair, t_label = call.data.split("_")
    bot.edit_message_text(STRINGS[lang]['scanning'].format(pair), call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    
    res, acc = get_live_analysis(pair, t_label)
    
    if acc == 0:
        bot.edit_message_text("⚠️ Error: No data. (Market may be closed)", call.message.chat.id, call.message.message_id)
        return

    icon = "🚀 STRONG BUY" if "STRONG" in res and "BUY" in res else "📈 BUY" if "BUY" in res else "🆘 STRONG SELL" if "STRONG" in res and "SELL" in res else "📉 SELL" if "SELL" in res else "⚖️ NEUTRAL"
    txt = (f"🚨 **Tukha Signal LIVE** 🚨\n━━━━━━━━━━━━━━━\n"
           f"💎 {STRINGS[lang]['pair_label']}: `{pair}`\n⏱ {STRINGS[lang]['time_label']}: `{t_label}`\n"
           f"📊 {STRINGS[lang]['signal_label']}: **{icon}**\n🎯 {STRINGS[lang]['accuracy']}: `{acc}%`\n"
           f"━━━━━━━━━━━━━━━\n{STRINGS[lang]['success']}")
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

def get_live_analysis(pair, t_label):
    intervals = {
        "1 MIN": Interval.INTERVAL_1_MINUTE, 
        "5 MIN": Interval.INTERVAL_5_MINUTES, 
        "15 MIN": Interval.INTERVAL_15_MINUTES, 
        "30 MIN": Interval.INTERVAL_30_MINUTES
    }
    interval = intervals.get(t_label, Interval.INTERVAL_1_MINUTE)
    
    # კოდის ფიქსი: Screener და Exchange სწორად შერჩევა
    if "USDT" in pair:
        scr = "crypto"
        exch = "BINANCE"
    else:
        scr = "forex"
        exch = "FX_IDC" # უფრო სტაბილური ფორექს წყარო

    try:
        h = TA_Handler(symbol=pair, screener=scr, exchange=exch, interval=interval, timeout=10)
        a = h.get_analysis()
        buy, sell = a.summary.get('BUY', 0), a.summary.get('SELL', 0)
        neutral = a.summary.get('NEUTRAL', 0)
        total = buy + sell + neutral
        if total > 0:
            accuracy = round(max(buy, sell) / total * 100, 1)
            return a.summary.get('RECOMMENDATION', 'NEUTRAL'), accuracy
    except:
        return "NEUTRAL", 0
    return "NEUTRAL", 0

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
