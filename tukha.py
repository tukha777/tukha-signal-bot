import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
from flask import Flask
from threading import Thread
import os
import time

# --- Flask Server ---
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

# 🛑 VIP მომხმარებლების ID
ALLOWED_USERS = [8696404791, 8711448963] 

user_lang = {}

# 7 პოპულარული წყვილი
PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY", "AUDUSD", "USDCAD", "BTCUSDT"]

TIMES = {
    "1 MIN": Interval.INTERVAL_1_MINUTE,
    "5 MIN": Interval.INTERVAL_5_MINUTES,
    "15 MIN": Interval.INTERVAL_15_MINUTES,
    "30 MIN": Interval.INTERVAL_30_MINUTES
}

# --- 8 ენის მონაცემთა ბაზა ---
STRINGS = {
    'en': {
        'welcome': "✨ **Welcome to Tukha Signal Bot** ✨\n\nPlease select your language to proceed:",
        'main_msg': "💎 **Main Menu**\n──────────────────\nSelect an option below:",
        'lang_btn': "🌐 Language",
        'info_btn': "ℹ️ Information",
        'start_btn': "🚀 Start Signal",
        'ref_btn': "🎁 Referrals",
        'paywall': "🚫 **Access Denied!**\n──────────────────\nThis is a professional trading tool.\n\n💰 **Subscription Fee:** $30 / Month\n💎 **Benefits:** Unlimited real-time signals, 75%+ accuracy.\n\n📩 **To Activate:** @TukhaTheGreat",
        'choose_pair': "📊 **Choose Asset**\nSelect a trading pair:",
        'choose_time': "⏳ **Timeframe**\nPair: `{}`\nSelect expiry:",
        'scanning': "🔍 **Scanning Market Data...**",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nThe bot analyzes Forex and major Crypto pairs in real-time.\n\n💡 **Golden Rule:**\nTrust only signals with accuracy higher than 75%.\n\n⚠️ **Forex does not work on weekends!**",
        'ref_text': "🎁 **Referral Program**\n──────────────────\nInvite friends and get **+7 days VIP** for every active user!\n\n🔗 Your link:\n`https://t.me/{}?start={}`",
        'pair_label': "Asset", 'time_label': "Time", 'signal_label': "Signal", 'accuracy_label': "Accuracy", 'success': "✅ Good luck!"
    },
    'ka': {
        'welcome': "✨ **მოგესალმებით Tukha Signal Bot-ში** ✨\n\nგთხოვთ, აირჩიოთ ენა გასაგრძელებლად:",
        'main_msg': "💎 **მთავარი მენიუ**\n──────────────────\nაირჩიეთ სასურველი ღილაკი:",
        'lang_btn': "🌐 ენა",
        'info_btn': "ℹ️ ინფორმაცია",
        'start_btn': "🚀 სიგნალის დაწყება",
        'ref_btn': "🎁 რეფერალები",
        'paywall': "🚫 **წვდომა შეზღუდულია!**\n──────────────────\nეს არის პროფესიონალური სავაჭრო ინსტრუმენტი.\n\n💰 **ღირებულება:** 30$ / თვეში\n💎 **რას მიიღებთ:** შეუზღუდავი სიგნალები რეალურ დროში, 75%+ სიზუსტე.\n\n📩 **გასააქტიურებლად:** @TukhaTheGreat",
        'choose_pair': "📊 **აირჩიეთ წყვილი**\nაირჩიეთ აქტივი ანალიზისთვის:",
        'choose_time': "⏳ **დროის შერჩევა**\nწყვილი: `{}`\nაირჩიეთ ვადა:",
        'scanning': "🔍 **ბაზრის სკანირება...**",
        'info_text': "🤖 **Tukha Signal Bot v3.2**\n\nბოტი აანალიზებს ფორექსსა და მთავარ კრიპტო წყვილებს რეალურ დროში.\n\n💡 **ოქროს წესი:**\nენდეთ მხოლოდ იმ სიგნალებს, რომელთა სიზუსტე 75%-ზე მაღალია.\n\n⚠️ **ფორექსი არ მუშაობს შაბათ-კვირას!**",
        'ref_text': "🎁 **რეფერალური სისტემა**\n──────────────────\nმოიწვიე მეგობარი და მიიღე **+7 დღე VIP** საჩუქრად ყოველ აქტიურ იუზერზე!\n\n🔗 შენი ლინკი:\n`https://t.me/{}?start={}`",
        'pair_label': "აქტივი", 'time_label': "ვადა", 'signal_label': "სიგნალი", 'accuracy_label': "სიზუსტე", 'success': "✅ წარმატებულ ვაჭრობას გისურვებთ!"
    },
    'ru': {
        'welcome': "✨ **Tukha Signal Bot** ✨\n\nВыберите язык:",
        'main_msg': "💎 **Главное меню**\n──────────────────",
        'lang_btn': "🌐 Язык", 'info_btn': "ℹ️ Инфо", 'start_btn': "🚀 Старт", 'ref_btn': "🎁 Рефералы",
        'paywall': "🚫 **Доступ закрыт!**\n\n💰 **Цена:** $30 / Месяц\n📩 **Контакт:** @TukhaTheGreat",
        'choose_pair': "📊 Выберите пару:", 'choose_time': "⏳ Пара: `{}`\nВыберите время:",
        'scanning': "🔍 Сканирование...", 'info_text': "🤖 **v3.2**\nРаботает в реальном времени. Точность 75%+",
        'ref_text': "🎁 Пригласи друга и получи **+7 дней VIP**!\n\n🔗 Ссылка:\n`https://t.me/{}?start={}`",
        'pair_label': "Актив", 'time_label': "Время", 'signal_label': "Сигнал", 'accuracy_label': "Точность", 'success': "✅ Удачи!"
    },
    'es': { 'welcome': "✨ **Bienvenido** ✨\nElige tu idioma:", 'main_msg': "💎 **Menú Principal**", 'lang_btn': "🌐 Idioma", 'info_btn': "ℹ️ Info", 'start_btn': "🚀 Señal", 'ref_btn': "🎁 Invitados", 'paywall': "🚫 **Sin Acceso**\n$30 / mes", 'choose_pair': "📊 Elige par:", 'choose_time': "⏳ Tiempo:", 'scanning': "🔍 Escaneando...", 'info_text': "🤖 v3.2. Forex y Crypto.", 'ref_text': "🎁 ¡+7 días gratis!\n`https://t.me/{}?start={}`", 'pair_label': "Activo", 'time_label': "Tiempo", 'signal_label': "Señal", 'accuracy_label': "Fuerza", 'success': "✅ ¡Suerte!" },
    'pt': { 'welcome': "✨ **Bem-vindo** ✨\nEscolha o idioma:", 'main_msg': "💎 **Menu**", 'lang_btn': "🌐 Idioma", 'info_btn': "ℹ️ Info", 'start_btn': "🚀 Sinal", 'ref_btn': "🎁 Convites", 'paywall': "🚫 **Sem Acesso**\n$30 / mês", 'choose_pair': "📊 Par:", 'choose_time': "⏳ Tempo:", 'scanning': "🔍 Analisando...", 'info_text': "🤖 v3.2. Forex & Crypto.", 'ref_text': "🎁 +7 dias VIP!\n`https://t.me/{}?start={}`", 'pair_label': "Ativo", 'time_label': "Tempo", 'signal_label': "Sinal", 'accuracy_label': "Força", 'success': "✅ Boa sorte!" },
    'tr': { 'welcome': "✨ **Hoş Geldiniz** ✨\nDil seçiniz:", 'main_msg': "💎 **Ana Menü**", 'lang_btn': "🌐 Dil", 'info_btn': "ℹ️ Bilgi", 'start_btn': "🚀 Sinyal", 'ref_btn': "🎁 Davet", 'paywall': "🚫 **Erişim Yok**\nAylık $30", 'choose_pair': "📊 Parite:", 'choose_time': "⏳ Süre:", 'scanning': "🔍 Taranıyor...", 'info_text': "🤖 v3.2. Canlı Sinyaller.", 'ref_text': "🎁 Arkadaşını davet et +7 gün VIP kazan!\n`https://t.me/{}?start={}`", 'pair_label': "Varlık", 'time_label': "Süre", 'signal_label': "Sinyal", 'accuracy_label': "Doğruluk", 'success': "✅ Bol kazançlar!" },
    'hi': { 'welcome': "✨ **स्वागत है** ✨\nभाषा चुनें:", 'main_msg': "💎 **मुख्य मेनू**", 'lang_btn': "🌐 भाषा", 'info_btn': "ℹ️ जानकारी", 'start_btn': "🚀 संकेत", 'ref_btn': "🎁 मित्रों को बुलाएं", 'paywall': "🚫 **पहुंच वर्जित**\n$30 / महीना", 'choose_pair': "📊 जोड़ी चुनें:", 'choose_time': "⏳ समय चुनें:", 'scanning': "🔍 स्कैनिंग...", 'info_text': "🤖 v3.2. लाइव संकेत।", 'ref_text': "🎁 मित्रों को आमंत्रित करें और +7 दिन VIP प्राप्त करें!\n`https://t.me/{}?start={}`", 'pair_label': "एसेट", 'time_label': "समय", 'signal_label': "संकेत", 'accuracy_label': "शुद्धता", 'success': "✅ शुभकामनाएँ!" },
    'ar': { 'welcome': "✨ **أهلاً بك** ✨\nاختر اللغة:", 'main_msg': "💎 **القائمة الرئيسية**", 'lang_btn': "🌐 اللغة", 'info_btn': "ℹ️ معلومات", 'start_btn': "🚀 ابدأ الإشارة", 'ref_btn': "🎁 الإحالات", 'paywall': "🚫 **تم رفض الوصول**\n30 دولار شهرياً", 'choose_pair': "📊 اختر الزوج:", 'choose_time': "⏳ اختر الوقت:", 'scanning': "🔍 جاري الفحص...", 'info_text': "🤖 v3.2. إشارات حية.", 'ref_text': "🎁 ادعُ أصدقاءك واحصل على +7 أيام مجانية!\n`https://t.me/{}?start={}`", 'pair_label': "الأصل", 'time_label': "الوقت", 'signal_label': "الإشارة", 'accuracy_label': "الدقة", 'success': "✅ بالتوفيق!" }
}

