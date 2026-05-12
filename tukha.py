import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread
import os
import time
import sqlite3
from datetime import datetime, timedelta

# --- Flask Server ---
app = Flask('')
@app.route('/')
def home(): return "Tukha Signal is Running!"

def run():
    try:
        port = int(os.environ.get("PORT", 8080))
        app.run(host='0.0.0.0', port=port, use_reloader=False)
    except Exception as e: print(f"Flask error: {e}")

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()

# --- ბოტის მონაცემები ---
TOKEN = '8701731141:AAGaHtQjc49BY4_Kcu1ADsgywLEamb_Cdpk'
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 8696404791 

# --- მონაცემთა ბაზა ---
def init_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, expiry_date TEXT, selected_lang TEXT, referred_by INTEGER)''')
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
        except: new_expiry = now + timedelta(days=days)
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
        try: return datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') > datetime.now()
        except: return False
    return False

init_db()

# --- მონაცემები ---
PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY", "AUDUSD", "USDCAD", "BTCUSDT"]
TIMES = {"1 MIN": Interval.INTERVAL_1_MINUTE, "5 MIN": Interval.INTERVAL_5_MINUTES, 
         "15 MIN": Interval.INTERVAL_15_MINUTES, "30 MIN": Interval.INTERVAL_30_MINUTES}

STRINGS = {
    'en': {
        'main_msg': "💎 **Main Menu**", 'lang_btn': "🌐 Language", 'info_btn': "ℹ️ Information", 
        'start_btn': "🚀 Start Signal", 'ref_btn': "🎁 Invite Friends", 'calc_btn': "🧮 Risk Calc",
        'paywall': "🚫 **Access Denied!**\nActivation required.\n📩 @TukhaTheGreat",
        'ref_text': "🎁 **Referral System**\nInvite a friend and get **+7 Days VIP**!\n🔗 `https://t.me/{}?start={}`",
        'calc_text': "🧮 **Risk Calculator**\nSend: `Balance Risk% SL_Pips` \nExample: `1000 2 20`",
        'asset': "Asset", 'time': "Time", 'signal': "Signal", 'accuracy': "Accuracy", 'success': "✅ Trade safe!"
    },
    'ka': {
        'main_msg': "💎 **მთავარი მენიუ**", 'lang_btn': "🌐 ენა", 'info_btn': "ℹ️ ინფორმაცია", 
        'start_btn': "🚀 სიგნალის დაწყება", 'ref_btn': "🎁 მეგობრები", 'calc_btn': "🧮 კალკულატორი",
        'paywall': "🚫 **წვდომა შეზღუდულია!**\nსაჭიროა VIP აქტივაცია.\n📩 @TukhaTheGreat",
        'ref_text': "🎁 **რეფერალური სისტემა**\nმოიწვიე მეგობარი და მიიღე **+7 დღე VIP**!\n🔗 `https://t.me/{}?start={}`",
        'calc_text': "🧮 **რისკის კალკულატორი**\nმოგვწერეთ: `ბალანსი რისკი% SL_პიპსი` \nმაგალითად: `1000 2 20`",
        'asset': "აქტივი", 'time': "ვადა", 'signal': "სიგნალი", 'accuracy': "სიზუსტე", 'success': "✅ წარმატებულ ვაჭრობას გისურვებთ!"
    }
    # ... დანარჩენი ენები იგივე პრინციპით შეგიძლიათ დაამატოთ
}

@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    args = message.text.split()
    
    # რეფერალური ლოგიკა
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id != uid:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (uid,))
            if not cursor.fetchone(): # თუ ახალი მომხმარებელია
                add_vip_days(referrer_id, 7) # მომწვევს ემატება 7 დღე
                bot.send_message(referrer_id, f"🎁 თქვენ მიიღეთ +7 დღე VIP მეგობრის მოწვევისთვის!")
            conn.close()

    markup = types.InlineKeyboardMarkup(row_width=2)
    langs = [("🇺🇸 English", "en"), ("🇬🇪 ქართული", "ka"), ("🇷🇺 Русский", "ru")] # დაამატეთ სხვებიც
    markup.add(*[types.InlineKeyboardButton(name, callback_data=f"setlang_{code}") for name, code in langs])
    bot.send_message(message.chat.id, "✨ **Select Language / აირჩიეთ ენა** ✨", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("setlang_"))
def callback_set_lang(call):
    lang = call.data.split("_")[1]
    update_user_lang(call.from_user.id, lang)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, STRINGS.get(lang, STRINGS['en'])['main_msg'], reply_markup=get_main_kbd(lang), parse_mode="Markdown")

def get_main_kbd(l):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row(STRINGS[l]['lang_btn'], STRINGS[l]['info_btn'])
    m.row(STRINGS[l]['start_btn'], STRINGS[l]['calc_btn'])
    m.row(STRINGS[l]['ref_btn'])
    return m

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    l = get_user_lang(uid)
    txt = message.text
    
    # რისკის კალკულატორის ლოგიკა (ტექსტური შეყვანა)
    if len(txt.split()) == 3 and txt.replace(' ', '').isdigit():
        try:
            bal, risk_p, sl = map(float, txt.split())
            risk_amt = bal * (risk_p / 100)
            lot = round(risk_amt / (sl * 10), 2) # ფორმულა ფორექსისთვის
            res = f"🧮 **Result:**\nRisk Amount: `${risk_amt}`\nRecommended Lot: `{lot}`"
            bot.reply_to(message, res, parse_mode="Markdown")
            return
        except: pass

    if txt in [s.get('start_btn') for s in STRINGS.values()]:
        if not is_vip(uid):
            bot.send_message(message.chat.id, STRINGS[l]['paywall'], parse_mode="Markdown")
            return
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(*[types.InlineKeyboardButton(f"💎 {p}", callback_data=f"pair_{p}") for p in PAIRS])
        bot.send_message(message.chat.id, "📊 Market Selection:", reply_markup=markup)
    
    elif txt in [s.get('ref_btn') for s in STRINGS.values()]:
        bot.send_message(uid, STRINGS[l]['ref_text'].format(bot.get_me().username, uid), parse_mode="Markdown")

    elif txt in [s.get('calc_btn') for s in STRINGS.values()]:
        bot.send_message(uid, STRINGS[l]['calc_text'], parse_mode="Markdown")

    elif txt in [s.get('lang_btn') for s in STRINGS.values()]:
        start_cmd(message)

# --- დანარჩენი Callback-ები (pair_, time_ და ა.შ.) იგივე რჩება რაც გქონდათ ---
@bot.callback_query_handler(func=lambda c: c.data.startswith("pair_"))
def callback_pair(call):
    pair = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(*[types.InlineKeyboardButton(f"⏱ {t}", callback_data=f"time_{pair}_{t}") for t in TIMES.keys()])
    bot.edit_message_text(f"⏳ **Asset: {pair}**", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("time_"))
def final_signal(call):
    l = get_user_lang(call.from_user.id)
    pair, t_label = call.data.split("_")[1], call.data.split("_")[2]
    bot.edit_message_text("🔍 Scanning...", call.message.chat.id, call.message.message_id)
    try:
        handler = TA_Handler(symbol=pair, screener="crypto" if "BTC" in pair else "forex", exchange="BINANCE" if "BTC" in pair else "OANDA", interval=TIMES[t_label], timeout=10)
        analysis = handler.get_analysis()
        rec = analysis.summary['RECOMMENDATION']
        buy, sell, neut = analysis.summary['BUY'], analysis.summary['SELL'], analysis.summary['NEUTRAL']
        acc = round(max(buy, sell) / (buy + sell + neut) * 100, 1)
        icon = "🚀 STRONG BUY" if "STRONG_BUY" in rec else "📈 BUY" if "BUY" in rec else "🆘 STRONG SELL" if "STRONG_SELL" in rec else "📉 SELL" if "SELL" in rec else "⚖️ NEUTRAL"
        
        res = (f"🌟 **TUKHA SIGNAL LIVE** 🌟\n──────────────────\n"
               f"💎 {STRINGS[l]['asset']}: `{pair}`\n⏱️ {STRINGS[l]['time']}: `{t_label}`\n"
               f"📊 {STRINGS[l]['signal']}: **{icon}**\n🎯 {STRINGS[l]['accuracy']}: `{acc}%`\n"
               f"──────────────────\n{STRINGS[l]['success']}")
        bot.edit_message_text(res, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    except: bot.edit_message_text("❌ Error.", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling(skip_pending=True)
