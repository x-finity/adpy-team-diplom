import logging
from vk_api.utils import get_random_id
import json
import random
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class User:
    def __init__(self, id, mode, cash):
        self.id = id
        self.mode = mode
        self.cash = cash
        self.disliked_users = []

    def dislike_user(self, user_id):
        self.disliked_users.append(user_id)
        logger.info(f"Пользователю {self.id} не понравился пользователь {user_id}")


def Keyboard(buttons):
    new_buttons = []
    for i in range(len(buttons)):
        new_buttons.append([])
        for j in range(len(buttons[i])):
            new_buttons[i].append(None)
    for i in range(len(buttons)):
        for j in range(len(buttons[i])):
            text = buttons[i][j][0]
            color = {'Зеленый': 'positive', 'Красный': 'negative', 'Серый': 'secondary', 'Синий': 'primary'}[buttons[i][j][1]]
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


def action_key(is_favorite, is_blocked):
    keys = [('Назад', 'Синий'), ('Далее', 'Зеленый'), ('💔', 'Красный') if is_favorite else ('❤️', 'Зеленый'),
            ('✅', 'Зеленый') if is_blocked else ('❌', 'Красный')]
    return Keyboard([keys])


# Декоратор для логирования
def log(func):
    def wrapper(*args, **kwargs):
        event = args[0]
        print(f"Обработка сообщения от пользователя {event.user_id}: {event.text.lower()}")
        return func(*args, **kwargs)

    return wrapper


# def sender(user_id, message, keyboard, photos=None):
#     if photos:
#         vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': 0,
#                             'keyboard': json.dumps({'buttons': keyboard}), 'attachment': photos})
#     else:
#         vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': 0,
#                             'keyboard': json.dumps({'buttons': keyboard})})


# def message_handler(func):
#     def wrapper(event):
#         if event.type == VkEventType.MESSAGE_NEW and event.to_me:
#             return func(event)
#
#     return wrapper


#@message_handler


class App:
    def __init__(self, user_api, group_api, db):
        self.uapi = user_api
        self.gapi = group_api
        self.match_id = None
        self.db = db
        self.current_user = None

    def set_current_user(self, user_id_or_name):
        try:
            current_user_id = self.uapi.get_user_id(user_id_or_name)
        except Exception as e:
            print(e)
            return False
        if not self.db.get_user_from_db(current_user_id):
            self.add_user(current_user_id)
        self.current_user = current_user_id
        return current_user_id

    def add_user(self, user_id):
        user_info = self.uapi.get_user_info(user_id)
        photo_list = self.uapi.get_user_photos(user_id)
        self.db.add_user_to_db(user_id, photo_list, **user_info)

    def del_user(self, user_id):
        if self.db.get_user_from_db(user_id):
            self.db.del_user_from_db(user_id)
            return True
        return False

    def get_matches_from_search(self):
        def isal_by_id(user_id):
            if (self.uapi.get_user_info(user_id)['first_name'].isalpha() and
                    self.uapi.get_user_info(user_id)['last_name'].isalpha()):
                return True
            return False

        def invert_sex(sex):
            if sex == 1:
                return 2
            elif sex == 2:
                return 1
            else:
                return sex

        if not self.current_user:
            return False
        user_search_info = self.db.get_user_from_db(self.current_user)
        if user_search_info['age'] > 6:
            user_search_info['age_delta'] = 5
        else:
            user_search_info['age_delta'] = None
        search_chunk = self.uapi.get_search_chunk(
            city=user_search_info['city'], age=user_search_info['age'],
            sex=invert_sex(user_search_info['sex']), age_delta=user_search_info['age_delta'],
            offset=user_search_info['offset'])
        self.db.modify_offset(self.current_user, len(search_chunk))
        if self.db.is_blocked(self.current_user, search_chunk[0]):  # Нужен ли этот блок
            self.get_matches_from_search()                          # если по offset он не попадется?
        if isal_by_id(search_chunk[0]):
            return search_chunk[0]
        else:
            self.get_matches_from_search()

    def handle_message(self, event):
        def if_fav_n_block(user_id, offer_id):
            return [self.db.is_favorite(user_id, offer_id), self.db.is_blocked(user_id, offer_id)]
        if self.gapi.vk_event_type(event.type) and event.to_me:
            print(f'processing event from user {event.user_id}, text: {event.text.lower()}')
            user_id = str(event.user_id)
            user_message_from = event.text.lower()
            if user_message_from == "начать":
                self.add_user(user_id)
                user_info = self.db.get_user_from_db(user_id)
                self.gapi.sender(user_id, f"Привет, {user_info['first_name']}!\n"
                                          f"Нажми кнопку \"Поиск людей\" для начала поиска пары", next_key)
            elif user_message_from == "поиск людей" or user_message_from == "далее":
                self.set_current_user(user_id)
                self.match_id = self.get_matches_from_search()
                match_info = self.uapi.get_user_info(self.match_id)
                photos_id = self.uapi.get_user_photos(self.match_id)
                if_blocked = self.db.is_blocked(self.current_user, self.match_id)
                if_favorite = self.db.is_favorite(self.current_user, self.match_id)
                photo_attach = ','.join([f'photo{self.match_id}_{photo_id}' for photo_id in photos_id])
                print(photo_attach)
                self.gapi.sender(user_id,
                                 f"Пользователь https://vk.com/id{str(self.match_id)}\n{match_info['first_name']} {match_info['last_name']}\n"
                                 f"Возраст: {match_info['age']}\nиз города {match_info['city']}",
                                 action_key(if_favorite, if_blocked), photos=photo_attach)
            elif user_message_from == "❤️":
                self.add_user(self.match_id)
                self.db.add_matching_to_db(self.current_user, self.match_id)
                self.db.modify_matching_to_favorite(self.current_user, self.match_id)
                self.gapi.sender(user_id, f"Пользователь {self.match_id} добавлен в избранное", action_key(
                    *if_fav_n_block(self.current_user, self.match_id)))
            elif user_message_from == "💔":
                self.db.modify_matching_to_favorite(self.current_user, self.match_id, is_favorite=False)
                self.gapi.sender(user_id, f"Пользователь {self.match_id} удален из избранного", action_key(
                    *if_fav_n_block(self.current_user, self.match_id)))
            elif user_message_from == "❌":
                self.add_user(self.match_id)
                self.db.add_matching_to_db(self.current_user, self.match_id)
                self.db.modify_matching_to_blacklist(self.current_user, self.match_id)
                self.gapi.sender(user_id, f"Пользователь {self.match_id} добавлен в черный список", action_key(
                    *if_fav_n_block(self.current_user, self.match_id)))
            elif user_message_from == "✅":
                self.db.modify_matching_to_blacklist(self.current_user, self.match_id, is_blocked=False)
                self.gapi.sender(user_id, f"Пользователь {self.match_id} удален из черного списка", action_key(
                    *if_fav_n_block(self.current_user, self.match_id)))
            elif user_message_from == "назад":
                self.gapi.sender(user_id, "Выберите действие:", start_key)
            else:
                self.gapi.sender(user_id, f"{user_message_from}", start_key)


def start(config):
    app = App(VkUserAPI(config['VK_USER_TOKEN']), VkGroupAPI(config['VK_GROUP_TOKEN']), AppDB(config))
    longpoll = app.gapi.get_longpoll()
    for event in longpoll.listen():
        app.handle_message(event)


if __name__ == '__main__':
    from modules.database import load_config, AppDB
    from modules.vkapi import VkUserAPI, VkGroupAPI

    config = load_config()
    start(config)
