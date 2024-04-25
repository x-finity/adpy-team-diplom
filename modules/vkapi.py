import vk_api
from datetime import date
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
        self.token = token
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()


class VkUserAPI:

    def __init__(self, token):
        self.token = token
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

    def get_user_photos(self, user_id):
        photos = self.vk.photos.get(owner_id=user_id, album_id='profile', extended=1).get('items')
        if photos:
            photos.sort(key=lambda x: x['likes']['count'], reverse=True)
            if len(photos) > 3:
                photos = photos[:3]
            photo_urls = [photo['sizes'][-1]['url'] for photo in photos]
            return photo_urls

    def get_user_id(self, user_name):
        if isinstance(user_name, int):
            return user_name
        elif user_name.isdigit():
            return int(user_name)
        user = self.vk.users.get(user_ids=user_name)
        return user[0].get('id')

    def get_search_result(self, city, age, sex, age_delta=5, offset=0, count=10, user_id=None, has_photo=True, max_count=None):
        from modules.database import is_blocked
        from basic_code import session
        while True:
            result = self.vk.users.search(count=count, offset=offset,
                                          hometown=city, has_photo=has_photo, age_from=age - age_delta,
                                          age_to=age + age_delta, sex=sex)
            for user in result['items']:
                if user.get('id') is not None:
                    if is_blocked(session, user_id, user['id']):
                        continue
                    if max_count is not None and offset >= max_count:
                        return
                    yield user['id']
                    offset += 1


if __name__ == "__main__":
    pass
