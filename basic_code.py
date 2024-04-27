import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import json
from modules.database import load_config, create_session
config = load_config()
session = create_session(config)


class User:
    def __init__(self, id, mode, cash):
        self.id = id
        self.mode = mode
        self.cash = cash


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

search_key = Keyboard([
    [('Назад', 'Красный'), ('Заполнить форму', 'Зеленый')],
])

parameters_key = Keyboard([
    [('Назад', 'Красный'), ('Пол', 'Зеленый'), ('Возраст', 'Зеленый')],
])


def sender(user_id, message, keyboard):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': 0, 'keyboard': json.dumps({'buttons': keyboard})})


users = {}

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            if event.text.lower() == "начать":
                sender(event.user_id, "Привет!", next_key)
            elif event.text.lower() == "поиск людей":
                sender(event.user_id, "Выберите действие:", search_key)
            elif event.text.lower() == "заполнить форму":
                sender(event.user_id, "Заполните форму!", parameters_key)
                if event.text.lower() == "назад":
                    sender(event.user_id, "Выберите действие:", search_key)
            elif event.text.lower() == "назад":
                sender(event.user_id, "Выберите действие:", start_key)
