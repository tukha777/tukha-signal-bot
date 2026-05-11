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
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

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
        current_expiry = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        new_expiry = max(current_expiry, now) + timedelta(days=days)
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
    cursor.execute("INSERT OR REPLACE INTO users (user_id, selected_lang) VALUES (?, ?)", (user_id, lang))
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
        return datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') > datetime.now()
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
        'choose_pair': "📊 **Market Selection**\nChoose a pair:",
        'choose_time': "⏳ **Timeframe**\nPair: `{}`\nSelect expiry:",
        'scanning': "🔍 **Scanning Market Data...**",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nThe bot analyzes Forex and major Crypto pairs in real-time.\n\n💡 **Golden Rule:**\nTrust only signals with accuracy higher than 75%.",
        'vip_msg': "🎉 **VIP Activated!**\nYou have access for {} days. ✅ We wish you a successful trade!",
        'ref_text': "🎁 **Referral System**\n──────────────────\nInvite a friend and get **+7 Days VIP**!\n🔗 `https://t.me/{}?start={}`",
        'pair_label': "Asset", 'time_label': "Time", 'signal_label': "Signal", 'accuracy_label': "Strength", 'success': "✅ We wish you a successful trade!",
        'error': "❌ Error analyzing data. Try again later."
    },
    'ka': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨\n\nPlease select your language:",
        'main_msg': "💎 **მთავარი მენიუ**\n──────────────────\nაირჩიეთ სასურველი ღილაკი:",
        'lang_btn': "🌐 ენა", 'info_btn': "ℹ️ ინფორმაცია", 'start_btn': "🚀 სიგნალის დაწყება", 'ref_btn': "🎁 მეგობრები",
        'paywall': "🚫 **წვდომა შეზღუდულია!**\n──────────────────\nსაჭიროა VIP აქტივაცია.\n\n💰 **ფასი:** 30$ / თვეში\n📩 **კონტაქტი:** @TukhaTheGreat",
        'choose_pair': "📊 **წყვილების არჩევა**\nაირჩიეთ აქტივი:",
        'choose_time': "⏳ **დროის შერჩევა**\nწყვილი: `{}`\nაირჩიეთ ვადა:",
        'scanning': "🔍 **ბაზრის სკანირება...**",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nბოტი აანალიზებს ფორექსსა და მთავარ კრიპტო წყვილებს რეალურ დროში.\n\n💡 **ოქროს წესი:**\nენდეთ მხოლოდ იმ სიგნალებს, რომელთა სიზუსტე 75%-ზე მაღალია.",
        'vip_msg': "🎉 **VIP სტატუსი გააქტიურდა!**\nთქვენ გაქვთ წვდომა {} დღით. ✅ წარმატებულ ვაჭრობას გისურვებთ!",
        'ref_text': "🎁 **რეფერალური სისტემა**\n──────────────────\nმოიწვიე მეგობარი და მიიღე **+7 დღე VIP**!\n🔗 `https://t.me/{}?start={}`",
        'pair_label': "აქტივი", 'time_label': "ვადა", 'signal_label': "სიგნალი", 'accuracy_label': "სიზუსტე", 'success': "✅ წარმატებულ ვაჭრობას გისურვებთ!",
        'error': "❌ მონაცემების ანალიზისას მოხდა შეცდომა."
    },
    'ru': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨",
        'main_msg': "💎 **Главное меню**\n──────────────────",
        'lang_btn': "🌐 Язык", 'info_btn': "ℹ️ Инфо", 'start_btn': "🚀 Старт", 'ref_btn': "🎁 Рефералы",
        'paywall': "🚫 **Доступ закрыт!**\nНужна активация VIP.",
        'choose_pair': "📊 **Выбор пары**",
        'choose_time': "⏳ **Таймфрейм**\nПара: `{}`",
        'scanning': "🔍 **Анализ рынка...**",
        'vip_msg': "🎉 **VIP статус активирован!**\nУ вас есть доступ на {} дней. ✅ Желаем успешной торговли!",
        'pair_label': "Актив", 'time_label': "Таймфрейм", 'signal_label': "Сигнал", 'accuracy_label': "Точность", 'success': "✅ Желаем вам успешной торговли!",
        'error': "❌ Ошибка при анализе данных."
    },
    'es': { 'welcome': "✨ **Welcome to Tukha Signal Bot** ✨", 'main_msg': "💎 **Menú Principal**", 'lang_btn': "🌐 Idioma", 'info_btn': "ℹ️ Info", 'start_btn': "🚀 Señal", 'ref_btn': "🎁 Invitados", 'pair_label': "Activo", 'time_label': "Tiempo", 'signal_label': "Señal", 'accuracy_label': "Precisión", 'success': "✅ ¡Le deseamos una operación exitosa!", 'error': "❌ Error al analizar los datos." },
    'pt': { 'welcome': "✨ **Welcome to Tukha Signal Bot** ✨", 'main_msg': "💎 **Menu Principal**", 'lang_btn': "🌐 Idioma", 'info_btn': "ℹ️ Info", 'start_btn': "🚀 Sinal", 'ref_btn': "🎁 Convites", 'pair_label': "Ativo", 'time_label': "Tempo", 'signal_label': "Sinal", 'accuracy_label': "Precisão", 'success': "✅ Desejamos-lhe uma negociação de sucesso!", 'error': "❌ Erro ao analisar dados." },
    'tr': { 'welcome': "✨ **Welcome to Tukha Signal Bot** ✨", 'main_msg': "💎 **Ana Menü**", 'lang_btn': "🌐 Dil", 'info_btn': "ℹ️ Bilgi", 'start_btn': "🚀 Sinyal", 'ref_btn': "🎁 Davet", 'pair_label': "Varlık", 'time_label': "Zaman", 'signal_label': "Sinyal", 'accuracy_label': "Doğruluk", 'success': "✅ Başարılı bir ticaret dilerზ!", 'error': "❌ Veri analizi hatası." },
    'hi': { 'welcome': "✨ **Welcome to Tukha Signal Bot** ✨", 'main_msg': "💎 **मुख्य मेनू**", 'lang_btn': "🌐 भाषा", 'info_btn': "ℹ️ जानकारी", 'start_btn': "🚀 संकेत", 'ref_btn': "🎁 मित्रों", 'pair_label': "एसेट", 'time_label': "समय", 'signal_label': "संकेत", 'accuracy_label': "सटीकता", 'success': "✅ हम आपके सफल व्यापार की कामना करते हैं!", 'error': "❌ डेटा विश्लेषण में त्रुटि।" },
    'ar': { 'welcome': "✨ **Welcome to Tukha Signal Bot** ✨", 'main_msg': "💎 **القائمة الرئيسية**", 'lang_btn': "🌐 اللغة", 'info_btn': "ℹ️ معلومات", 'start_btn': "🚀 إشارة", 'ref_btn': "🎁 إحالات", 'pair_label': "الأصل", 'time_label': "الوقت", 'signal_label': "الإشارة", 'accuracy_label': "الدقة", 'success': "✅ نتمنى لك تجارة ناجحة!", 'error': "❌ خطأ في تحليل البيانات." }
}

