import requests

import json

from matplotlib import dates

import matplotlib.pyplot as plt

import datetime

import logging


class Zabbix:
    def __init__(self, user, password, url, host):
        self.user = user
        self.password = password
        self.url = url
        self.token = None
        self.id_ = 1
        self.state_auth = False
        self.host = host

    def logout(self):
        if not self.state_auth:
            return
        payload = {
            "jsonrpc": "2.0",
            "method": "user.logout",
            "params": [],
            "id": self.id_,
            "auth": self.token
        }
        answer = requests.post(url=self.url, json=payload)

        try:
            data = answer.json()
            if "result" not in data:
                exit(1)

        except json.JSONDecodeError:
            exit(1)

        self.id_ += 1
        self.state_auth = False

    def get_token(self):
        if self.state_auth:
            return

        payload = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.user,
                "password": self.password
            },
            "id": self.id_,
            "auth": None}
        answer = requests.post(url=self.url, json=payload)
        try:
            data = answer.json()
            if "result" not in data:
                logging.error(data)
                exit(1)
        except json.JSONDecodeError:
            exit(1)
        self.id_ += 1
        self.token = data['result']
        self.state_auth = True

    def __enter__(self):
        self.get_token()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()
        return

    def get_triggers_problem(self, ):
        payload = {
            "jsonrpc": "2.0",
            "method": "trigger.get",
            "params": {
                "output": ["triggerid"],  # ID triggers that with problem
                "host": self.host,
                "filter": {
                    "value": 1  # HAS PROBLEM
                }
            },
            "auth": self.token,
            "id": self.id_
        }

        answer = requests.post(url=self.url, json=payload)
        self.id_ += 1
        try:
            data = answer.json()
            if 'error' not in answer:
                return [item['triggerid'] for item in data["result"]]
        except json.JSONDecodeError:
            ...

        return []

    def get_items_for_trigger(self, triggers, name=False):
        payload = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "triggerids": triggers,
                "output": ["itemid", "name"] if name else "itemid",
            },
            "auth": self.token,
            "id": self.id_
        }

        answer = requests.post(url=self.url, json=payload)
        self.id_ += 1
        try:
            data = answer.json()
            if 'error' not in answer:
                if not name:
                    return [item['itemid'] for item in data["result"]]
                return [(item['itemid'], item['name']) for item in data["result"]]
        except json.JSONDecodeError:
            ...
        return []

#
#
    def get_history_item(self, item_id, type_="3", limit=30):
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
            "auth": self.token,
            "id": self.id_
        }

        self.id_ += 1
        answer = requests.post(url=self.url, json=payload)

        try:
            data = answer.json()
            if 'error' not in answer:
                return sorted(data['result'], key=lambda dct: int(dct['clock']))
        except json.JSONDecodeError:
            ...
        return []

    def get_type_for_item(self, item):
        payload = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": ["value_type"],
                "itemids": item,
            },
            "auth": self.token,
            "id": self.id_
        }
        self.id_ += 1
        answer = requests.post(url=self.url, json=payload)

        try:
            data = answer.json()
            if 'error' not in answer:
                return data['result'][-1]['value_type']
        except json.JSONDecodeError:
            ...
        return -100

    @staticmethod
    def convert_timestamp_to_datetime(timestamp_list):
        return [datetime.datetime.fromtimestamp(item, tz=None) for item in timestamp_list]

    @staticmethod
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
        return f"{name}.png"
