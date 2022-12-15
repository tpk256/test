
from api import *


# спарсить
# имя хоста поулчить
host = "Zabbix server"
zabbix_url_api = "http://127.0.0.1:80/api_jsonrpc.php"
name = "ping"
item_id = 0

token = get_token(user="Admin", password="zabbix", url=zabbix_url_api)
print(token)
trgs = [trg["triggerid"] for trg in get_triggers_problem(host, token, zabbix_url_api)]
print(trgs, "trgs")

items = [get_items_for_trigger(trg, token, zabbix_url_api, True)[0]["itemid"] for trg in trgs]
print(items, "items")

items_types = [(item, get_type_for_item(token, zabbix_url_api, item)[0]['value_type']) for item in items ]
print(items_types)
# items = ['28615']

hs = [get_history_item(item, token, zabbix_url_api, type_, ) for item, type_ in items_types]

for_gr = sorted(hs[0], key=lambda dct: int(dct['clock']))

x = []
y = []
for item in for_gr:
    x += [int(item['clock'])]
    y += [int(item['value'])]

x = convert_timestamp_to_datetime(x)
create_graph(x, y, "number_process")

# logout(token, url=zabbix_url_api)