def get_main_kbd(l):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row(STRINGS[l]['lang_btn'], STRINGS[l]['info_btn'])
    m.row(STRINGS[l]['start_btn'])
    m.row(STRINGS[l]['ref_btn'])
    return m

def get_lang_inline():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇺🇸 EN", callback_data="setlang_en"),
        types.InlineKeyboardButton("🇬🇪 KA", callback_data="setlang_ka"),
        types.InlineKeyboardButton("🇷🇺 RU", callback_data="setlang_ru"),
        types.InlineKeyboardButton("🇪🇸 ES", callback_data="setlang_es"),
        types.InlineKeyboardButton("🇧🇷 PT", callback_data="setlang_pt"),
        types.InlineKeyboardButton("🇹🇷 TR", callback_data="setlang_tr"),
        types.InlineKeyboardButton("🇮🇳 HI", callback_data="setlang_hi"),
        types.InlineKeyboardButton("🇸🇦 AR", callback_data="setlang_ar")
    )
    return markup

@bot.message_handler(commands=['addvip'])
def admin_add_vip(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        target_id, days = int(parts[1]), int(parts[2])
        add_vip_days(target_id, days)
        bot.reply_to(message, f"✅ User {target_id} activated.")
        u_lang = get_user_lang(target_id)
        bot.send_message(target_id, STRINGS[u_lang]['vip_msg'].format(days), parse_mode="Markdown")
    except: bot.reply_to(message, "❌ `/addvip ID DAYS`")

@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    bot.send_message(message.chat.id, STRINGS['en']['welcome'], reply_markup=get_lang_inline(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("setlang_"))
def callback_set_lang(call):
    lang = call.data.split("_")[1]
    update_user_lang(call.from_user.id, lang)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, STRINGS[lang]['main_msg'], reply_markup=get_main_kbd(lang), parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    uid = message.from_user.id
    l = get_user_lang(uid)
    if message.text == STRINGS[l]['start_btn']:
        if not is_vip(uid):
            bot.send_message(message.chat.id, STRINGS[l]['paywall'], parse_mode="Markdown")
            return
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(*(types.InlineKeyboardButton(f"💎 {p}", callback_data=f"pair_{p}") for p in PAIRS))
        bot.send_message(message.chat.id, STRINGS[l]['choose_pair'], reply_markup=markup, parse_mode="Markdown")
    elif message.text == STRINGS[l]['info_btn']:
        bot.send_message(message.chat.id, STRINGS[l]['info_text'], parse_mode="Markdown")
    elif message.text == STRINGS[l]['ref_btn']:
        bot.send_message(uid, STRINGS[l]['ref_text'].format(bot.get_me().username, uid), parse_mode="Markdown")
    elif message.text == STRINGS[l]['lang_btn']:
        bot.send_message(message.chat.id, "🌐 Choose Language:", reply_markup=get_lang_inline())

@bot.callback_query_handler(func=lambda c: c.data.startswith("pair_"))
def callback_pair(call):
    l = get_user_lang(call.from_user.id)
    pair = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(*(types.InlineKeyboardButton(f"⏱ {t}", callback_data=f"time_{pair}_{t}") for t in TIMES.keys()))
    bot.edit_message_text(STRINGS[l]['choose_time'].format(pair), call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

def get_analysis(pair, interval):
    try:
        is_crypto = "BTC" in pair
        screener = "crypto" if is_crypto else "forex"
        exchange = "BINANCE" if is_crypto else "OANDA"
        handler = TA_Handler(symbol=pair, screener=screener, exchange=exchange, interval=interval, timeout=10)
        analysis = handler.get_analysis()
        rec = analysis.summary['RECOMMENDATION']
        buy = analysis.summary['BUY']
        sell = analysis.summary['SELL']
        neutral = analysis.summary['NEUTRAL']
        acc = round(max(buy, sell) / (buy + sell + neutral) * 100, 1)
        return rec, acc
    except Exception as e:
        print(f"Analysis error: {e}")
        return None, None

@bot.callback_query_handler(func=lambda c: c.data.startswith("time_"))
def final_signal(call):
    uid = call.from_user.id
    l = get_user_lang(uid)
    pair, t_label = call.data.split("_")[1], call.data.split("_")[2]
    bot.edit_message_text(STRINGS[l]['scanning'], call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    rec, acc = get_analysis(pair, TIMES[t_label])
    
    if rec is None:
        bot.edit_message_text(STRINGS[l]['error'], call.message.chat.id, call.message.message_id)
        return

    icon = "🚀 STRONG BUY" if "STRONG_BUY" in rec else "📈 BUY" if "BUY" in rec else "🆘 STRONG SELL" if "STRONG_SELL" in rec else "📉 SELL" if "SELL" in rec else "⚖️ NEUTRAL"
    res = (f"🌟 **TUKHA SIGNAL LIVE** 🌟\n──────────────────\n"
           f"💎 {STRINGS[l]['pair_label']}: `{pair}`\n⏱ {STRINGS[l]['time_label']}: `{t_label}`\n"
           f"📊 {STRINGS[l]['signal_label']}: **{icon}**\n🎯 {STRINGS[l]['accuracy_label']}: `{acc}%`\n"
           f"──────────────────\n{STRINGS[l]['success']}")
    bot.edit_message_text(res, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(skip_pending=True)
