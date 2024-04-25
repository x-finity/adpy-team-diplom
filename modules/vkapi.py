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
                sex = True if user_info['sex'] == 1 else False if user_info['sex'] == 2 else None
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

    def get_search_result(self, city, age, sex, age_delta=5):
        return self.vk.users.search(count=100, hometown=city, age_from=age - age_delta, age_to=age + age_delta, sex=sex)


if __name__ == "__main__":
    from database import load_config
    token = load_config()['VK_GROUP_TOKEN']
    # print("Токен VK:", token)
    # user_id = input("Введите введите ID пользователя: ") or 126875243
    # vk_group = VkGroupAPI(token)
    # user_info = vk_group.get_user_info(user_id)
    # if user_info:
    #     print("Имя:", user_info['first_name'])
    #     print("Фамилия:", user_info['last_name'])
    #     print("Пол:", "Женский" if user_info['sex'] == 1 else "Мужской")
    #     print("Город:", user_info['city'])
    #     print("Возраст:", user_info['age'])
    # else:
    #     print("Не удалось получить информацию о пользователе.")

    vk_user = VkUserAPI(load_config()['VK_USER_TOKEN'])
    user_id = vk_user.get_user_id(input("Введите введите ID пользователя: ") or 126875243)
    # print(vk_user.get_user_info(user_id))
    # print(vk_user.get_search_result('Москва', 30, 1))
    pprint(vk_user.get_user_photos(user_id))