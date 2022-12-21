import os

from api import Zabbix

from base64 import b64encode

import requests

import logging

import sys

logging.basicConfig(filename="log.txt", filemode="a", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if len(sys.argv) != 13:
    logging.error("Недостаточное количество аргументов")
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
                   "Content-Type": "multipart/form-data"}

        payload = {"group_chat_id": express_send_to,
                   "notification": {
                       "status": "ok",
                       "body": express_message},
                   "file": {"file_name": name,
                            "data": f"data:image/png;base64,{b64encode(data).decode('ASCII')}"}
                   }

        req = requests.post(url, json=payload, headers=headers)

        if not req.ok:
            logging.error("Неудачный запрос")
            exit(-1)
        return req.json()
    except requests.Timeout:
        logging.error("Сервис botx недоступен")
        exit(-1)


# event_value = 1
# user = "Admin"
# password = "zabbix"
# url = "http://127.0.0.1:80/api_jsonrpc.php"
# host = "Zabbix server"
#


if __name__ == "__main__":

    try:
        if event_value == 1:  # It's a problem
            zb = Zabbix(user, password, url, host)
            with zb:
                trgs = zb.get_triggers_problem()
                if not trgs:
                    logging.info("Нет активных триггеров")
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
                msg = send_problem(filename)
                if msg['status'] == "ok":
                    logging.info(f"Сообщение отправлено и доставлено {msg}")
                else:
                    logging.error(f"Сообщение отправлено, но не доставлено  {msg}")
                if os.path.exists(filename):
                    os.remove(filename)
    except:
        logging.error("Возникла ошибка", exc_info=True)

