import config
import aiml
import telebot
import time
import os
import requests

kernel = aiml.Kernel()
if os.path.isfile("brain.brn"):
    kernel.bootstrap(brainFile="brain.brn")
else:
    kernel.bootstrap(learnFiles="startup.xml", commands="LOAD AIML BOT")
    kernel.saveBrain("brain.brn")


bot = telebot.TeleBot(config.token)

SESSION = False


@bot.message_handler(commands=["start"])
def handle_start(message):
    title = "Бот - криптовалютчик, расскажет все о битках и нальет виски\n*нет*"
    bot.send_message(message.chat.id, title)


@bot.message_handler(commands=["help"])
def handle_help(message):
    help = "Можешь написать мне 'давай поболтаем', но болтаю я ток о криптовалюте\n" \
           "Если тебя интересует крипта:\n" \
           "скажи курс _;\n" \
           "что ты думаешь о _;\n" \
           "покажи популярные криптовалюты;"
    bot.send_message(message.chat.id, help)


@bot.message_handler(content_types=["text"])
def chat(message):
    global SESSION
    if not SESSION:
        if message.text.lower() not in ["привет",]:
            bot.send_message(message.chat.id, "А поздороваться? Оо")
            return
        else:
            SESSION = True
    elif message.text.lower() in ["привет",]:
        bot.send_message(message.chat.id, "Мы уже здоровались Оо")
        return
    if message.text.lower() in ["пока",] and SESSION:
        SESSION = False

    kernel.setPredicate("name", message.chat.first_name + " " + message.chat.last_name, message.chat.id)
    print("message by " + message.chat.first_name + " " + message.chat.last_name)
    bot_response = kernel.respond(message.text, message.chat.id)
    if "скажи курс" in message.text.lower() and bot_response not in ["моя твоя не понимэ", "аааа сложна",
                                                                     "шо? Оо"]:
        curr = kernel.getPredicate("curr", message.chat.id)
        response = requests.get("https://api.cryptonator.com/api/ticker/{0}-rub".format(curr.lower()))
        if response.json()["success"]:
            price = response.json()["ticker"]["price"] + " rub"
        else:
            price = "такой криптовалюты нет"
        bot.send_message(message.chat.id, "{0} {1}".format(bot_response, price))
    elif "что ты думаешь о" in message.text.lower() and bot_response not in ["моя твоя не понимэ", "аааа сложна",
                                                                             "шо? Оо"]:
        curr_info = kernel.getPredicate("curr_info", message.chat.id)
        response = requests.get("https://api.cryptonator.com/api/ticker/{0}-rub".format(curr_info.lower()))
        if response.json()["success"]:
            if response.json()["ticker"]["base"] == "BTC":
                answer = "это ж биток, закупайся пока не поздно!"
            else:
                advice = "закупайся!" if float(
                    response.json()["ticker"]["change"]) < 0 else "закупаться не стоит, подожди снижения курса!"
                answer = "Изменение курса за последний час: {0}, совет - {1}".format(
                    response.json()["ticker"]["change"], advice)
        else:
            answer = "такой криптовалюты нет"
        bot.send_message(message.chat.id, "{0} {1}".format(bot_response, answer))
    else:
        bot_response = bot_response.replace("and", "\n")
        bot.send_message(message.chat.id, bot_response)


def telegram_polling(none_stop=True, timeout=5):
    try:
        bot.polling(none_stop, timeout)
    except:
        bot.stop_polling()
        time.sleep(10)
        telegram_polling()


if __name__ == '__main__':
    telegram_polling()