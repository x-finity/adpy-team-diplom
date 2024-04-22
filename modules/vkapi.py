import vk_api


class VkUser:
    def __init__(self, token):
        self.token = token
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()

    def get_user_info(self, user_id):
        try:
            user_info = self.vk.users.get(user_ids=user_id, fields='sex, city')
            if user_info:
                user_info = user_info[0]
                first_name = user_info['first_name']
                last_name = user_info['last_name']
                sex = user_info['sex']
                city = user_info.get('city', {}).get('title', 'Не указано')
                return {'first_name': first_name, 'last_name': last_name, 'sex': sex, 'city': city}
            else:
                return None
        except Exception as e:
            print("Ошибка при получении информации о пользователе:", e)
            return None


if __name__ == "__main__":
    token = ...
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
