import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message
from dotenv import load_dotenv
from os import getenv
from data import load_data, save_data, game_data1

load_dotenv()
bot = telebot.TeleBot(getenv('TOKEN'))
user_data = load_data()
game_data = game_data1()


@bot.message_handler(commands=['help'])
def message_help(message):
    user_id = message.from_user.id
    bot.send_message(
        chat_id=user_id,
        text="Это помощь с ботом!\n"
             "Чтобы запустить бота - /start\n"
             "Чтобы узнать как я работаю - /about\n"
             "Чтобы узнать о моих возможностях - /help")


@bot.message_handler(commands=['about'])
def message_about(message):
    user_id = message.from_user.id
    bot.send_message(
        chat_id=user_id,
        text='Этот бот-квест написан @ziinnger и соавтором, человеком, который меня выручил, прекрасной @linamistq')
    bot.send_sticker(
        chat_id=user_id,
        sticker="CAACAgIAAxkBAAELFV9llU7QjE3AIpuaSSu8PX5y6grW4AACMQMAAm2wQgOanBOYGq4GgDQE"
    )


@bot.message_handler(commands=['start'])
def message_start(message):
    user_id = message.from_user.id
    markup = ReplyKeyboardMarkup()

    if str(user_id) not in user_data:
        markup.add(KeyboardButton("Начать путешествие🚀"))

        user_data[str(user_id)] = {
            "user_name": message.from_user.username,
            "location": "start"
        }

        save_data(user_data)
    elif str(user_id) in user_data:
        markup.add(KeyboardButton("Продолжить🪐"), KeyboardButton("Начать заново🛸"))

    text = ("<b>{}</b>!🚀 Добро пожаловать в 3072 год! На Земле начали происходить частые массовые "
            "экологические катастрофы, поэтому человечество было вынуждено отправлять экспедиции в космос "
            "для поисков планет, которые пригодны для жизни.\n\n"
            "Вы — упорный специалист по космической навигации, который отправился в очередную экспедицию, чтобы спасти "
            "человечество.\n\n<i>Выберите действие, Ваши решения влияют на отношения, тайны и будущее общества. "
            "Продолжайте выбирать, и помните: каждое действие имеет свои последствия.</i>")

    with open(r'C:\Users\Юля\PycharmProject\pythonProject_bot\media\1.jpg', 'rb') as f:
        bot.send_photo(
            message.chat.id,
            f,
            caption=text.format(message.from_user.username),
            reply_markup=markup,
            parse_mode='html'
        )


def create_markup(user_data, user_id, game_data):
    markup = ReplyKeyboardMarkup()
    key = user_data[str(user_id)]['location']
    if key and key in game_data and 'options' in game_data[key].keys():
        for option in game_data[key]['options'].keys():
            markup.add(option)
    else:
        markup.add("Начать заново🛸")
    return markup


def filter_continues(message: Message):
    keywords = ["Продолжить🪐", "Начать путешествие🚀"]
    return message.text in keywords


@bot.message_handler(func=filter_continues)
def continue_restart(message: Message):
    user_id = message.from_user.id
    send_question(user_id)


def filter_restart(message: Message):
    keywords = ["Начать заново🛸"]
    return message.text in keywords


@bot.message_handler(func=filter_restart)
def restart_solution(message: Message):
    user_id = message.from_user.id
    user_data[str(user_id)]['location'] = 'start'
    save_data(user_data)
    send_question(user_id)


def send_question(user_id):
    key = user_data[str(user_id)]['location']
    description = game_data[key]['description']
    photo = game_data[key]['media']
    markup = create_markup(user_data, user_id, game_data)
    if key != "planet_v" and key != "planet":
        with open(photo, 'rb') as f:
            bot.send_photo(
                chat_id=user_id,
                photo=f,
                caption=f'{description}\n\n'
                        f'<i>Каждое Ваше действие имеет свои последствия.\n'
                        f'Ваше решение...</i>',
                reply_markup=markup,
                parse_mode='html'
            )
    elif key == "planet_v":

        with open(photo, 'rb') as f:
            bot.send_photo(
                chat_id=user_id,
                photo=f,
                caption=f"{description}\n"
                        f"Теперь планета носит название <b>{user_data[str(user_id)]['user_name']}</b>!",
                reply_markup=markup,
                parse_mode='html'
            )
    else:
        with open(photo, 'rb') as f:
            bot.send_photo(
                chat_id=user_id,
                photo=f,
                caption=description,
                reply_markup=markup,
                parse_mode='html'
            )


@bot.message_handler(func=lambda message: True)
def handle_answer(message):
    user_id = message.chat.id

    if str(user_id) not in user_data:
        return message_start(message)

    user_answer = message.text
    key = user_data[str(user_id)]['location']

    if user_answer not in game_data[key]['options'].keys():
        bot.send_message(
            user_id, "Пожалуйста, выберите один из предложенных вариантов."
        )
        return
    change_scales(str(user_id), user_answer)
    send_question(str(user_id))


def change_scales(user_id: str, user_answer: str):
    key = user_data[str(user_id)]['location']
    location = game_data[key]['options'][user_answer]
    user_data[str(user_id)]['location'] = location
    save_data(user_data)


bot.polling(none_stop=True)