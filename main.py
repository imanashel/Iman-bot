
from flask import Flask, request
import requests
import telebot
from telebot import types

BOT_TOKEN = 'YOUR_BOT_TOKEN'
MY_CHAT_IDS = [6963943034]

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route("/", methods=["POST"])
def send_to_bot():
    data = request.json
    if not data or "text" not in data:
        return {"error": "Missing 'text' field"}, 400

    payload = {"text": data["text"]}
    for chat_id in MY_CHAT_IDS:
        bot.send_message(chat_id, payload['text'])
    return {"status": "sent to all"}, 200

user_states = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📊 سیگنال اسکالپ")
    btn2 = types.KeyboardButton("📈 سیگنال روزانه")
    btn3 = types.KeyboardButton("💵 مدیریت سرمایه")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "سلام حاج ایمان! یکی از گزینه‌ها رو انتخاب کن:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id

    if message.text == "📊 سیگنال اسکالپ":
        bot.send_message(user_id, "⏱ سیگنال اسکالپ آماده نیست (در حال توسعه).")
    elif message.text == "📈 سیگنال روزانه":
        bot.send_message(user_id, "📆 سیگنال روزانه هنوز ارسال نشده.")
    elif message.text == "💵 مدیریت سرمایه":
        user_states[user_id] = {'step': 1}
        bot.send_message(user_id, "✅ لطفاً مقدار سرمایه خود را وارد کنید:")
    elif user_id in user_states:
        state = user_states[user_id]
        if state['step'] == 1:
            try:
                state['capital'] = float(message.text)
                state['step'] = 2
                bot.send_message(user_id, "✅ حالا قیمت ورود (Entry) را وارد کنید:")
            except:
                bot.send_message(user_id, "لطفاً یک عدد معتبر برای سرمایه وارد کنید.")
        elif state['step'] == 2:
            try:
                state['entry'] = float(message.text)
                state['step'] = 3
                bot.send_message(user_id, "✅ حالا حد ضرر (SL) را وارد کنید:")
            except:
                bot.send_message(user_id, "لطفاً یک عدد معتبر برای Entry وارد کنید.")
        elif state['step'] == 3:
            try:
                state['sl'] = float(message.text)
                distance = abs(state['entry'] - state['sl'])
                risk = state['capital'] * 0.02
                if distance == 0:
                    bot.send_message(user_id, "❌ فاصله بین Entry و SL صفر است!")
                else:
                    amount = round(risk / distance, 6)
                    bot.send_message(user_id,
                        f"✅ محاسبه انجام شد:\n\n"
                        f"💵 سرمایه: {state['capital']}$\n"
                        f"📉 فاصله حد ضرر: {distance}$\n"
                        f"⚠️ ریسک: {risk}$ (۲٪)\n"
                        f"📊 مقدار ورود مناسب: {amount} واحد"
                    )
                del user_states[user_id]
            except:
                bot.send_message(user_id, "لطفاً عدد معتبر برای SL وارد کنید.")
    else:
        bot.send_message(user_id, "⛔️ دستور نامعتبر است.")

if __name__ == '__main__':
    from threading import Thread
    Thread(target=bot.polling, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
