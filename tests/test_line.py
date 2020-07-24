import logging
import os
import unittest
from line import PushMessanger, NotifyMessanger

CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
DEVELOPER = os.environ.get('DEVELOPER')
NOTIFY_TOKEN = os.environ.get('NOTIFY_TOKEN')


class TestLineApi(unittest.TestCase):
    def test_push_message(self):
        push_messanger = PushMessanger(
            secret=CHANNEL_SECRET, token=CHANNEL_ACCESS_TOKEN)
        push_messanger.push(to=[DEVELOPER], message='this is test message.')

    def test_notify_message(self):
        notify_messanger = NotifyMessanger(token=NOTIFY_TOKEN)
        notify_messanger.push('this is test message for test notification.')


if __name__ == "__main__":
    unittest.main()