def get_main_keyboard(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(STRINGS[lang]['lang_btn'], STRINGS[lang]['info_btn'])
    markup.row(STRINGS[lang]['start_btn'])
    markup.row(STRINGS[lang]['ref_btn'])
    return markup

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

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, STRINGS['en']['welcome'], reply_markup=get_lang_inline(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("setlang_"))
def set_language(call):
    lang = call.data.split("_")[1]
    user_lang[call.from_user.id] = lang
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, STRINGS[lang]['main_msg'], reply_markup=get_main_keyboard(lang), parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['start_btn'] for l in STRINGS))
def show_pairs(message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, 'en')
    if user_id not in ALLOWED_USERS:
        bot.send_message(message.chat.id, STRINGS[lang]['paywall'], parse_mode="Markdown")
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(f"💎 {pair}", callback_data=f"pair_{pair}") for pair in PAIRS]
    markup.add(*buttons)
    bot.send_message(message.chat.id, STRINGS[lang]['choose_pair'], reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['info_btn'] for l in STRINGS))
def info_btn(message):
    lang = user_lang.get(message.from_user.id, 'en')
    bot.send_message(message.chat.id, STRINGS[lang]['info_text'], parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['ref_btn'] for l in STRINGS))
def referral_btn(message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, 'en')
    bot_username = bot.get_me().username
    bot.send_message(user_id, STRINGS[lang]['ref_text'].format(bot_username, user_id), parse_mode="Markdown")

