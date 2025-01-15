from aiogram.types import Message, ReactionTypeEmoji

from app.external_connections.ops_pa import PGAnswer, PG_PAYMENT_TYPE, PG_TRX_STATUS
from app.external_connections.postgres import POSTGRES, PostgresShop
import app.request_state_machines.create_task.India.UPI_IMPS_701 as apm701
import app.request_state_machines.create_task.India.UPI_IMPS_666 as apm666
async def run_state(message: Message, trx_details: PGAnswer, shop: PostgresShop, message_full_text:str) -> bool:
    match trx_details.state:
        case PG_TRX_STATUS.COMPLETED.value:
            return await state_COMPLETED(message=message, trx_details=trx_details, shop=shop, message_full_text=message_full_text)
        case PG_TRX_STATUS.DECLINED.value:
            return await state_DECLINED(message=message, trx_details=trx_details, shop=shop, message_full_text=message_full_text)
        case PG_TRX_STATUS.CANCELLED.value:
            return await state_CANCELLED(message=message, trx_details=trx_details, shop=shop, message_full_text=message_full_text)
        case PG_TRX_STATUS.CHECKOUT.value:
            return await state_CHECKOUT(message=message, trx_details=trx_details, shop=shop, message_full_text=message_full_text)
        case PG_TRX_STATUS.AWAITING_WEBHOOK.value:
            return await state_AWAITING_WEBHOOK(message=message, trx_details=trx_details, shop=shop, message_full_text=message_full_text)
        case PG_TRX_STATUS.AWAITING_REDIRECT.value:
            return await state_AWAITING_REDIRECT(message=message, trx_details=trx_details, shop=shop, message_full_text=message_full_text)
        case PG_TRX_STATUS.PENDING.value:
            return await state_PENDING(message=message, trx_details=trx_details, shop=shop, message_full_text=message_full_text)
    print(f"UPI. Trx {trx_details.trx_id} has undetectable state: {trx_details.state}")
    return False

async def state_COMPLETED(message: Message, trx_details: PGAnswer, shop: PostgresShop, message_full_text:str) -> bool:
    await message.react(reaction=[ReactionTypeEmoji(emoji="👍")])
    await message.reply("""Transaction status: COMPLETED. \n
                        Статус транзакции: COMPLETED""")
    return True
async def state_DECLINED(message: Message, trx_details: PGAnswer, shop: PostgresShop, message_full_text:str) -> bool:
    terminal_id = trx_details.terminal.split('_')[-1]
    match int(terminal_id):
        case 666:
            success = await apm666.beh_send_auto_ticket(message, trx_details, shop, message_full_text)
            return success
        case 701:
            success = await apm701.beh_send_auto_ticket(message, trx_details, shop, message_full_text)
            return success
    print(f"Terminal: {terminal_id}. Not found in states")

async def state_PENDING(message: Message, trx_details: PGAnswer, shop: PostgresShop, message_full_text:str) -> bool:
    terminal_id = trx_details.terminal.split('_')[-1]
    match int(terminal_id):
        case 666:
            success = await apm666.beh_send_auto_ticket(message, trx_details, shop, message_full_text)
            return success
        case 701:
            success = await apm701.beh_send_auto_ticket(message, trx_details, shop, message_full_text)
            return success
    print(f"Terminal: {terminal_id}. Not found in states")
async def state_CANCELLED(message: Message, trx_details: PGAnswer, shop: PostgresShop, message_full_text:str) -> bool:
    await message.reply("""Transaction status: CANCELLED.\n
                        The specified transaction by this ID had not gone to the bank and had been closed\n
                        May you doublecheck transaction ID and send NEW ticket request pls \n
                        Статус транзакции: "CANCELLED"\n
                        Указанная транзакция по данному ID не поступила в банк и была закрыта\n
                        Перепроверьте, пожалуйста, ID транзакции и отправьте НОВЫЙ запрос""")
    return True
async def state_CHECKOUT(message: Message, trx_details: PGAnswer, shop: PostgresShop, message_full_text:str) -> bool:
    await message.reply("""Transaction status: CHECKOUT.\n
                    The specified transaction by this ID has not gone to the bank yet\n
                        May you doublecheck transaction ID and send NEW ticket request pls \n
                        Статус транзакции: "CHECKOUT"\n
                        Указанная транзакция по данному ID еще не поступила в банк\n
                        Перепроверьте, пожалуйста, ID транзакции и отправьте НОВЫЙ запрос""")
    return True
async def state_AWAITING_WEBHOOK(message: Message, trx_details: PGAnswer, shop: PostgresShop, message_full_text:str) -> bool:
    terminal_id = trx_details.terminal.split('_')[-1]
    match int(terminal_id):
        case 666:
            success = await apm666.beh_send_auto_ticket(message, trx_details, shop, message_full_text)
            return success
        case 701:
            success = await apm701.beh_send_auto_ticket(message, trx_details, shop, message_full_text)
            return success
    print(f"Terminal: {terminal_id}. Not found in states")
async def state_AWAITING_REDIRECT(message: Message, trx_details: PGAnswer, shop: PostgresShop, message_full_text:str) -> bool:
    print(f"UPI. Trx {trx_details.trx_id} came with unsolved state: {trx_details.state}")
    return True