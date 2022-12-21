import os

from api import Zabbix

from expressAPi import *

import sys


if len(sys.argv) != 13:
    exit(-1)

event_source, \
    host, \
    user, \
    password, \
    url, \
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


def send_problem(name):
    try:
        with open(name, mode="rb") as f:
            data = f.read()

        url = express_url + "/api/v4/botx/notifications/direct"
        headers = {"Authorization": f"Bearer {express_token}",
                   "Content-Type": "application/json"}

        payload = {"group_chat_id": express_send_to,
                   "notification": {
                       "status": "ok",
                       "body": express_message,
                   }}
        req = requests.post(url, json=payload, headers=headers)

        multi_part = {"content": (f"{name}", f"{data}", "image/png"),
                      "group_chat_id": (None, express_send_to),
                      "meta": (None,
                               json.dumps({
                                   "duration": None,
                                   "caption": f"{name}"
                               }),
                               "application/json")

                      }
        url = express_url + "/api/v3/botx/files/upload"
        req = requests.post(url, files=multi_part, headers=headers)

        if not req.ok:
            exit(-1)
        return req.json()
    except requests.Timeout:
        exit(-1)


# event_value = 1
# user = "Admin"
# password = "zabbix"
# url = "http://127.0.0.1:80/api_jsonrpc.php"
# host = "Zabbix server"
#


if __name__ == "__main__":
    if event_value == 1:  # It's a problem
        zb = Zabbix(user, password, url, host)
        with zb:
            trgs = zb.get_triggers_problem()
            if not trgs:
                exit(0)

            items = {}
            for value in zb.get_items_for_trigger(trgs, name=True):
                if len(value) == 1:
                    items[value[0]] = []
                else:
                    items[value[0]] = [value[1]]
            for key in items:
                type_ = zb.get_type_for_item(key)
                items[key] += [type_]
            for key in items:
                history = zb.get_history_item(key, items[key][-1])

                values = sorted(history, key=lambda clk: clk['clock'])
                items[key] += [zb.convert_timestamp_to_datetime(int(item['clock']) for item in values)]
                items[key] += [[item['value'] for item in values]]

        for key in items:
            filename = "./" + zb.create_graph(items[key][-2], items[key][-1], items[key][0])
            send_problem(filename)

            if os.path.exists(filename):
                os.remove(filename)

