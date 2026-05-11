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
        'main_msg': "💎 **Main Menu**\n──────────────────",
        'lang_btn': "🌐 Language", 'info_btn': "ℹ️ Information", 'start_btn': "🚀 Start Signal", 'ref_btn': "🎁 Invite Friends",
        'paywall': "🚫 **Access Denied!**\nActivation required.\n📩 @TukhaTheGreat",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\nReal-time market analysis.\n💡 Trust signals over 75%.",
        'ref_text': "🎁 **Referral**\nInvite friends and get +7 Days VIP!\n🔗 `https://t.me/{}?start={}`",
        'vip_msg': "🎉 **VIP Activated!** for {} days.", 'success': "✅ Good luck!"
    },
    'ka': {
        'main_msg': "💎 **მთავარი მენიუ**\n──────────────────",
        'lang_btn': "🌐 ენა", 'info_btn': "ℹ️ ინფორმაცია", 'start_btn': "🚀 სიგნალის დაწყება", 'ref_btn': "🎁 მეგობრები",
        'paywall': "🚫 **წვდომა შეზღუდულია!**\nსაჭიროა VIP.\n📩 @TukhaTheGreat",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\nბაზრის რეალური ანალიზი.\n💡 ენდეთ 75%-ზე მაღალ სიგნალს.",
        'ref_text': "🎁 **რეფერალი**\nმოიწვიე მეგობარი და მიიღე +7 დღე VIP!\n🔗 `https://t.me/{}?start={}`",
        'vip_msg': "🎉 **VIP გააქტიურდა!** {} დღით.", 'success': "✅ წარმატებები!"
    },
    'ru': { 'main_msg': "💎 **Главное меню**", 'lang_btn': "🌐 Язык", 'info_btn': "ℹ️ Инфо", 'start_btn': "🚀 Старт", 'ref_btn': "🎁 Рефералы", 'paywall': "🚫 Нужен VIP", 'info_text': "🤖 Анализ рынка v3.2", 'ref_text': "🎁 Реферал: https://t.me/{}?start={}", 'vip_msg': "🎉 VIP на {} дней.", 'success': "✅ Удачи!" },
    'es': { 'main_msg': "💎 **Menú**", 'lang_btn': "🌐 Idioma", 'info_btn': "ℹ️ Info", 'start_btn': "🚀 Señal", 'ref_btn': "🎁 Invitados", 'paywall': "🚫 VIP requerido", 'info_text': "🤖 Análisis v3.2", 'ref_text': "🎁 Enlace: https://t.me/{}?start={}", 'vip_msg': "🎉 VIP por {} días.", 'success': "✅ ¡Éxito!" },
    'pt': { 'main_msg': "💎 **Menu**", 'lang_btn': "🌐 Idioma", 'info_btn': "ℹ️ Info", 'start_btn': "🚀 Sinal", 'ref_btn': "🎁 Convites", 'paywall': "🚫 VIP necessário", 'info_text': "🤖 Análise v3.2", 'ref_text': "🎁 Convite: https://t.me/{}?start={}", 'vip_msg': "🎉 VIP por {} dias.", 'success': "✅ Sucesso!" },
    'tr': { 'main_msg': "💎 **Menü**", 'lang_btn': "🌐 Dil", 'info_btn': "ℹ️ Bilgi", 'start_btn': "🚀 Sinyal", 'ref_btn': "🎁 Davet", 'paywall': "🚫 VIP gerekli", 'info_text': "🤖 Analiz v3.2", 'ref_text': "🎁 Davet: https://t.me/{}?start={}", 'vip_msg': "🎉 VIP {} gün.", 'success': "✅ Başarılar!" },
    'hi': { 'main_msg': "💎 **मेन्यू**", 'lang_btn': "🌐 भाषा", 'info_btn': "ℹ️ जानकारी", 'start_btn': "🚀 संकेत", 'ref_btn': "🎁 मित्रों", 'paywall': "🚫 VIP आवश्यक", 'info_text': "🤖 विश्लेषण v3.2", 'ref_text': "🎁 लिंक: https://t.me/{}?start={}", 'vip_msg': "🎉 VIP {} दिन।", 'success': "✅ शुभकामनाएँ!" },
    'ar': { 'main_msg': "💎 **القائمة**", 'lang_btn': "🌐 اللغة", 'info_btn': "ℹ️ معلومات", 'start_btn': "🚀 إشارة", 'ref_btn': "🎁 إحالات", 'paywall': "🚫 مطلوب VIP", 'info_text': "🤖 تحليل v3.2", 'ref_text': "🎁 رابط: https://t.me/{}?start={}", 'vip_msg': "🎉 تم تفعيل VIP لمدة {} أيام.", 'success': "✅ بالتوفيق!" }
}

