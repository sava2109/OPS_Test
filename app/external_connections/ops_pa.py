from enum import Enum

import requests
import json
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

async def check_status(shop_api_key:str, trx_id:str) -> PGAnswer | None:
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

        
    else:
        answer = None
    return answer