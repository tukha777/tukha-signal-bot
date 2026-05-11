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

# 🛑 შენი ID
ADMIN_ID = 8696404791 

# --- მონაცემთა ბაზა (SQLite) ---
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, expiry_date TEXT)''')
    conn.commit()
    conn.close()

def add_vip_days(user_id, days):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT expiry_date FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    now = datetime.now()
    if row and row[0]:
        current_expiry = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        new_expiry = max(current_expiry, now) + timedelta(days=days)
    else:
        new_expiry = now + timedelta(days=days)
    cursor.execute("INSERT OR REPLACE INTO users (user_id, expiry_date) VALUES (?, ?)", 
                   (user_id, new_expiry.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    return new_expiry

def is_vip(user_id):
    if user_id == ADMIN_ID: return True
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT expiry_date FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        return datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') > datetime.now()
    return False

init_db()

# --- მონაცემები ---
user_lang = {}
PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY", "AUDUSD", "USDCAD", "BTCUSDT"]
TIMES = {"1 MIN": Interval.INTERVAL_1_MINUTE, "5 MIN": Interval.INTERVAL_5_MINUTES, 
         "15 MIN": Interval.INTERVAL_15_MINUTES, "30 MIN": Interval.INTERVAL_30_MINUTES}

STRINGS = {
    'en': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨\n\nPlease select your language:",
        'main_msg': "💎 **Main Menu**\n──────────────────\nChoose an option:",
        'lang_btn': "🌐 Language", 'info_btn': "ℹ️ Information", 'start_btn': "🚀 Start Signal", 'ref_btn': "🎁 Invite Friends",
        'paywall': "🚫 **Access Denied!**\n──────────────────\nActivation is required.\n\n💰 **Price:** $30 / Month\n📩 **Contact:** @TukhaTheGreat",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nThe bot analyzes Forex and major Crypto pairs.\n💡 **Rule:** Accuracy > 75%.",
        'ref_text': "🎁 **Invite Friend = +7 Days VIP!**\n🔗 `https://t.me/{}?start={}`",
        'vip_success': "🎉 **VIP Activated!**\nYou have access for {} days. Good luck!",
        'success': "✅ We wish you a successful trade!"
    },
    'ka': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨\n\nPlease select your language:",
        'main_msg': "💎 **მთავარი მენიუ**\n──────────────────\nაირჩიეთ სასურველი ღილაკი:",
        'lang_btn': "🌐 ენა", 'info_btn': "ℹ️ ინფორმაცია", 'start_btn': "🚀 სიგნალის დაწყება", 'ref_btn': "🎁 მეგობრები",
        'paywall': "🚫 **წვდომა შეზღუდულია!**\n──────────────────\nსაჭიროა VIP აქტივაცია.\n\n💰 **ფასი:** 30$ / თვეში\n📩 **კონტაქტი:** @TukhaTheGreat",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n💡 ენდეთ მხოლოდ სიგნალებს > 75% სიზუსტით.",
        'ref_text': "🎁 **მოიწვიე მეგობარი და მიიღე +7 დღე VIP!**\n🔗 `https://t.me/{}?start={}`",
        'vip_success': "🎉 **VIP სტატუსი გააქტიურდა!**\nთქვენ გაქვთ წვდომა {} დღით. წარმატებულ ვაჭრობას გისურვებთ!",
        'success': "✅ წარმატებულ ვაჭრობას გისურვებთ!"
    },
    'ru': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨\n\nPlease select your language:",
        'main_msg': "💎 **Главное меню**",
        'lang_btn': "🌐 Язык", 'info_btn': "ℹ️ Инфо", 'start_btn': "🚀 Старт", 'ref_btn': "🎁 Рефералы",
        'paywall': "🚫 **Доступ закрыт!**\nНужна активация VIP.",
        'vip_success': "🎉 **VIP статус активирован!**\nУ вас есть доступ на {} дней. Желаем успешной торговли!",
        'success': "✅ Желаем вам успешной торговли!"
    },
    'es': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨",
        'main_msg': "💎 **Menú Principal**",
        'lang_btn': "🌐 Idioma", 'info_btn': "ℹ️ Info", 'start_btn': "🚀 Señal", 'ref_btn': "🎁 Invitados",
        'vip_success': "🎉 **¡VIP activado!**\nTienes acceso por {} días. ¡Buena suerte!",
        'success': "✅ ¡Le deseamos una operación exitosa!"
    },
    'pt': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨",
        'main_msg': "💎 **Menu Principal**",
        'lang_btn': "🌐 Idioma", 'info_btn': "ℹ️ Info", 'start_btn': "🚀 Sinal", 'ref_btn': "🎁 Convites",
        'vip_success': "🎉 **VIP Ativado!**\nVocê tem acesso por {} dias. Boa sorte!",
        'success': "✅ Desejamos-lhe uma negociação de sucesso!"
    },
    'tr': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨",
        'main_msg': "💎 **Ana Menü**",
        'lang_btn': "🌐 Dil", 'info_btn': "ℹ️ Bilgi", 'start_btn': "🚀 Sinyal", 'ref_btn': "🎁 Davet",
        'vip_success': "🎉 **VIP Aktif Edildi!**\n{} günlük erişiminiz var. Bol kazançlar!",
        'success': "✅ Başarılı bir ticaret dileriz!"
    },
    'hi': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨",
        'main_msg': "💎 **मुख्य मेनू**",
        'lang_btn': "🌐 भाषा", 'info_btn': "ℹ️ जानकारी", 'start_btn': "🚀 संकेत", 'ref_btn': "🎁 मित्रों",
        'vip_success': "🎉 **VIP सक्रिय हो गया!**\nआपके पास {} दिनों के लिए पहुंच है। शुभकामनाएँ!",
        'success': "✅ हम आपके सफल व्यापार की कामना करते हैं!"
    },
    'ar': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨",
        'main_msg': "💎 **القائمة الرئيسية**",
        'lang_btn': "🌐 اللغة", 'info_btn': "ℹ️ معلومات", 'start_btn': "🚀 إشارة", 'ref_btn': "🎁 إحالات",
        'vip_success': "🎉 **تم تفعيل VIP!**\nلديك صلاحية لمدة {} يومًا. بالتوفيق!",
        'success': "✅ نتمنى لك تجارة ناجحة!"
    }
}

# --- ადმინ ბრძანება ---
@bot.message_handler(commands=['addvip'])
def admin_add_vip(message):
    uid = message.from_user.id
    if uid != ADMIN_ID: return
    try:
        parts = message.text.split()
        target_id, days = int(parts[1]), int(parts[2])
        expiry = add_vip_days(target_id, days)
        
        # ადმინს ყოველთვის ქართულად უპასუხოს
        bot.reply_to(message, f"✅ მომხმარებელი `{target_id}` გააქტიურდა `{expiry}`-მდე", parse_mode="Markdown")
        
        # იუზერს გაუგზავნოს თავის ენაზე
        target_lang = user_lang.get(target_id, 'en')
        bot.send_message(target_id, STRINGS[target_lang]['vip_success'].format(days), parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Format: `/addvip ID DAYS`")

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        inviter = int(args[1])
        if inviter != uid:
            add_vip_days(inviter, 7)
            bot.send_message(inviter, "🎁 **Bonus!** Someone joined via your link. You got **+7 Days VIP**!")
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    langs = [types.InlineKeyboardButton(f"{k.upper()}", callback_data=f"setlang_{k}") for k in STRINGS.keys()]
    markup.add(*langs)
    bot.send_message(message.chat.id, STRINGS['en']['welcome'], reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("setlang_"))
def set_lang(call):
    lang = call.data.split("_")[1]
    user_lang[call.from_user.id] = lang
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, STRINGS[lang]['main_msg'], 
                     reply_markup=get_main_kbd(lang), parse_mode="Markdown")

def get_main_kbd(l):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row(STRINGS[l]['lang_btn'], STRINGS[l]['info_btn'])
    m.row(STRINGS[l]['start_btn'])
    m.row(STRINGS[l]['ref_btn'])
    return m

# ... (დანარჩენი კოდი - სიგნალები და ანალიზი - უცვლელია) ...

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['start_btn'] for l in STRINGS))
def pair_menu(message):
    uid = message.from_user.id
    l = user_lang.get(uid, 'en')
    if not is_vip(uid):
        bot.send_message(message.chat.id, STRINGS[l]['paywall'], parse_mode="Markdown")
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(*(types.InlineKeyboardButton(f"💎 {p}", callback_data=f"pair_{p}") for p in PAIRS))
    bot.send_message(message.chat.id, "📊 Select Asset:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("pair_"))
def timeframe_menu(call):
    l = user_lang.get(call.from_user.id, 'en')
    pair = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(*(types.InlineKeyboardButton(f"⏱ {t}", callback_data=f"time_{pair}_{t}") for t in TIMES.keys()))
    bot.edit_message_text(f"⏳ Pair: {pair}\nSelect timeframe:", call.message.chat.id, call.message.message_id, reply_markup=markup)

def get_analysis(pair, interval):
    try:
        is_crypto = "USDT" in pair or "BTC" in pair
        exchange = "BINANCE" if is_crypto else "OANDA"
        analysis = TA_Handler(symbol=pair, screener="crypto" if is_crypto else "forex", 
                              exchange=exchange, interval=interval, timeout=10).get_analysis()
        summary = analysis.summary['RECOMMENDATION']
        buy, sell, neutral = analysis.summary['BUY'], analysis.summary['SELL'], analysis.summary['NEUTRAL']
        accuracy = max(buy, sell) / (buy + sell + neutral) * 100 if (buy+sell+neutral) > 0 else 0
        return summary, round(accuracy, 1)
    except: return "NEUTRAL", 0

@bot.callback_query_handler(func=lambda c: c.data.startswith("time_"))
def final_signal(call):
    l = user_lang.get(call.from_user.id, 'en')
    pair, t_label = call.data.split("_")[1], call.data.split("_")[2]
    bot.edit_message_text("🔍 Scanning...", call.message.chat.id, call.message.message_id)
    rec, acc = get_analysis(pair, TIMES[t_label])
    icon = "🚀 STRONG BUY" if "STRONG_BUY" in rec else "📈 BUY" if "BUY" in rec else "🆘 STRONG SELL" if "STRONG_SELL" in rec else "📉 SELL" if "SELL" in rec else "⚖️ NEUTRAL"
    res = (f"🌟 **TUKHA SIGNAL LIVE** 🌟\n──────────────────\n"
           f"💎 Asset: `{pair}`\n⏱ Time: `{t_label}`\n"
           f"📊 Signal: **{icon}**\n🎯 Accuracy: `{acc}%`\n"
           f"──────────────────\n{STRINGS[l]['success']}")
    bot.edit_message_text(res, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

if __name__ == "__main__":
    keep_alive()
    try: bot.remove_webhook()
    except: pass
    time.sleep(1)
    print("Tukha Signal ბოტი ჩაირთვა...")
    bot.polling(none_stop=True)
