import os
import logging
import requests
import traceback

from flask import abort, jsonify

from line import PushMessanger, NotifyMessanger

# sco executive member's line group
EXECUTIVES = os.environ.get('EXECUTIVES')
# line api
CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')


def notify_missing_to_users(request):
    # notify if miss to register today -> user
    # using pushing API
    bq = BigQueryHandler()
    missing_users = bq.find_missing_users(n_days=1)

    push_messanger = PushMessanger(
        secret=CHANNEL_SECRET, token=CHANNEL_ACCESS_TOKEN)
    try:
        push_messanger.push(to=missing_users, message=_create_prompt_message())
    except Exception as e:
        # TODO: 管理者通知処理の追加
        logging.error(str(e))
        logging.info(traceback.format_exc())
        return abort(500)

    # notify if missing continues by 3 days -> operators
    # using line notify
    missing_users = bq.find_missing_users(n_days=3)
    notify_messanger = NotifyMessanger()
    try:
        notify_messanger.push(
            message=_create_notification_message())
    except Exception as e:
        # TODO: 管理者通知処理の追加
        logging.error(str(e))
        logging.info(traceback.format_exc())
        return abort(500)

    return jsonify({'message': 'ok'})


def alert_if_doubt(request):
    # alert if a user has records over 37.5 in the last week -> operators
    pass


def _create_prompt_message():
    return ""


def _create_notification_message():
    return ""
