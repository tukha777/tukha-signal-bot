import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread
import os
import time
import sqlite3
from datetime import datetime, timedelta

# --- Flask Server (Keep Alive) ---
app = Flask('')
@app.route('/')
def home(): return "Tukha Signal is Running!"

def run():
    try:
        port = int(os.environ.get("PORT", 8080))
        app.run(host='0.0.0.0', port=port, use_reloader=False)
    except Exception as e:
        print(f"Flask error: {e}")

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()

# --- ბოტის მონაცემები ---
TOKEN = '8701731141:AAGaHtQjc49BY4_Kcu1ADsgywLEamb_Cdpk'
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 8696404791 
CHANNEL_ID = "@TukhaSignals" # აქ ჩაწერე შენი არხის ID ავტო-სიგნალებისთვის

# --- მონაცემთა ბაზა ---
def init_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, expiry_date TEXT, selected_lang TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS alerts 
                      (user_id INTEGER, pair TEXT, target_price REAL)''')
    conn.commit()
    conn.close()

def add_vip_days(user_id, days):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT expiry_date FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    now = datetime.now()
    if row and row[0]:
        try:
            current_expiry = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
            new_expiry = max(current_expiry, now) + timedelta(days=days)
        except:
            new_expiry = now + timedelta(days=days)
    else:
        new_expiry = now + timedelta(days=days)
    cursor.execute("INSERT OR REPLACE INTO users (user_id, expiry_date, selected_lang) VALUES (?, ?, ?)", 
                   (user_id, new_expiry.strftime('%Y-%m-%d %H:%M:%S'), get_user_lang(user_id)))
    conn.commit()
    conn.close()
    return new_expiry

def update_user_lang(user_id, lang):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, selected_lang) VALUES (?, ?)", (user_id, lang))
    cursor.execute("UPDATE users SET selected_lang = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()
    conn.close()

def get_user_lang(user_id):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT selected_lang FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else 'en'

def is_vip(user_id):
    if user_id == ADMIN_ID: return True
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT expiry_date FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        try:
            return datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') > datetime.now()
        except: return False
    return False

init_db()

# --- მონაცემები ---
PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY", "AUDUSD", "USDCAD", "BTCUSDT"]
TIMES = {"1 MIN": Interval.INTERVAL_1_MINUTE, "5 MIN": Interval.INTERVAL_5_MINUTES, 
         "15 MIN": Interval.INTERVAL_15_MINUTES, "30 MIN": Interval.INTERVAL_30_MINUTES}

STRINGS = {
    'en': {
        'main_msg': "💎 **Main Menu**\n──────────────────\nPlease select the desired button:",
        'lang_btn': "🌐 Language", 'info_btn': "ℹ️ Information", 'start_btn': "🚀 Start Signal", 'ref_btn': "🎁 Invite Friends",
        'calc_btn': "🧮 Calculator", 'alert_btn': "🔔 Price Alert",
        'paywall': "🚫 **Access Denied!**\nActivation required.\n📩 @TukhaTheGreat",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nThe bot analyzes Forex and major Crypto pairs in real-time.\n\n💡 **Golden Rule:**\nTrust only signals with accuracy higher than 75%.",
        'ref_text': "🎁 **Referral System**\n──────────────────\nInvite a friend and get **+7 Days VIP**!\n🔗 `https://t.me/{}?start={}`",
        'vip_msg': "🎉 **VIP Status Activated!**\nYou have access for {} days. ✅ We wish you a successful trade!",
        'asset': "Asset", 'time': "Time", 'signal': "Signal", 'accuracy': "Accuracy", 'success': "✅ We wish you a successful trade!"
    },
    'ka': {
        'main_msg': "💎 **მთავარი მენიუ**\n──────────────────\nაირჩიეთ სასურველი ღილაკი:",
        'lang_btn': "🌐 ენა", 'info_btn': "ℹ️ ინფორმაცია", 'start_btn': "🚀 სიგნალის დაწყება", 'ref_btn': "🎁 მეგობრები",
        'calc_btn': "🧮 კალკულატორი", 'alert_btn': "🔔 ფასის შეტყობინება",
        'paywall': "🚫 **წვდომა შეზღუდულია!**\nსაჭიროა VIP აქტივაცია.\n📩 @TukhaTheGreat",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nბოტი აანალიზებს ფორექსსა და მთავარ კრიპტო წყვილებს რეალურ დროში.\n\n💡 **ოქროს წესი:**\nენდეთ მხოლოდ იმ სიგნალებს, რომელთა სიზუსტე 75%-ზე მაღალია.",
        'ref_text': "🎁 **რეფერალური სისტემა**\n──────────────────\nმოიწვიე მეგობარი და მიიღე **+7 დღე VIP**!\n🔗 `https://t.me/{}?start={}`",
        'vip_msg': "🎉 **VIP სტატუსი გააქტიურდა!**\nთქვენ გაქვთ წვდომა {} დღით. ✅ წარმატებულ ვაჭრობას გისურვებთ!",
        'asset': "აქტივი", 'time': "ვადა", 'signal': "სიგნალი", 'accuracy': "სიზუსტე", 'success': "✅ წარმატებულ ვაჭრობას გისურვებთ!"
    }
}
# შენიშვნა: სხვა ენები (ru, es, pt, tr, hi, ar) დაემატება ანალოგიურად

def get_main_kbd(l):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row(STRINGS[l]['lang_btn'], STRINGS[l]['info_btn'])
    m.row(STRINGS[l]['start_btn'])
    m.row(STRINGS[l]['ref_btn'], STRINGS[l]['calc_btn'])
    m.row(STRINGS[l]['alert_btn'])
    return m

# --- ავტომატური სიგნალების ფუნქცია (Background Task) ---
def auto_signal_task():
    while True:
        try:
            for pair in PAIRS:
                handler = TA_Handler(symbol=pair, screener="crypto" if "BTC" in pair else "forex", 
                                    exchange="BINANCE" if "BTC" in pair else "OANDA", 
                                    interval=Interval.INTERVAL_15_MINUTES, timeout=10)
                analysis = handler.get_analysis()
                buy, sell, neut = analysis.summary['BUY'], analysis.summary['SELL'], analysis.summary['NEUTRAL']
                acc = round(max(buy, sell) / (buy + sell + neut) * 100, 1)
                
                if acc >= 90: # მხოლოდ 90%+ სიგნალები არხისთვის
                    rec = analysis.summary['RECOMMENDATION']
                    icon = "🚀 STRONG BUY" if "STRONG" in rec and "BUY" in rec else "🆘 STRONG SELL"
                    msg = f"🔥 **VIP AUTO SIGNAL (90%+)** 🔥\n──────────────────\n💎 Asset: `{pair}`\n📊 Signal: **{icon}**\n🎯 Accuracy: `{acc}%`\n──────────────────\n👉 Get more: @{bot.get_me().username}"
                    bot.send_message(CHANNEL_ID, msg, parse_mode="Markdown")
            time.sleep(1800) # ყოველ 30 წუთში შემოწმება
        except: time.sleep(60)

# --- HANDLERS ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(*(types.InlineKeyboardButton(f"{d} {n}", callback_data=f"setlang_{c}") 
               for d, n, c in [("🇺🇸", "English", "en"), ("🇬🇪", "ქართული", "ka"), ("🇷🇺", "Русский", "ru"), 
                              ("🇪🇸", "Español", "es"), ("🇧🇷", "Português", "pt"), ("🇹🇷", "Türkçe", "tr"), 
                              ("🇮🇳", "हिन्दी", "hi"), ("🇸🇦", "العربية", "ar")]))
    bot.send_message(message.chat.id, "✨ **Select Language** ✨", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("setlang_"))
def callback_set_lang(call):
    lang = call.data.split("_")[1]
    update_user_lang(call.from_user.id, lang)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, STRINGS.get(lang, STRINGS['en'])['main_msg'], 
                     reply_markup=get_main_kbd(lang), parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    l = get_user_lang(uid)
    l_str = STRINGS.get(l, STRINGS['en'])
    txt = message.text

    if txt == l_str['start_btn']:
        if not is_vip(uid):
            bot.send_message(message.chat.id, l_str['paywall'], parse_mode="Markdown")
            return
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(*[types.InlineKeyboardButton(f"💎 {p}", callback_data=f"pair_{p}") for p in PAIRS])
        bot.send_message(message.chat.id, "📊 **Market Selection**", reply_markup=markup)

    elif txt == l_str['calc_btn']:
        bot.send_message(message.chat.id, "🧮 **Lot Calculator**\n──────────────────\nUsage: `/calc BALANCE RISK_PERCENT`\nExample: `/calc 1000 2` (2% risk on $1000 balance)")

    elif txt == l_str['info_btn']:
        bot.send_message(message.chat.id, l_str['info_text'], parse_mode="Markdown")

    elif txt == l_str['ref_btn']:
        bot.send_message(uid, l_str['ref_text'].format(bot.get_me().username, uid), parse_mode="Markdown")

# --- კალკულატორის ლოგიკა ---
@bot.message_handler(commands=['calc'])
def calc_lots(message):
    try:
        parts = message.text.split()
        balance = float(parts[1])
        risk = float(parts[2])
        amount = (balance * risk) / 100
        res = f"🧮 **Risk Calculation:**\n──────────────────\n💰 Balance: `${balance}`\n🎲 Risk: `{risk}%`\n📉 Risk Amount: **`${amount}`**"
        bot.reply_to(message, res, parse_mode="Markdown")
    except: bot.reply_to(message, "❌ Use: `/calc 1000 2`", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("pair_"))
def callback_pair(call):
    l = get_user_lang(call.from_user.id)
    pair = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(*(types.InlineKeyboardButton(f"⏱ {t}", callback_data=f"time_{pair}_{t}") for t in TIMES.keys()))
    bot.edit_message_text(f"⏳ **Asset: {pair}**", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("time_"))
def final_signal(call):
    l = get_user_lang(call.from_user.id)
    l_str = STRINGS.get(l, STRINGS['en'])
    pair, t_label = call.data.split("_")[1], call.data.split("_")[2]
    bot.edit_message_text("🔍 Scanning...", call.message.chat.id, call.message.message_id)
    try:
        handler = TA_Handler(symbol=pair, screener="crypto" if "BTC" in pair else "forex", 
                            exchange="BINANCE" if "BTC" in pair else "OANDA", 
                            interval=TIMES[t_label], timeout=10)
        analysis = handler.get_analysis()
        rec = analysis.summary['RECOMMENDATION']
        buy, sell, neut = analysis.summary['BUY'], analysis.summary['SELL'], analysis.summary['NEUTRAL']
        acc = round(max(buy, sell) / (buy + sell + neut) * 100, 1)
        icon = "🚀 STRONG BUY" if "STRONG_BUY" in rec else "📈 BUY" if "BUY" in rec else "🆘 STRONG SELL" if "STRONG_SELL" in rec else "📉 SELL" if "SELL" in rec else "⚖️ NEUTRAL"
        
        res = (f"🌟 **TUKHA SIGNAL LIVE** 🌟\n──────────────────\n"
               f"💎 {l_str['asset']}: `{pair}`\n⏱️ {l_str['time']}: `{t_label}`\n"
               f"📊 {l_str['signal']}: **{icon}**\n🎯 {l_str['accuracy']}: `{acc}%`\n"
               f"──────────────────\n{l_str['success']}")
        bot.edit_message_text(res, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    except: bot.edit_message_text("❌ Error", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    init_db()
    keep_alive()
    Thread(target=auto_signal_task, daemon=True).start() # ავტო-სიგნალების დაქოქვა
    time.sleep(2)
    print("Tukha Signal Bot is Active...")
    bot.infinity_polling(skip_pending=True)