@bot.message_handler(func=lambda m: any(m.text == STRINGS[l]['lang_btn'] for l in STRINGS))
def change_lang(message):
    bot.send_message(message.chat.id, "🌐 Choose Language:", reply_markup=get_lang_inline())

@bot.callback_query_handler(func=lambda call: call.data.startswith("pair_"))
def callback_pair(call):
    lang = user_lang.get(call.from_user.id, 'en')
    selected_pair = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(f"⏱ {t}", callback_data=f"time_{selected_pair}_{t}") for t in TIMES.keys()]
    markup.add(*buttons)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text=STRINGS[lang]['choose_time'].format(selected_pair), reply_markup=markup, parse_mode="Markdown")

def get_live_analysis(pair, interval):
    try:
        is_crypto = "USDT" in pair or "BTCUSD" in pair
        screener = "crypto" if is_crypto else "forex"
        exchange = "BINANCE" if is_crypto else "OANDA"
        analysis = TA_Handler(symbol=pair, screener=screener, exchange=exchange, interval=interval, timeout=10).get_analysis()
        summary = analysis.summary['RECOMMENDATION']
        buy, sell, neutral = analysis.summary['BUY'], analysis.summary['SELL'], analysis.summary['NEUTRAL']
        total = buy + sell + neutral
        accuracy = max(buy, sell) / total * 100 if total > 0 else 0
        return summary, round(accuracy, 1)
    except:
        return "NEUTRAL", 0

@bot.callback_query_handler(func=lambda call: call.data.startswith("time_"))
def callback_signal(call):
    lang = user_lang.get(call.from_user.id, 'en')
    data = call.data.split("_")
    pair, time_label = data[1], data[2]
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=STRINGS[lang]['scanning'])
    
    recommendation, accuracy = get_live_analysis(pair, TIMES[time_label])
    icon = "🚀 STRONG BUY" if "STRONG_BUY" in recommendation else "📈 BUY" if "BUY" in recommendation else "🆘 STRONG SELL" if "STRONG_SELL" in recommendation else "📉 SELL" if "SELL" in recommendation else "⚖️ NEUTRAL"
    
    result_text = (
        f"🌟 **TUKHA SIGNAL LIVE** 🌟\n"
        f"──────────────────\n"
        f"💎 {STRINGS[lang]['pair_label']}: `{pair}`\n"
        f"⏱ {STRINGS[lang]['time_label']}: `{time_label}`\n"
        f"📊 {STRINGS[lang]['signal_label']}: **{icon}**\n"
        f"🎯 {STRINGS[lang]['accuracy_label']}: `{accuracy}%`\n"
        f"──────────────────\n"
        f"{STRINGS[lang]['success']}"
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=result_text, parse_mode="Markdown")

if __name__ == "__main__":
    keep_alive()
    # Conflict 409-ის საწინააღმდეგო გასუფთავება
    try:
        bot.remove_webhook()
        time.sleep(2)
    except:
        pass
    bot.polling(none_stop=True)
