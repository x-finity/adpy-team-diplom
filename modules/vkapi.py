import vk_api
from datetime import date


def get_age(bdate):
    print(bdate)
    if bdate.count('.') == 2:
        bdate = date(*[int(x) for x in bdate.split('.')[::-1]])
    elif bdate.count('.') == 1:
        bdate = date(*[int(x) for x in bdate.split('.')[::-1]],1)
    else:
        bdate = date(int(bdate), 1, 1)
    print(bdate)
    today = date.today()
    age = today.year - bdate.year
    if today.month < bdate.month or (today.month == bdate.month and today.day < bdate.day):
        age -= 1
    return age


class VkUser:
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


if __name__ == "__main__":
    from database import load_config
    token = load_config()['VK_TOKEN']
    print("Токен VK:", token)
    user_id = input("Введите введите ID пользователя: ")
    vk_user = VkUser(token)
    user_info = vk_user.get_user_info(user_id)
    if user_info:
        print("Имя:", user_info['first_name'])
        print("Фамилия:", user_info['last_name'])
        print("Пол:", "Женский" if user_info['sex'] == 1 else "Мужской")
        print("Город:", user_info['city'])
    else:
        print("Не удалось получить информацию о пользователе.")
