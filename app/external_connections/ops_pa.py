from enum import Enum

import requests
import json
from app.external_connections.postgres import POSTGRES
from requests.exceptions import RequestException
from aiogram.types import Message
class PG_TRX_STATUS(Enum):
    COMPLETED = "COMPLETED"
    DECLINED = "DECLINED"
    CHARGEBACK = "CHARGEBACK"
    CANCELLED = "CANCELLED"
    CHECKOUT = "CHECKOUT"
    PENDING = "PENDING"
    AWAITING_WEBHOOK = "AWAITING_WEBHOOK"
    AWAITING_REDIRECT = "AWAITING_REDIRECT"
class PG_PAYMENT_TYPE(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    REFUND = "REFUND"
    CHARGEBACK = "CHARGEBACK"

class PGAnswer:
    def __init__(self, trx_id:str=None,
                 state:str=None, paymentType:str=None, paymentMethod:str=None,
                 terminal:str=None):
        self.trx_id = trx_id
        self.state = state
        self.paymentType = paymentType
        self.paymentMethod = paymentMethod
        self.terminal = terminal

def check_balance(shop_api_key: str, terminal_name: str, threshold = 100) -> None:
   
    if not shop_api_key or not terminal_name:
        return None

    try:
        terminal_id = POSTGRES.get_provider_by_terminal_name(terminal_name)
        if not terminal_id:
            return None

        url = f"https://app.inops.net/api/v1/terminals/getBalance/{terminal_id}"
        headers = {
            'Authorization': f'Bearer {shop_api_key}',
        }

        response = requests.get(
            url=url,
            headers=headers,
        )

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            return None

        status = int(data.get('status', 0))
        
        if status == 200:
            try:
                balance = data['result']['balance']['amount']
                return balance <= threshold
            except KeyError as e:
                return None
        else:
            error_message = data.get('message', 'Unknown error')
            return None

    except RequestException as e:
        print(error_message)
        return None
    except Exception as e:
        return None

async def check_status(shop_api_key:str, trx_id:str, message : Message) -> PGAnswer | None:
    if shop_api_key == None:
        return None
    url = f"https://app.inops.net/api/v1/payments/{trx_id}"
    payload = ""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {shop_api_key}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data_raw = response.text
    
    data = json.loads(data_raw)
    status = int(data['status'])
    if status == 200:
        answer = PGAnswer(trx_id=data['result']['id'],
                          state=data['result']['state'],
                          paymentType=data['result']['paymentType'],
                          paymentMethod=data['result']['paymentMethod'],
                          terminal=data['result']['terminalName'])
        if check_balance(shop_api_key=shop_api_key,terminal_name=data['result']['terminalName']):
            await message.reply('Terminal Balance is Low (Below 100)')
        
    else:
        answer = None
    return answer