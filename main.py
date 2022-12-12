import requests

from api import *


# спарсить
# имя хоста поулчить
host = "Zabbix server"
zabbix_url_api = "http://127.0.0.1:80/api_jsonrpc.php"

item_id = 0

token = get_token(user="Admin", password="zabbix", url=zabbix_url_api)

trgs = [trg["triggerid"] for trg in get_triggers_problem(host, token, zabbix_url_api)]
print(trgs, "trgs")

items = [get_items_for_trigger(trg, token, zabbix_url_api)[0]["itemid"] for trg in trgs]
print(items, "items")

# items = ['28584', '28615']
hs = [get_history_item(item, token, zabbix_url_api) for item in items]
print(hs)

logout(token, url=zabbix_url_api)