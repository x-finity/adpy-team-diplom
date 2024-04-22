import vk_api
import json
from vk_api.longpoll import VkLongPoll, VkEventType


class VkBot:
    def __init__(self, token):
        self.token = token
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)

        self.keyboard = self.generate_keyboard([['Привет', 'Пока']], one_time=False)

    def generate_keyboard(self, buttons, one_time=True):
        keyboard = {
            "one_time": one_time,
            "buttons": [[self.get_button(text, 'positive') for text in row] for row in buttons]
        }
        return json.dumps(keyboard, ensure_ascii=False).encode('utf-8').decode('utf-8')

    def get_button(self, text, color):
        return {
            "action": {
                "type": "text",
                "payload": "{\"button\": \"" + "1" + "\"}",
                "label": text
            },
            "color": color
        }

    def sender(self, user_id, message):
        self.vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': 0, 'keyboard': self.keyboard})

    def handle_message(self, event):
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                user_id = event.user_id
                message = event.text.lower()
                self.sender(user_id, message.upper())

    def start(self):
        for event in self.longpoll.listen():
            self.handle_message(event)


if __name__ == "__main__":
    token = 'vk1.a.GANkgLMit6kQxEW8nCRllSQrcaAGu6jyxGbRqhOG__KryGP84fROOcGu6k-3UfRWpSF3hBXaVi08ur8Ouce8LWUZHuO6kPzN9CL4UaJ6bDgyXdGz88Ul_FZKon_nDaraPxDT3iC5rCsz93gPyiQ_MZBTIrNfDC75fAMC_-h5I88JzDEnVQ8ZDKeJGrXYZM-pfUOHnVbcWlfavX85EkiA7A'
    bot = VkBot(token)
    bot.start()
