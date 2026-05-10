import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread
import os
import time
import datetime

app = Flask('')
@app.route('/')
def home(): return "Online"

def run():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

TOKEN = '8701731141:AAG-Q6mXdIv65BR-Zqn90ZGMc3M0D1xKwRk'
ADMIN_IDS = [8696404791, 8711448963] 

bot = telebot.TeleBot(TOKEN)

def set_bot_commands():
    bot.set_my_commands([
        types.BotCommand("start", "🚀 Restart & Menu")
    ])

ALLOWED_USERS = [8696404791, 8711448963] 
user_data = {} 
user_lang = {}

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
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nეს ბოტი აანალიზებს ბაზარს რეალურ დროში 20-ზე მეტი ტექნიკური ინდიკატორის გამოყენებით.\n\n💡 **ოქროს წესი:**\nენდეთ მხოლოდ იმ სიგნალებს, რომელთა სიზუსტე **75%-ზე მაღალია**.\n\n⚠️ **ფორექსი არ მუშაობს შაბათ-კვირას!**",
        'accuracy': "🎯 სიზუსტე",
        'pair_label': "💎 წყვილი",
        'time_label': "⏱ ვადა",
        'signal_label': "📊 სიგნალი",
        'success': "✅ წარმატებულ ვაჭრობას გისურვებთ!",
        'paywall': "🚫 **წვდომა შეზღუდულია!**\n\nბოტის გამოსაყენებლად საჭიროა VIP აქტივაცია.\n\n💰 **ფასი:** $30 (1 თვე)\n📩 **გასააქტიურებლად:** @TukhaTheGreat",
        'ref_msg': "🎁 **მოიწვიე მეგობარი და მიიღე VIP!**\n\nთუ შენი მეგობარი შეიძენს VIP-ს, შენ საჩუქრად მიიღებ **14 დღეს**.\n\nშენი ლინკი:\n`https://t.me/{}?start={}`",
        'ref_bonus': "🎁 გილოცავთ! თქვენმა რეფერალმა შეიძინა VIP. დაგერიცხათ +14 დღე!"
    },
    'en': {
        'start': "🚨 **Tukha Signal** is Online!",
        'info_btn': "ℹ️ Information",
        'signal_btn': "🚀 Start Signal",
        'lang_btn': "🌐 Change Language",
        'ref_btn': "🎁 Invite & Get VIP",
        'choose_pair': "📊 Choose pair:",
        'choose_time': "⏳ Choose timeframe:",
        'scanning': "🔍 Scanning: **{}**...",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nThis bot analyzes the market in real-time using over 20 technical indicators.\n\n💡 **Golden Rule:**\nTrust only signals with an accuracy higher than **75%**.\n\n⚠️ **Forex market is closed on weekends!**",
        'accuracy': "🎯 Accuracy",
        'pair_label': "💎 Pair",
        'time_label': "⏱ Time",
        'signal_label': "📊 Signal",
        'success': "✅ Good luck!",
        'paywall': "🚫 **Access Denied!**\n\nActivation is required.\n\n💰 **Price:** $30 (1 Month)\n📩 **Contact:** @TukhaTheGreat",
        'ref_msg': "🎁 **Invite a friend & Get VIP!**\n\nIf your friend buys VIP, you get **14 days** for free.\n\nYour link:\n`https://t.me/{}?start={}`",
        'ref_bonus': "🎁 Congratulations! Your referral purchased VIP. You received +14 days!"
    },
    'ru': {
        'start': "🚨 **Tukha Signal** Включен!",
        'info_btn': "ℹ️ Информация",
        'signal_btn': "🚀 Запустить сигнал",
        'lang_btn': "🌐 Сменить язык",
        'ref_btn': "🎁 Пригласить и получить VIP",
        'choose_pair': "📊 Выберите пару:",
        'choose_time': "⏳ Выберите таймфрейм:",
        'scanning': "🔍 Сканирование: **{}**...",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nЭтот боტ анализирует рынок в реальном времени, используя более 20 технических индикаторов.\n\n💡 **Золотое правило:**\nДоверяйте только тем сигналам, точность которых выше **75%**.\n\n⚠️ **Форекс не работает по выходным!**",
        'accuracy': "🎯 Точность",
        'pair_label': "💎 Пара",
        'time_label': "⏱ Время",
        'signal_label': "📊 Сигнал",
        'success': "✅ Удачной торговли!",
        'paywall': "🚫 **Доступ ограничен!**\n\nТребуется активация VIP.\n\n💰 **Цена:** $30 (1 месяц)\n📩 **Контакт:** @TukhaTheGreat",
        'ref_msg': "🎁 **Пригласи друга и получи VIP!**\n\nЕсли ваш друг купит VIP, вы получите **14 дней** бесплатно.\n\nВаша ссылка:\n`https://t.me/{}?start={}`",
        'ref_bonus': "🎁 Поздравляем! Ваш реферал купил VIP. Вам начислено +14 дней!"
    }
}

