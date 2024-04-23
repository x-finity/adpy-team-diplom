import requests

class VKAPIClient:
    API_BASE_URL = 'https://api.vk.com/method'

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.199'
        }

    def _build_url(self, api_method):
        return f'{self.API_BASE_URL}/{api_method}'

    def get_profile_photos(self):
        parameters = self.get_common_params()
        parameters.update({
            'user_ids': self.user_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1
        })
        response = requests.get(self._build_url('photos.get'),
                                params=parameters)
        return response.json()