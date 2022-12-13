import requests
from matplotlib import dates

import matplotlib.pyplot as plt

import numpy as np

import datetime

id_ = 1
# Todo переделать почеловечески,а то как-то костыльно


def increment_id():
    global id_
    id_ += 1


def get_token(user, password, url) -> str:
    payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": user,
            "password": password
        },
        "id": id_,
        "auth": None}
    answer = requests.post(url=url, json=payload).json()
    increment_id()
    if 'error' not in answer:
        return answer['result']
    print(answer)
    exit(-1)


def logout(token, url):

    payload = {
            "jsonrpc": "2.0",
            "method": "user.logout",
            "params": [],
            "id": id_,
            "auth": token
        }
    answer = requests.post(url=url, json=payload).json()
    increment_id()
    if 'error' not in answer:
        return answer['result']
    print(answer)


def get_history(host, token, url):
    # add itemsids
    payload = {
            "jsonrpc": "2.0",
            "method": "history.get",
            "params": {
                "output": "extend",
                "history": 0,
                "limit": 10,
                "search": {
                    "host": host,
                    "Key": "agent.ping"
                }
            },
            "auth": token,
            "id": id_
        }
    increment_id()
    answer = requests.post(url=url, json=payload).json()

    if 'error' not in answer:
        return answer
    print(answer)


def get_triggers_problem(host, token, url, desc=False):
    payload = {
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            "output": ["triggerid", "description"] if desc else "triggerid",  # ID triggers that with problem
            "host": host,
            "filter": {
                "value": 1  # HAS PROBLEM
            }
        },
        "auth": token,
        "id": id_
    }
    increment_id()
    answer = requests.post(url=url, json=payload).json()

    if 'error' not in answer:
        return answer["result"]
    print(answer)


def get_items_for_trigger(trigger, token, url, name=False):
    payload = {
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "triggerids": trigger,
            "output": ["itemid", "name"] if name else "itemid",
        },
        "auth": token,
        "id": id_
    }
    increment_id()
    answer = requests.post(url=url, json=payload).json()
    if 'error' not in answer:
        return answer["result"]
    print(answer)


def get_history_item(item_id, token, url, type_=3, limit=100):
    payload = {
        "jsonrpc": "2.0",
        "method": "history.get",
        "params": {
            "output": "extend",
            "history": type_,
            "itemids": item_id,
            "sortfield": "clock",
            "sortorder": "DESC",
            "limit": limit
        },
        "auth": token,
        "id": id_
    }

    increment_id()
    answer = requests.post(url=url, json=payload).json()

    if 'error' not in answer:
        return answer['result']
    print(answer)


def get_type_for_item(token, url,  item):
    payload = {
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "output": ["value_type"],
            "itemids": item,
        },
        "auth": token,
        "id": id_
    }
    increment_id()
    answer = requests.post(url=url, json=payload).json()

    if 'error' not in answer:
        return answer['result']
    print(answer)


def convert_timestamp_to_datetime(timestamp_list):
    return [datetime.datetime.fromtimestamp(item, tz=None) for item in timestamp_list]


def create_graph(x, y, name):
    fmt = dates.DateFormatter('%d-%H:%M')
    fig, ax = plt.subplots()

    plt.title(f"График изменения {name}")
    plt.xlabel("Datetime")
    plt.ylabel("Values")
    ax.grid()

    ax.plot(x, y, "-o")
    ax.xaxis.set_major_formatter(fmt)
    fig.autofmt_xdate()

    fig.savefig(f"{name}.png")
