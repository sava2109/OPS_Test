import asyncio, datetime
from datetime import datetime, timedelta
from aiogram.types import ReactionTypeEmoji

from app.external_connections.postgres import POSTGRES, PostgresTicketRequest

from app.external_connections import ops_pa
from app.external_connections.ops_pa import PG_PAYMENT_TYPE, PG_TRX_STATUS
from app.external_connections.clickup import CLICKUP_CLIENT, CU_TaskStatus

async def check_trx(ticket_data: PostgresTicketRequest, bot) -> None:
    current_time = datetime.now()
    current_date = datetime.strptime(str(ticket_data.created_at), '%Y-%m-%d %H:%M:%S.%f')
    shop_data = POSTGRES.get_shop_by_id(ticket_data.shop_id)
    shop_api_key = POSTGRES.get_shop_api_key(shop_data.pg_api_key_id).pg_api_key
    pg_data = await ops_pa.check_status(shop_api_key=shop_api_key, trx_id=ticket_data.trx_id)
    print(pg_data)
    if pg_data == None:
        print(f"Couldn't check trx request: {ticket_data.id}")
        return
    
    if pg_data.state == PG_TRX_STATUS.COMPLETED.value:
        # Change DB Request status to CLOSE
        if not ticket_data.closed:
            db_patch_result = POSTGRES.close_ticket(ticket_data.id, True)
            if db_patch_result == False:
                print(f"AUTO_REQUEST_STATE: became completed, but didn't change in DB: {ticket_data.id}")

            # Answer in merchant chat
            await bot.set_message_reaction(chat_id=shop_data.support_chat_id, message_id=ticket_data.shop_message_id, reaction=[ReactionTypeEmoji(emoji="👍")])
            await bot.send_message(chat_id=shop_data.support_chat_id, text=f'New transaction status: COMPLETED\n\n{ticket_data.message_full_text}', reply_to_message_id=ticket_data.shop_message_id)
            # TASK: close clickup
            await CLICKUP_CLIENT.update_task_status(ticket_data.cu_task_id, CU_TaskStatus.COMPLETE)
        else :
            if current_date < current_time - timedelta(days=30) :
                POSTGRES.delete_old_ticket(ticket_data.id)
                print(f'ticket {ticket_data.cu_task_id} is closed for more than 30days ==> Deleted')
        return
    
    else:
        #when ticket was created and if it more then 1hour ago, do= > more cases
		# Check if the created_date is more than 1 hour ago and if the closed is false
        if current_date < current_time - timedelta(hours=1) and not ticket_data.closed :
            await CLICKUP_CLIENT.update_task_tag(ticket_data.cu_task_id)
            POSTGRES.activate_ticket_manual_tag(ticket_data.id)
        return
        
        #task more then 1 hour- change status to "manual" (mark in the database bool, put in cluck up tag "MANUAL" and assign Sergei to the task)
        #case 1: no replyies,  no reaction no reply ---ping message "CHECK"
        #case 2: provider says 'not our vpa,ugabuga...', forward for now new chat Egor Sergei and me
        #case 3: 