def get_main_keyboard(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(STRINGS[lang]['lang_btn'])
    markup.add(STRINGS[lang]['info_btn'])
    markup.add(STRINGS[lang]['signal_btn'])
    markup.add(STRINGS[lang]['ref_btn'])
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
        if parent_id:
            try: bot.send_message(parent_id, "🔔 ახალი რეფერალი შემოვიდა თქვენი ლინკით!")
            except: pass
    lang = user_lang.get(user_id, 'en')
    bot.send_message(message.chat.id, STRINGS[lang]['start'], reply_markup=get_main_keyboard(lang), parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['ref_btn'] for l in STRINGS))
def show_referral(message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, 'en')
    bot_username = bot.get_me().username
    bot.send_message(user_id, STRINGS[lang]['ref_msg'].format(bot_username, user_id), parse_mode="Markdown")

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
    user_id = message.from_user.id
    lang = user_lang.get(user_id, 'en')
    now = datetime.datetime.now()
    expiry = user_data.get(user_id, {}).get('expiry')
    if user_id not in ALLOWED_USERS and (not expiry or expiry < now):
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("🔑 Send my ID", callback_data=f"req_vip_{user_id}"))
        bot.send_message(message.chat.id, STRINGS[lang]['paywall'], reply_markup=m, parse_mode="Markdown")
        return
    markup = types.InlineKeyboardMarkup(row_width=3)
    # აქ დავაბრუნე ყველა წყვილი სრულად
    btns = [types.InlineKeyboardButton(p, callback_data=f"p_{p}") for p in [
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", 
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", 
        "XAUUSD", "XAGUSD"
    ]]
    markup.add(*btns)
    bot.send_message(message.chat.id, STRINGS[lang]['choose_pair'], reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("req_vip_"))
def request_vip(call):
    uid = call.data.split("_")[2]
    uname = call.from_user.username or "NoName"
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("✅ გააქტიურება (30 დღე)", callback_data=f"adm_act_{uid}"))
    for adm in ADMIN_IDS:
        try: bot.send_message(adm, f"🔔 VIP მოთხოვნა!\nUser: @{uname}\nID: `{uid}`", reply_markup=m, parse_mode="Markdown")
        except: pass
    bot.answer_callback_query(call.id, "Request sent!")

@bot.callback_query_handler(func=lambda c: c.data.startswith("adm_act_"))
def admin_activate(call):
    if call.from_user.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "Not an Admin!")
        return
    target_id = int(call.data.split("_")[2])
    activate_user_vip(target_id, 30)
    bot.edit_message_text(f"✅ მომხმარებელი {target_id} გააქტიურებულია!", call.message.chat.id, call.message.message_id)
    bot.send_message(target_id, "🎉 Your VIP access is activated for 30 days!")

def activate_user_vip(uid, days):
    now = datetime.datetime.now()
    if uid not in ALLOWED_USERS: ALLOWED_USERS.append(uid)
    current_expiry = user_data.get(uid, {}).get('expiry')
    if current_expiry and current_expiry > now:
        new_expiry = current_expiry + datetime.timedelta(days=days)
    else:
        new_expiry = now + datetime.timedelta(days=days)
    if uid not in user_data: user_data[uid] = {'referred_by': None}
    user_data[uid]['expiry'] = new_expiry
    parent_id = user_data[uid].get('referred_by')
    if parent_id:
        p_lang = user_lang.get(parent_id, 'en')
        if parent_id not in ALLOWED_USERS: ALLOWED_USERS.append(parent_id)
        p_expiry = user_data.get(parent_id, {}).get('expiry') or now
        user_data[parent_id]['expiry'] = (p_expiry if p_expiry > now else now) + datetime.timedelta(days=14)
        try: bot.send_message(parent_id, STRINGS[p_lang]['ref_bonus'])
        except: pass

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
    interval = times.get(t_label, Interval.INTERVAL_1_MINUTE)
    try:
        scr = "crypto" if "USDT" in pair else "cfd" if "XAU" in pair else "forex"
        exch = "BINANCE" if scr == "crypto" else "TVC" if "XAU" in pair else "FX_IDC"
        h = TA_Handler(symbol=pair, screener=scr, exchange=exch, interval=interval, timeout=10)
        a = h.get_analysis()
        b, s, n = a.summary.get('BUY', 0), a.summary.get('SELL', 0), a.summary.get('NEUTRAL', 0)
        total = b + s + n
        return a.summary.get('RECOMMENDATION', 'NEUTRAL').replace("_", " "), round(max(b, s) / total * 100, 1) if total > 0 else 0
    except: return "NEUTRAL", 0

if __name__ == "__main__":
    set_bot_commands()
    keep_alive()
    bot.polling(none_stop=True)
