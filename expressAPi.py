import sys

from api import *

if len(sys.argv) != 9:
    print("Недостаточно аргументов", file=sys.stderr)
    exit(-1)

event_source, \
    event_update_status, \
    event_value, \
    express_message, \
    express_send_to, \
    express_tags,\
    express_token, \
    express_url = sys.argv[1:]


# Ignore event_source because we use only triggers
# Ignore event_update_status
# What's mean express_tags?


def send_problem():
    try:
        url = express_url + "/api/v4/botx/notifications/direct"
        headers = {"Authorization": f"Bearer {express_token}",
                   "Content-Type": "application/json"}

        payload = {"group_chat_id": express_send_to,
                   "notification": {
                       "status": "ok",
                       "body": express_message,
                   }}
        req = requests.post(url, json=payload, headers=headers)
        if not req.ok:
            print(f"Возникла проблема с отправленным запросом: {req.text}", file=sys.stderr)
            exit(-1)
        return req.json()
    except requests.Timeout:
        print(f"Запрос не был отправлен по причине недоступности сервера", file=sys.stderr)
        exit(-1)


def send_recovery():
    ...


if __name__ == "__main__":
    if event_value == 1:  # It's a problem
        send_problem()
    elif event_value == 0:  # It's a recovery
        send_recovery()
