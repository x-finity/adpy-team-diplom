import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import json
import random
#
# config = load_config()
# session = create_session(config)


vk_session = vk_api.VkApi(token="...")
longpoll = VkLongPoll(vk_session)


class User:
    def __init__(self, id, mode, cash):
        self.id = id
        self.mode = mode
        self.cash = cash
        self.disliked_users = []

    def dislike_user(self, user_id):
        self.disliked_users.append(user_id)


def Keyboard(buttons):
    new_buttons = []
    for i in range(len(buttons)):
        new_buttons.append([])
        for j in range(len(buttons[i])):
            new_buttons[i].append(None)
    for i in range(len(buttons)):
        for j in range(len(buttons[i])):
            text = buttons[i][j][0]
            color = {'Зеленый': 'positive', 'Красный': 'negative', 'Серый': 'secondary'}[buttons[i][j][1]]
            new_buttons[i][j] = {'action': {'type': 'text', 'payload': '{"button": "1"}', 'label': text},
                                 'color': color}
    return new_buttons


start_key = Keyboard([
    [('Начать', 'Зеленый')],
])

next_key = Keyboard([
    [('Назад', 'Красный'), ('Поиск людей', 'Зеленый')],
])

form_key = Keyboard([
    [('Назад', 'Красный'), ('Заполнить форму', 'Зеленый')],
])

parameters_key = Keyboard([
    [('Назад', 'Красный'), ('Пол', 'Зеленый'), ('Возраст', 'Зеленый')],
])

search_key = Keyboard([
    [('Назад', 'Красный'), ('', 'Зеленый')],
])

action_key = Keyboard([
    [('Назад', 'Красный'), ('Нравится', 'Зеленый'), ('Не нравится', 'Серый')],
])


# Декоратор для логирования
def log(func):
    def wrapper(*args, **kwargs):
        event = args[0]
        print(f"Обработка сообщения от пользователя {event.user_id}: {event.text.lower()}")
        return func(*args, **kwargs)
    return wrapper



def sender(user_id, message, keyboard):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': 0, 'keyboard': json.dumps({'buttons': keyboard})})



def message_handler(func):
    def wrapper(event):
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            return func(event)
    return wrapper



@message_handler
def handle_message(event):
    user_id = event.user_id
    # Проверяем, есть ли уже пользователь в словаре users, если нет - создаем нового
    # user = users.get(user_id, User(user_id, None, None))
    # Обработка различных вариантов текста сообщения
    if event.text.lower() == "начать":
        sender(event.user_id, "Привет!", next_key)
    elif event.text.lower() == "поиск людей":
        sender(event.user_id, "Выберите действие:", action_key)
    elif event.text.lower() == "заполнить форму":
        sender(event.user_id, "Заполните форму!", parameters_key)
    elif event.text.lower() == "назад":
        sender(event.user_id, "Выберите действие:", start_key)



for event in longpoll.listen():
    handle_message(event)
