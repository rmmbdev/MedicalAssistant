import requests


class BotHandler:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def send_message_with_keyboard(self, chat_id, text, keyboard):
        params = {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': keyboard,
        }
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp
