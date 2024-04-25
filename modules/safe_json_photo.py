from pprint import pprint
from urllib.parse import urlencode
import json


def token_vk():
    VK_TOKEN = config('vk_token')
    return VK_TOKEN


def get_token():
    APP_ID = "51846243"
    OAUTH_BASE_URL = "https://oauth.vk.com/authorize"
    params = {
        'client_id': APP_ID,
        'redirect_uri': 'https://oauth.vk.com/blank.html',
        'display': 'page',
        'scope': 'status,photos',
        'response_type': 'token',
    }
    oauth_url = f'{OAUTH_BASE_URL}?{urlencode(params)}'
    return oauth_url


def download_json(info_photos):
    with open('file1.json', 'w') as json_file:
        json.dump(info_photos, json_file)

if __name__ == '__main__':
    print(get_token())