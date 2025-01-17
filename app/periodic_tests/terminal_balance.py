
import requests
import json
from app.external_connections.postgres import POSTGRES
from requests.exceptions import RequestException

async def check_balance(bot) -> dict:
   threshold = 100000
   results = {}

   try:
       terminals = POSTGRES.get_all_terminals()
       if not terminals:
           return {}

       for terminal_id, api_key,id in terminals:
           url = f"https://app.inops.net/api/v1/terminals/getBalance/{terminal_id}"
           headers = {
               'Authorization': f'Bearer {api_key}',
           }
           try:
               response = requests.get(
                   url=url,
                   headers=headers,
                   timeout=30
               )

               try:
                   data = response.json()
                   status = int(data.get('status', 0))
                   if status == 200:
                        balance = data['result'][0]['balance']['amount']
                        chat_id = POSTGRES.get_chat_id(id=id)
                        if balance< threshold:
                            await bot.send_message(
                            chat_id=chat_id,
                            text=f"terminal with ID {terminal_id} has low balance : {balance}",
                            
                            )
                        else:
                            print(balance, 'balance is above threshold')
                   else:
                       error_message = data.get('message', 'Unknown error')
                       print(error_message)
                       results[terminal_id] = {
                           'error': f'API Error: {error_message}'
                       }

               except json.JSONDecodeError:
                   results[terminal_id] = {
                       'error': 'Invalid JSON response'
                   }

           except RequestException as e:
               results[terminal_id] = {
                   'error': f'Request failed: {str(e)}'
               }
           except Exception as e:
               results[terminal_id] = {
                   'error': f'Unexpected error: {str(e)}'
               }



   except Exception as e:
       print(f"Fatal error checking balances: {e}")
       return {}