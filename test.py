import unittest
from unittest.mock import MagicMock, patch
from basic_code import User, Keyboard, App


class TestUser(unittest.TestCase):
    def test_user_initialization(self):
        user = User(id=123, mode='test', cash=100)
        self.assertEqual(user.id, 123)
        self.assertEqual(user.mode, 'test')
        self.assertEqual(user.cash, 100)
        self.assertEqual(user.disliked_users, [])

    def test_dislike_user(self):
        user = User(id=123, mode='test', cash=100)
        user.dislike_user(456)
        self.assertEqual(user.disliked_users, [456])


class TestKeyboard(unittest.TestCase):
    def test_keyboard_generation(self):
        buttons = [('Начать', 'Зеленый')]
        expected_result = [[{'action': {'type': 'text', 'payload': '{"button": "1"}', 'label': 'Начать'}, 'color': 'positive'}]]
        self.assertEqual(Keyboard(buttons), expected_result)


class TestApp(unittest.TestCase):
    def setUp(self):
        self.mock_user_api = MagicMock()
        self.mock_group_api = MagicMock()
        self.mock_db = MagicMock()
        self.app = App(self.mock_user_api, self.mock_group_api, self.mock_db)

    def test_set_current_user(self):
        self.mock_user_api.get_user_id.return_value = 123
        result = self.app.set_current_user('test_user')
        self.assertEqual(result, 123)
        self.mock_db.get_user_from_db.assert_called_once_with(123)

    @patch('your_module.App.get_matches_from_search')
    def test_handle_message_start(self, mock_get_matches_from_search):
        mock_event = MagicMock()
        mock_event.text.lower.return_value = 'начать'
        mock_event.user_id = 'test_user'
        self.app.handle_message(mock_event)
        self.mock_db.add_user_to_db.assert_called_once_with('test_user')
        self.mock_db.get_user_from_db.assert_called_once_with('test_user')
        self.mock_group_api.sender.assert_called_once_with('test_user', 'Привет, Test!\nНажми кнопку "Поиск людей" для начала поиска пары', mock_get_matches_from_search)


if __name__ == '__main__':
    unittest.main()