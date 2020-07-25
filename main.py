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
# how many days required to notify when user forget to record body temp.
N_DAYS_NOTIFY_TO_USER = os.environ.get('N_DAYS_NOTIFY_TO_USER')
N_DAYS_NOTIFY_TO_EXECUTIVES = os.environ.get('N_DAYS_NOTIFY_TO_EXECUTIVES')


def notify_missing_to_users(request):
    # notify if miss to register -> user
    # using pushing API
    bq = BigQueryHandler()
    missing_users = bq.find_missing_users(n_days=N_DAYS_NOTIFY_TO_USER)
    missing_user_ids = [u['id'] for u in missing_users]

    push_messanger = PushMessanger(
        secret=CHANNEL_SECRET, token=CHANNEL_ACCESS_TOKEN)
    try:
        if len(missing_user_ids) > 0:
            push_messanger.push(to=missing_user_ids,
                                message=_create_prompt_message())
    except Exception as e:
        # TODO: 管理者通知処理の追加
        logging.error(str(e))
        logging.info(traceback.format_exc())
        return abort(500)

    # notify if missing continues in several days -> executives
    # using line notify
    missing_users = bq.find_missing_users(n_days=N_DAYS_NOTIFY_TO_EXECUTIVES)
    notify_messanger = NotifyMessanger()
    try:
        if len(missing_users) > 0:
            notify_messanger.push(
                message=_create_notification_message(missing_users))
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
    return "おはようございます。昨日の体温測定をお忘れでは無いでしょうか？今日は忘れないうちに登録のほど、よろしくお願いいたします！"


def _create_notification_message(users):
    msg = f"[報告]下記の方は{N_DAYS_NOTIFY_TO_EXECUTIVES}日連続で体温記録を実施していません。\n"
    for user in users:
        msg += f"- {user} さん\n"
    return msg
