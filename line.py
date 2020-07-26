import logging
import requests


class PushMessanger():
    def __init__(self, secret, token):
        self.secret = secret
        self.token = token

    def push(self, to, message):
        data = {
            'to': to,
            'messages': [{
                'type': 'text',
                'text': message
            }]
        }
        res = requests.post(
            'https://api.line.me/v2/bot/message/multicast',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.token}'
            },
            json=data
        )
        logging.info(data)
        res.raise_for_status()


class NotifyMessanger():
    def __init__(self, token):
        self.token = token

    def push(self, message):
        data = {'message': '\n' + message}
        res = requests.post(
            'https://notify-api.line.me/api/notify',
            headers={
                'Authorization': f'Bearer {self.token}'
            },
            data=data
        )
        logging.info(data)
        res.raise_for_status()