def get_admin_viplist():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, expiry_date FROM users")
    rows = cursor.fetchall()
    conn.close()
    now = datetime.now()
    active = [f"👤 `{r[0]}` | 📅 `{r[1]}`" for r in rows if r[1] and datetime.strptime(r[1], '%Y-%m-%d %H:%M:%S') > now]
    return "💎 **Active VIPs:**\n" + "\n".join(active) if active else "ℹ️ Empty."

@bot.message_handler(commands=['addvip'])
def admin_add_vip(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        target_id, days = int(parts[1]), int(parts[2])
        add_vip_days(target_id, days)
        bot.reply_to(message, f"✅ Activated.")
        u_lang = get_user_lang(target_id)
        bot.send_message(target_id, STRINGS.get(u_lang, STRINGS['en'])['vip_msg'].format(days), parse_mode="Markdown")
    except: bot.reply_to(message, "❌ `/addvip ID DAYS`")

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
    bot.send_message(message.chat.id, "✨ **Select Language** ✨", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("setlang_"))
def callback_set_lang(call):
    lang = call.data.split("_")[1]
    update_user_lang(call.from_user.id, lang)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, STRINGS[lang]['main_msg'], reply_markup=get_main_kbd(lang), parse_mode="Markdown")

def get_main_kbd(l):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row(STRINGS[l]['lang_btn'], STRINGS[l]['info_btn'])
    m.row(STRINGS[l]['start_btn'])
    m.row(STRINGS[l]['ref_btn'])
    return m

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    l = get_user_lang(uid)
    txt = message.text
    
    # ვამოწმებთ რომელი ღილაკი დააჭირა ყველა ენაზე
    all_starts = [s['start_btn'] for s in STRINGS.values()]
    all_infos = [s['info_btn'] for s in STRINGS.values()]
    all_refs = [s['ref_btn'] for s in STRINGS.values()]
    all_langs = [s['lang_btn'] for s in STRINGS.values()]

    if txt in all_starts:
        if not is_vip(uid):
            bot.send_message(message.chat.id, STRINGS[l]['paywall'], parse_mode="Markdown")
            return
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(*[types.InlineKeyboardButton(f"💎 {p}", callback_data=f"pair_{p}") for p in PAIRS])
        if uid == ADMIN_ID:
            markup.row(types.InlineKeyboardButton("📋 VIP List", callback_data="admin_list"), types.InlineKeyboardButton("➕ Add Help", callback_data="admin_help"))
        bot.send_message(message.chat.id, "📊 Selection:", reply_markup=markup)
    
    elif txt in all_infos:
        bot.send_message(message.chat.id, STRINGS[l]['info_text'], parse_mode="Markdown")
        
    elif txt in all_refs:
        bot.send_message(uid, STRINGS[l]['ref_text'].format(bot.get_me().username, uid), parse_mode="Markdown")
        
    elif txt in all_langs:
        start_cmd(message)

@bot.callback_query_handler(func=lambda c: c.data in ["admin_list", "admin_help"])
def admin_callbacks(call):
    if call.data == "admin_list": bot.send_message(call.message.chat.id, get_admin_viplist(), parse_mode="Markdown")
    else: bot.send_message(call.message.chat.id, "💡 `/addvip ID DAYS`", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("pair_"))
def callback_pair(call):
    pair = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(*[types.InlineKeyboardButton(f"⏱ {t}", callback_data=f"time_{pair}_{t}") for t in TIMES.keys()])
    bot.edit_message_text(f"⏳ {pair}", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("time_"))
def final_signal(call):
    l = get_user_lang(call.from_user.id)
    pair, t_label = call.data.split("_")[1], call.data.split("_")[2]
    bot.edit_message_text("🔍 Scanning...", call.message.chat.id, call.message.message_id)
    try:
        handler = TA_Handler(symbol=pair, screener="crypto" if "BTC" in pair else "forex", exchange="BINANCE" if "BTC" in pair else "OANDA", interval=TIMES[t_label], timeout=10)
        analysis = handler.get_analysis()
        rec, buy, sell, neut = analysis.summary['RECOMMENDATION'], analysis.summary['BUY'], analysis.summary['SELL'], analysis.summary['NEUTRAL']
        acc = round(max(buy, sell) / (buy + sell + neut) * 100, 1)
        icon = "🚀 STRONG BUY" if "STRONG_BUY" in rec else "📈 BUY" if "BUY" in rec else "🆘 STRONG SELL" if "STRONG_SELL" in rec else "📉 SELL" if "SELL" in rec else "⚖️ NEUTRAL"
        bot.edit_message_text(f"🌟 **{pair}** | {t_label}\n📊 {icon}\n🎯 Accuracy: {acc}%\n{STRINGS[l]['success']}", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    except: bot.edit_message_text("❌ Error", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    init_db()
    keep_alive()
    time.sleep(2)
    print("Tukha Signal Bot is Active...")
    bot.infinity_polling(skip_pending=True)
