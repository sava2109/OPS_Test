import os, json
from datetime import datetime
from typing import Any

import requests
from dotenv import load_dotenv


class XanoShop:
    def __init__(self, id: int = None, merchant_id: int = None, management_chat: str = None, support_chat: str = None, api_key:str=None):
        self.id = id
        self.merchant_id = merchant_id
        self.management_chat = management_chat
        self.support_chat = support_chat
        self.api_key = api_key
class XanoProvider:
    def __init__(self, id: int = None, provider_name: int = None, terminal_name: str = None,
                 list_id_clickup: str = None, support_chat_id_tg: str = None):
        self.id = id
        self.provider_name = provider_name
        self.terminal_name = terminal_name
        self.list_id_clickup = list_id_clickup
        self.support_chat_id_tg = support_chat_id_tg
class XanoTrxRequest:
    def __init__(self, id: int = None, shop_id: int = None, provider_id: int = None, pg_id: int = None,
                 trx_id: str = None,
                 task_id_click_up: str = None,
                 provider_support_chat_id: int = None, provider_message_id: int = None,
                 shop_support_chat_id: int = None, shop_message_id: int = None,
                 closed: bool = None, manual: bool = None, created_at: datetime = None, shop_api_key:str = None, message_full_text:str = None):
        self.id = id
        self.shop_id = shop_id
        self.provider_id = provider_id
        self.pg_id = pg_id
        self.trx_id = trx_id
        self.task_id_click_up = task_id_click_up
        self.provider_support_chat_id = provider_support_chat_id
        self.provider_message_id = provider_message_id
        self.shop_support_chat_id = shop_support_chat_id
        self.shop_message_id = shop_message_id
        self.closed = closed
        self.manual = manual
        self.created_at = created_at
        self.shop_api_key = shop_api_key
        self.message_full_text = message_full_text

