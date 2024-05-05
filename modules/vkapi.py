import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from datetime import date
import json
from pprint import pprint


def get_age(bdate):
    if bdate.count('.') == 2:
        bdate = date(*[int(x) for x in bdate.split('.')[::-1]])
    else:
        return 0
    today = date.today()
    age = today.year - bdate.year
    if today.month < bdate.month or (today.month == bdate.month and today.day < bdate.day):
        age -= 1
    return age


class VkGroupAPI:
    def __init__(self, token):
        if isinstance(token, dict):
            self.token = token['VK_GROUP_TOKEN'][:]
        else:
            self.token = token[:]
        self.vk_session = vk_api.VkApi(token=token)

    def sender(self, user_id, message, keyboard, photos=None):
        if photos:
            self.vk_session.method('messages.send', {'user_id': user_id, 'message': message,
                                                     'random_id': 0, 'keyboard': json.dumps({'buttons': keyboard}),
                                                     'attachment': photos})
        else:
            self.vk_session.method('messages.send', {'user_id': user_id, 'message': message,
                                                     'random_id': 0, 'keyboard': json.dumps({'buttons': keyboard})})

    def get_longpoll(self):
        return VkLongPoll(self.vk_session)

    def vk_event_type(self, event_type):
        return True if event_type == VkEventType.MESSAGE_NEW else False


class VkUserAPI:

    def __init__(self, token):
        # print(f'start {token}')
        if isinstance(token, dict):
            self.token = token['VK_USER_TOKEN'][:]
        else:
            self.token = token[:]
        # print(self.token)
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()

    def get_user_info(self, user_id):
        try:
            user_info = self.vk.users.get(user_ids=user_id, fields='sex, city, bdate')
            if user_info:
                user_info = user_info[0]
                # print(user_info)
                if 'bdate' in user_info:
                    bdate = user_info['bdate']
                    age = get_age(bdate)
                else:
                    age = None
                first_name = user_info['first_name']
                last_name = user_info['last_name']
                sex = user_info['sex']
                city = user_info.get('city', {}).get('title', 'Не указано')
                return {'first_name': first_name, 'last_name': last_name, 'sex': sex, 'city': city, 'age': age}
            else:
                return None
        except Exception as e:
            print("Ошибка при получении информации о пользователе:", e)
            return None

    def get_user_photos(self, user_id, flag=None):
        photos = self.vk.photos.get(owner_id=user_id, album_id='profile', extended=1).get('items')
        if flag is not None:
            return photos
        if photos:
            photos.sort(key=lambda x: x['likes']['count'], reverse=True)
            if len(photos) > 3:
                photos = photos[:3]
            photo_id = [photo['id'] for photo in photos]
            return photo_id

    def get_user_id(self, user_name):
        if isinstance(user_name, int):
            return user_name
        elif user_name.isdigit():
            return int(user_name)
        user = self.vk.users.get(user_ids=user_name)
        return user[0].get('id')

    def get_search_chunk(self, city, age, sex, age_delta=None, offset=0, count=1, has_photo=True):
        if age_delta is None:
            result = self.vk.users.search(count=count, offset=offset,
                                          hometown=city, has_photo=has_photo, sex=sex)
        else:
            result = self.vk.users.search(count=count, offset=offset,
                                          hometown=city, has_photo=has_photo, age_from=age - age_delta,
                                          age_to=age + age_delta, sex=sex)
        return [user.get('id') for user in result['items']]

    def get_search_result(self, city, age, sex, age_delta=5, offset=0, count=10, has_photo=True, max_count=10):
        while True:
            result = self.vk.users.search(count=count, offset=offset,
                                          hometown=city, has_photo=has_photo, age_from=age - age_delta,
                                          age_to=age + age_delta, sex=sex)
            for user in result['items']:
                if user.get('id') is not None:
                    if max_count is not None and offset >= max_count:
                        return
                    yield user['id']
                    offset += 1


if __name__ == "__main__":
    pass
