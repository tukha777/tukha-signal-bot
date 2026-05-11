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
        'choose_pair': "📊 **Market Selection**\nChoose a pair:",
        'choose_time': "⏳ **Timeframe**\nPair: `{}`\nSelect expiry:",
        'scanning': "🔍 **Scanning Market Data...**",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nThe bot analyzes Forex and major Crypto pairs in real-time.\n\n💡 **Golden Rule:**\nTrust only signals with accuracy higher than 75%.\n\n⚠️ **Forex does not work on weekends!**",
        'ref_text': "🎁 **Referral System**\n──────────────────\nInvite a friend and get **+7 Days VIP** automatically!\n\n🔗 Your link:\n`https://t.me/{}?start={}`",
        'pair_label': "Asset", 'time_label': "Time", 'signal_label': "Signal", 'accuracy_label': "Strength", 'success': "✅ We wish you a successful trade!"
    },
    'ka': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨\n\nPlease select your language:",
        'main_msg': "💎 **მთავარი მენიუ**\n──────────────────\nაირჩიეთ სასურველი ღილაკი:",
        'lang_btn': "🌐 ენა", 'info_btn': "ℹ️ ინფორმაცია", 'start_btn': "🚀 სიგნალის დაწყება", 'ref_btn': "🎁 მეგობრები",
        'paywall': "🚫 **წვდომა შეზღუდულია!**\n──────────────────\nსაჭიროა VIP აქტივაცია.\n\n💰 **ფასი:** 30$ / თვეში\n📩 **კონტაქტი:** @TukhaTheGreat",
        'choose_pair': "📊 **წყვილების არჩევა**\nაირჩიეთ აქტივი:",
        'choose_time': "⏳ **დროის შერჩევა**\nწყვილი: `{}`\nაირჩიეთ ვადა:",
        'scanning': "🔍 **ბაზრის სკანირება...**",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nბოტი აანალიზებს ფორექსსა და მთავარ კრიპტო წყვილებს რეალურ დროში.\n\n💡 **ოქროს წესი:**\nენდეთ მხოლოდ იმ სიგნალებს, რომელთა სიზუსტე 75%-ზე მაღალია.\n\n⚠️ **ფორექსი არ მუშაობს შაბათ-კვირას!**",
        'ref_text': "🎁 **რეფერალური სისტემა**\n──────────────────\nმოიწვიე მეგობარი და მიიღე **+7 დღე VIP** საჩუქრად!\n\n🔗 შენი ლინკი:\n`https://t.me/{}?start={}`",
        'pair_label': "აქტივი", 'time_label': "ვადა", 'signal_label': "სიგნალი", 'accuracy_label': "სიზუსტე", 'success': "✅ წარმატებულ ვაჭრობას გისურვებთ!"
    },
    'ru': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨\n\nPlease select your language:",
        'main_msg': "💎 **Главное меню**\n──────────────────\nВыберите опцию:",
        'lang_btn': "🌐 Язык", 'info_btn': "ℹ️ Инфо", 'start_btn': "🚀 Старт", 'ref_btn': "🎁 Рефералы",
        'paywall': "🚫 **Доступ закрыт!**\n──────────────────\nНужна активация VIP.\n💰 **Цена:** $30 / Месяц\n📩 **Контакт:** @TukhaTheGreat",
        'choose_pair': "📊 **Выбор пары**\nВыберите актив:",
        'choose_time': "⏳ **Таймфрейм**\nПара: `{}`\nВыберите время:",
        'scanning': "🔍 **Анализ рынка...**",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nБот анализирует Форекс и Крипто в реальном времени.\n💡 **Золотое правило:** Доверяйте сигналам выше 75%.\n⚠️ Форекс не работает на выходных!",
        'ref_text': "🎁 **Реферальная система**\n──────────────────\nПригласи друга и получи **+7 дней VIP**!\n🔗 Ссылка:\n`https://t.me/{}?start={}`",
        'pair_label': "Актив", 'time_label': "Время", 'signal_label': "Сигнал", 'accuracy_label': "Точность", 'success': "✅ Желаем вам успешной торговли!"
    },
    'es': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨\n\nPlease select your language:",
        'main_msg': "💎 **Menú Principal**\n──────────────────",
        'lang_btn': "🌐 Idioma", 'info_btn': "ℹ️ Información", 'start_btn': "🚀 Iniciar Señal", 'ref_btn': "🎁 Invitados",
        'paywall': "🚫 **Acceso Denegado!**\nPrecio: $30 / Mes\n@TukhaTheGreat",
        'choose_pair': "📊 **Seleccionar Par**", 'choose_time': "⏳ **Tiempo**\nPar: `{}`", 'scanning': "🔍 **Analizando...**",
        'info_text': "🤖 **v3.2**\n💡 Regla de Oro: Precisión > 75%.",
        'ref_text': "🎁 ¡Invita a un amigo y obtén **+7 días VIP**!\n🔗 `https://t.me/{}?start={}`",
        'pair_label': "Activo", 'time_label': "Tiempo", 'signal_label': "Señal", 'accuracy_label': "Precisión", 'success': "✅ ¡Le deseamos una operación exitosa!"
    },
    'pt': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨\n\nPlease select your language:",
        'main_msg': "💎 **Menu Principal**\n──────────────────",
        'lang_btn': "🌐 Idioma", 'info_btn': "ℹ️ Info", 'start_btn': "🚀 Iniciar Sinal", 'ref_btn': "🎁 Convites",
        'paywall': "🚫 **Acesso Negado!**\nPreço: $30 / Mês\n@TukhaTheGreat",
        'choose_pair': "📊 **Selecionar Par**", 'choose_time': "⏳ **Tempo**\nPar: `{}`", 'scanning': "🔍 **Analisando...**",
        'info_text': "🤖 **v3.2**\n💡 Regra de Ouro: Precisão > 75%.",
        'ref_text': "🎁 Convide um amigo e ganhe **+7 dias VIP**!\n🔗 `https://t.me/{}?start={}`",
        'pair_label': "Ativo", 'time_label': "Tempo", 'signal_label': "Sinal", 'accuracy_label': "Precisão", 'success': "✅ Desejamos-lhe uma negociação de sucesso!"
    },
    'tr': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨\n\nPlease select your language:",
        'main_msg': "💎 **Ana Menü**\n──────────────────",
        'lang_btn': "🌐 Dil", 'info_btn': "ℹ️ Bilgi", 'start_btn': "🚀 Sinyal", 'ref_btn': "🎁 Davet",
        'paywall': "🚫 **Erişim Engellendi!**\nÜcret: $30 / Ay\n@TukhaTheGreat",
        'choose_pair': "📊 **Parite Seç**", 'choose_time': "⏳ **Zaman Dilimi**\nParite: `{}`", 'scanning': "🔍 **Taranıyor...**",
        'info_text': "🤖 **v3.2**\n💡 Altın Kural: Doğruluk > %75.",
        'ref_text': "🎁 Bir arkadaşını davet et ve **+7 gün VIP** kazan!\n🔗 `https://t.me/{}?start={}`",
        'pair_label': "Varlık", 'time_label': "Zამან", 'signal_label': "Sinyal", 'accuracy_label': "Doğruluk", 'success': "✅ Başarılı bir ticaret dilerზ!"
    },
    'hi': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨\n\nPlease select your language:",
        'main_msg': "💎 **मुख्य मेनू**\n──────────────────",
        'lang_btn': "🌐 भाषा", 'info_btn': "ℹ️ जानकारी", 'start_btn': "🚀 संकेत शुरू करें", 'ref_btn': "🎁 मित्रों को बुलाएं",
        'paywall': "🚫 **पहुंच वर्जित!**\nकीमत: $30 / महीना\n@TukhaTheGreat",
        'choose_pair': "📊 **जोड़ी चुनें**", 'choose_time': "⏳ **समय सीमा**\nजोड़ी: `{}`", 'scanning': "🔍 **स्कैनिंग...**",
        'info_text': "🤖 **v3.2**\n💡 सुनहरा नियम: सटीकता > 75%.",
        'ref_text': "🎁 मित्र को आमंत्रित करें और **+7 दिन VIP** प्राप्त करें!\n🔗 `https://t.me/{}?start={}`",
        'pair_label': "एसेट", 'time_label': "समय", 'signal_label': "संकेत", 'accuracy_label': "सटीकता", 'success': "✅ हम आपके सफल व्यापार की कामना करते हैं!"
    },
    'ar': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨\n\nPlease select your language:",
        'main_msg': "💎 **القائمة الرئيسية**\n──────────────────",
        'lang_btn': "🌐 اللغة", 'info_btn': "ℹ️ معلومات", 'start_btn': "🚀 ابدأ الإشارة", 'ref_btn': "🎁 الإحالات",
        'paywall': "🚫 **تم رفض الوصول!**\nالسعر: 30 دولار شهرياً\n@TukhaTheGreat",
        'choose_pair': "📊 **اختر الزوج**", 'choose_time': "⏳ **الإطار الزمني**\nالزوج: `{}`", 'scanning': "🔍 **جاري الفحص...**",
        'info_text': "🤖 **v3.2**\n💡 القاعدة الذهبية: الدقة > 75%.",
        'ref_text': "🎁 ادعُ صديقاً واحصل على **+7 أيام مجانية**!\n🔗 `https://t.me/{}?start={}`",
        'pair_label': "الأصل", 'time_label': "الوقت", 'signal_label': "الإشارة", 'accuracy_label': "الدقة", 'success': "✅ نتمنى لك تجارة ناجحة!"
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
        
        # შეტყობინება ადმინს (ქართულად)
        bot.reply_to(message, f"✅ მომხმარებელი `{target_id}` გააქტიურდა `{expiry}`-მდე", parse_mode="Markdown")
        
        # შეტყობინება იუზერს (ქართულად და რუსულად)
        msg_to_user = (f"🎉 **VIP სტატუსი გააქტიურდა!**\nთქვენ გაქვთ წვდომა {days} დღით.\n\n"
                       f"🎉 **VIP статус активирован!**\nУ вас есть доступ на {days} дней.")
        bot.send_message(target_id, msg_to_user, parse_mode="Markdown")
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
    langs = [
        types.InlineKeyboardButton("🇺🇸 EN", callback_data="setlang_en"),
        types.InlineKeyboardButton("🇬🇪 KA", callback_data="setlang_ka"),
        types.InlineKeyboardButton("🇷🇺 RU", callback_data="setlang_ru"),
        types.InlineKeyboardButton("🇪🇸 ES", callback_data="setlang_es"),
        types.InlineKeyboardButton("🇧🇷 PT", callback_data="setlang_pt"),
        types.InlineKeyboardButton("🇹🇷 TR", callback_data="setlang_tr"),
        types.InlineKeyboardButton("🇮🇳 HI", callback_data="setlang_hi"),
        types.InlineKeyboardButton("🇸🇦 AR", callback_data="setlang_ar")
    ]
    markup.add(*langs)
    # მისალმება სულ ინგლისურად
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

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['start_btn'] for l in STRINGS))
def pair_menu(message):
    uid = message.from_user.id
    l = user_lang.get(uid, 'en')
    if not is_vip(uid):
        bot.send_message(message.chat.id, STRINGS[l]['paywall'], parse_mode="Markdown")
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(*(types.InlineKeyboardButton(f"💎 {p}", callback_data=f"pair_{p}") for p in PAIRS))
    bot.send_message(message.chat.id, STRINGS[l]['choose_pair'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['info_btn'] for l in STRINGS))