class XanoClient:
    def __init__(self):
        load_dotenv()
        self.email = os.getenv('XANO_EMAIL')
        self.password = os.getenv('XANO_PASS')
        self.base_url = os.getenv('XANO_ENDPOINT')
        self.auth()

    def get_shop_by_id(self, shop_id: str) -> XanoShop | None:
        url = f"{self.base_url}/shops/{shop_id}/shopbyid"
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token
        }
        payload = {
            "shops_id": shop_id
        }

        response = requests.get(url, json=payload, headers=headers)
        # Check XANO auth
        if response.status_code == 401:
            self.auth()
            return self.get_shop_by_id(shop_id=shop_id)
        if response.status_code == 429:
            print("Request: shop by id. Too many requests")
            return None
        if response.status_code != 200:
            return None
        else:
            data = response.json()
            shop = XanoShop(id=data['id'],
                            merchant_id=data['merchant_id'],
                            support_chat=data['support_chat_id'],
                            management_chat=data['management_chat_id'],
                            api_key=data['api_key']
                            )
            return shop
    def get_shop_API_key(self, shop_id: str) -> Any | None:
        url = f"{self.base_url}/shops/{shop_id}/apikey"

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token
        }
        payload = {
            "shops_id": shop_id
        }

        response = requests.get(url, json=payload, headers=headers)
        # Check XANO auth
        if response.status_code == 401:
            self.auth()
            return self.get_shop_API_key(shop_id=shop_id)
        if response.status_code == 429:
            print("Request: shop API key. Too many requests")
            return None
        if response.status_code != 200:
            return None
        else:
            data = response.json()
            return data['api_key']
    def get_shops_by_support_chat_id(self, chat_id: str) -> list[XanoShop] | None:
        url = f"{self.base_url}/shops/{chat_id}/"
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token
        }
        payload = {
            "support_chat_id": chat_id
        }

        response = requests.get(url, data=json.dumps(payload), headers=headers)
        # Check XANO auth
        if response.status_code == 401:
            self.auth()
            return self.get_shops_by_support_chat_id(chat_id=chat_id)
        if response.status_code == 429:
            print("Request: shop by support chat id. Too many requests")
            return None
        if response.status_code != 200:
            return None
        else:
            data = response.json()
            answer_array = []
            for item in data:
                try:
                    shop = XanoShop(id=item.get('id'),
                                    merchant_id=item.get('merchant_id'),
                                    support_chat=item.get('support_chat'),
                                    management_chat=item.get('management_chat'),
                                    api_key=item.get('api_key')
                                    )
                    answer_array.append(shop)
                except Exception as e:
                    print(f"Xano shops list Parsing answer error: {e}")
                    return None
            return answer_array

    def get_provider_by_terminal_name(self, terminal_name: int) -> XanoProvider | None:
        url = f"{self.base_url}/provider/{terminal_name}/"

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token
        }
        payload = {
            "provider_terminal_name": terminal_name
        }

        response = requests.get(url, json=payload, headers=headers)
        # Check XANO auth
        if response.status_code == 401:
            self.auth()
            return self.get_provider_by_terminal_name(shop_id=terminal_name)

        if response.status_code == 429:
            print("Request: provider by terminal. Too many requests")
            return None

        if response.status_code != 200:
            return None
        else:
            data = response.json()
            answer = XanoProvider(id=data['id'],
                                  provider_name=data['provider_name'],
                                  terminal_name=data['terminal_name'],
                                  list_id_clickup=data['list_id_clickup'],
                                  support_chat_id_tg=data['support_chat_id_tg'], )
            return answer

    def get_merchants_list(self):
        url = f"{self.base_url}/merchant"

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token
        }
        payload = {}

        response = requests.get(url, json=payload, headers=headers)

        if response.status_code == 401:
            self.auth()
            self.get_merchants_list()
            return
        if response.status_code == 429:
            print("Request: merchants list. Too many requests")
            return None
        data_raw = response.text
        print(data_raw)
        return


    def get_trx_requests(self) -> list[XanoTrxRequest] | None:
        url = f"{self.base_url}/trxrequests/getallactive"
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token
        }
        payload = {}

        response = requests.get(url, json=payload, headers=headers)
        # Check XANO auth
        if response.status_code == 401:
            self.auth()
            return self.get_trx_requests()
        if response.status_code == 429:
            print("Request: trx requests. Too many requests")
            return None
        if response.status_code != 200:
            return None

        data = response.json()
        answer_array = []
        for item in data:
            try:
                trx_requests = XanoTrxRequest(id=item.get('id'),
                                              shop_id=item.get('shop_id'),
                                              provider_id=item.get('provider_id'),
                                              pg_id=item.get('pg_id'),
                                              trx_id=item.get('trx_id'),
                                              task_id_click_up=item.get('task_id_click_up'),
                                              provider_support_chat_id=item.get('provider_support_chat_id'),
                                              provider_message_id=item.get('provider_message_id'),
                                              shop_support_chat_id=item.get('shop_support_chat_id'),
                                              shop_message_id=item.get('shop_message_id'),
                                              closed=item.get('Closed'),
                                              manual=item.get('ManualTicket'),
                                              created_at=item.get('created_at'),
                                              shop_api_key=item.get('shop_api_key'),
                                              message_full_text=item.get('message_full_text')
                                              )
                answer_array.append(trx_requests)
            except Exception as e:
                print(f"Xano shops list Parsing answer error: {e}")
                return None
        return answer_array
    def post_new_trx_request(self, trx_id: str, shop_data: XanoShop, merch_mes_id:int, provider_data: XanoProvider, provider_mes_id: int, task_id_ca: str,
                             is_manual_ticket: bool, message_full_text: str) -> bool:
        url = f"{self.base_url}/trxrequests"

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token
        }
        payload = {
            "shop_id": shop_data.id,
            "provider_id": provider_data.id,
            "pg_id": 0,
            "trx_id": trx_id,
            "task_id_click_up": task_id_ca,
            "provider_support_chat_id": provider_data.support_chat_id_tg,
            "provider_message_id": provider_mes_id,
            "shop_support_chat_id": shop_data.support_chat,
            "shop_message_id": merch_mes_id,
            "Closed": False,
            "ManualTicket": is_manual_ticket,
            "shop_api_key": shop_data.api_key,
            "message_full_text": message_full_text
        }

        response = requests.post(url, json=payload, headers=headers)
        # Check XANO auth
        if response.status_code == 401:
            self.auth()
            return self.post_new_trx_request(trx_id=trx_id, shop_data=shop_data, merch_mes_id=merch_mes_id, provider_data=provider_data, provider_mes_id=provider_mes_id, task_id_ca=task_id_ca, is_manual_ticket=is_manual_ticket)
        if response.status_code == 429:
            print("Request: post new trx request. Too many requests")
            return False
        return response.status_code == 200
    def patch_trx_request(self, trx_data: XanoTrxRequest) -> bool:
        url = f"{self.base_url}/trxrequests/{trx_data.id}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token
        }
        payload = {
            "shop_id": trx_data.shop_id,
            "provider_id": trx_data.provider_id,
            "pg_id": trx_data.pg_id,
            "trx_id": trx_data.trx_id,
            "task_id_click_up": trx_data.task_id_click_up,
            "provider_support_chat_id": trx_data.provider_support_chat_id,
            "provider_message_id": trx_data.provider_message_id,
            "shop_support_chat_id": trx_data.shop_support_chat_id,
            "shop_message_id": trx_data.shop_message_id,
            "Closed": trx_data.closed,
            "ManualTicket": trx_data.manual,
            "shop_api_key": trx_data.shop_api_key,
            "message_full_text": trx_data.message_full_text
        }

        response = requests.patch(url, json=payload, headers=headers)
        # Check XANO auth
        if response.status_code == 401:
            self.auth()
            return self.patch_trx_request(trx_data)
        if response.status_code == 429:
            print("Request: edit trx request. Too many requests")
            return False
        return response.status_code == 200

    def auth(self):
        url = f"{self.base_url}/auth/login"

        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "email": self.email,
            "password": self.password
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data_raw = response.text
            data = json.loads(data_raw)
            self.token = data['authToken']
        else:
            print("XANO: Can't do auth")
            self.token = None

XANO_CLIENT = XanoClient()
