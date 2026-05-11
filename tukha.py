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
    # Flask-ის გაშვება ცალკე ნაკადად (Thread)
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
                      (user_id INTEGER PRIMARY KEY, expiry_date TEXT, selected_lang TEXT)''')
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
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨\n\nPlease select your language:",
        'main_msg': "💎 **Main Menu**\n──────────────────\nChoose an option:",
        'lang_btn': "🌐 Language", 'info_btn': "ℹ️ Information", 'start_btn': "🚀 Start Signal", 'ref_btn': "🎁 Invite Friends",
        'paywall': "🚫 **Access Denied!**\n──────────────────\nActivation is required.\n\n💰 **Price:** $30 / Month\n📩 **Contact:** @TukhaTheGreat",
        'scanning': "🔍 **Scanning Market Data...**",
        'vip_msg': "🎉 **VIP Activated!**\nYou have access for {} days. ✅ We wish you a successful trade!",
        'success': "✅ We wish you a successful trade!"
    },
    'ka': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨\n\nPlease select your language:",
        'main_msg': "💎 **მთავარი მენიუ**\n──────────────────\nაირჩიეთ სასურველი ღილაკი:",
        'lang_btn': "🌐 ენა", 'info_btn': "ℹ️ ინფორმაცია", 'start_btn': "🚀 სიგნალის დაწყება", 'ref_btn': "🎁 მეგობრები",
        'paywall': "🚫 **წვდომა შეზღუდულია!**\n──────────────────\nსაჭიროა VIP აქტივაცია.\n\n💰 **ფასი:** 30$ / თვეში\n📩 **კონტაქტი:** @TukhaTheGreat",
        'scanning': "🔍 **ბაზრის სკანირება...**",
        'vip_msg': "🎉 **VIP სტატუსი გააქტიურდა!**\nთქვენ გაქვთ წვდომა {} დღით. ✅ წარმატებულ ვაჭრობას გისურვებთ!",
        'success': "✅ წარმატებულ ვაჭრობას გისურვებთ!"
    }
}

# --- ადმინ ფუნქცია ---
def get_admin_viplist():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, expiry_date FROM users")
    rows = cursor.fetchall()
    conn.close()
    now = datetime.now()
    active_vips = []
    for r in rows:
        try:
            if datetime.strptime(r[1], '%Y-%m-%d %H:%M:%S') > now:
                active_vips.append(f"👤 `{r[0]}` | 📅 `{r[1]}`")
        except: continue
    if not active_vips: return "ℹ️ VIP list is empty."
    return "💎 **Active VIP Users:**\n──────────────────\n" + "\n".join(active_vips)

# --- HANDLERS ---
@bot.message_handler(commands=['addvip'])
def admin_add_vip(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        target_id, days = int(parts[1]), int(parts[2])
        add_vip_days(target_id, days)
        bot.reply_to(message, f"✅ User {target_id} activated for {days} days.")
        u_lang = get_user_lang(target_id)
        bot.send_message(target_id, STRINGS.get(u_lang, STRINGS['en'])['vip_msg'].format(days), parse_mode="Markdown")
    except: bot.reply_to(message, "❌ Use: `/addvip ID DAYS`")

@bot.message_handler(commands=['start'])
def start_cmd(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇺🇸 English", callback_data="setlang_en"),
        types.InlineKeyboardButton("🇬🇪 ქართული", callback_data="setlang_ka"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="setlang_ru"),
        types.InlineKeyboardButton("🇪🇸 Español", callback_data="setlang_es"),
        types.InlineKeyboardButton("🇧🇷 Português", callback_data="setlang_pt"),
        types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data="setlang_tr"),
        types.InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="setlang_hi"),
        types.InlineKeyboardButton("🇸🇦 العربية", callback_data="setlang_ar")
    )
    bot.send_message(message.chat.id, "✨ **Welcome to Tukha Signal Bot** ✨\n\nPlease select your language:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("setlang_"))
def callback_set_lang(call):
    lang = call.data.split("_")[1]
    update_user_lang(call.from_user.id, lang)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    l_str = STRINGS.get(lang, STRINGS['en'])
    bot.send_message(call.message.chat.id, l_str['main_msg'], reply_markup=get_main_kbd(lang), parse_mode="Markdown")

def get_main_kbd(l):
    l_str = STRINGS.get(l, STRINGS['ka'])
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row(l_str.get('lang_btn', "🌐 Language"), l_str.get('info_btn', "ℹ️ Info"))
    m.row(l_str.get('start_btn', "🚀 Start Signal"))
    m.row(l_str.get('ref_btn', "🎁 Invite"))
    return m

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    l = get_user_lang(uid)
    l_str = STRINGS.get(l, STRINGS['en'])
    
    if message.text in ["🚀 Start Signal", "🚀 სიგნალის დაწყება"]:
        if not is_vip(uid):
            bot.send_message(message.chat.id, l_str['paywall'], parse_mode="Markdown")
            return
        markup = types.InlineKeyboardMarkup(row_width=2)
        btns = [types.InlineKeyboardButton(f"💎 {p}", callback_data=f"pair_{p}") for p in PAIRS]
        markup.add(*btns)
        if uid == ADMIN_ID:
            markup.row(types.InlineKeyboardButton("➕ Add VIP (How-to)", callback_data="admin_help"),
                       types.InlineKeyboardButton("📋 VIP List", callback_data="admin_list"))
        bot.send_message(message.chat.id, "📊 **Market Selection**", reply_markup=markup, parse_mode="Markdown")
    
    elif message.text in ["🌐 Language", "🌐 ენა"]:
        start_cmd(message)

@bot.callback_query_handler(func=lambda c: c.data == "admin_list")
def callback_admin_list(call):
    bot.send_message(call.message.chat.id, get_admin_viplist(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data == "admin_help")
def callback_admin_help(call):
    bot.send_message(call.message.chat.id, "💡 **How to add VIP:**\nWrite: `/addvip ID DAYS` \nExample: `/addvip 12345678 30`", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("pair_"))
def callback_pair(call):
    pair = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(*(types.InlineKeyboardButton(f"⏱ {t}", callback_data=f"time_{pair}_{t}") for t in TIMES.keys()))
    bot.edit_message_text(f"⏳ **Asset: {pair}**\nSelect timeframe:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("time_"))
def final_signal(call):
    uid = call.from_user.id
    l = get_user_lang(uid)
    pair, t_label = call.data.split("_")[1], call.data.split("_")[2]
    bot.edit_message_text("🔍 **Scanning Market Data...**", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    try:
        is_crypto = "BTC" in pair
        handler = TA_Handler(symbol=pair, screener="crypto" if is_crypto else "forex", exchange="BINANCE" if is_crypto else "OANDA", interval=TIMES[t_label], timeout=10)
        analysis = handler.get_analysis()
        rec = analysis.summary['RECOMMENDATION']
        buy, sell, neut = analysis.summary['BUY'], analysis.summary['SELL'], analysis.summary['NEUTRAL']
        acc = round(max(buy, sell) / (buy + sell + neut) * 100, 1)
        icon = "🚀 STRONG BUY" if "STRONG_BUY" in rec else "📈 BUY" if "BUY" in rec else "🆘 STRONG SELL" if "STRONG_SELL" in rec else "📉 SELL" if "SELL" in rec else "⚖️ NEUTRAL"
        res = (f"🌟 **TUKHA SIGNAL LIVE** 🌟\n──────────────────\n"
               f"💎 Asset: `{pair}`\n⏱ Time: `{t_label}`\n"
               f"📊 Signal: **{icon}**\n🎯 Accuracy: `{acc}%`\n"
               f"──────────────────\n{STRINGS.get(l, STRINGS['en'])['success']}")
        bot.edit_message_text(res, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    except:
        bot.edit_message_text("❌ Analysis Error. Market may be closed.", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    init_db()
    keep_alive() 
    time.sleep(2) 
    print("Tukha Signal Bot is Active...") 
    bot.infinity_polling(skip_pending=True)