def info_msg(message):
    l = user_lang.get(message.from_user.id, 'en')
    bot.send_message(message.chat.id, STRINGS[l]['info_text'], parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['ref_btn'] for l in STRINGS))
def ref_msg(message):
    uid = message.from_user.id
    l = user_lang.get(uid, 'en')
    bot.send_message(uid, STRINGS[l]['ref_text'].format(bot.get_me().username, uid), parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['lang_btn'] for l in STRINGS))
def lang_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    langs = [
        types.InlineKeyboardButton("🇺🇸 EN", callback_data="setlang_en"),
        types.InlineKeyboardButton("🇬🇪 KA", callback_data="setlang_ka"),
        types.InlineKeyboardButton("🇷🇺 RU", callback_data="setlang_ru"),
        types.InlineKeyboardButton("🇪🇸 ES", callback_data="setlang_es"),
        types.InlineKeyboardButton("🇧🇷 PT", callback_data="setlang_pt"),
        types.InlineKeyboardButton("🇹🇷 TR", callback_data="setlang_tr"),
        types.InlineKeyboardButton("🇮🇳 HI", callback_data="setlang_hi"),
        types.InlineKeyboardButton("🇸🇦 AR", callback_data="setlang_ar")
    ]
    markup.add(*langs)
    bot.send_message(message.chat.id, "🌐 Choose Language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("pair_"))
def timeframe_menu(call):
    l = user_lang.get(call.from_user.id, 'en')
    pair = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(*(types.InlineKeyboardButton(f"⏱ {t}", callback_data=f"time_{pair}_{t}") for t in TIMES.keys()))
    bot.edit_message_text(STRINGS[l]['choose_time'].format(pair), call.message.chat.id, call.message.message_id, 
                          reply_markup=markup, parse_mode="Markdown")

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
    bot.edit_message_text(STRINGS[l]['scanning'], call.message.chat.id, call.message.message_id)
    rec, acc = get_analysis(pair, TIMES[t_label])
    icon = "🚀 STRONG BUY" if "STRONG_BUY" in rec else "📈 BUY" if "BUY" in rec else "🆘 STRONG SELL" if "STRONG_SELL" in rec else "📉 SELL" if "SELL" in rec else "⚖️ NEUTRAL"
    res = (f"🌟 **TUKHA SIGNAL LIVE** 🌟\n"
           f"──────────────────\n"
           f"💎 {STRINGS[l]['pair_label']}: `{pair}`\n"
           f"⏱ {STRINGS[l]['time_label']}: `{t_label}`\n"
           f"📊 {STRINGS[l]['signal_label']}: **{icon}**\n"
           f"🎯 {STRINGS[l]['accuracy_label']}: `{acc}%`\n"
           f"──────────────────\n"
           f"{STRINGS[l]['success']}")
    bot.edit_message_text(res, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

if __name__ == "__main__":
    keep_alive()
    try: bot.remove_webhook()
    except: pass
    time.sleep(1)
    print("Tukha Signal ბოტი ჩაირთვა...")
    bot.polling(none_stop=True)
