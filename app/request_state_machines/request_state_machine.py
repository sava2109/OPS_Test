from aiogram.types import Message
import app.external_connections.ops_pa as ops_pa
from app.external_connections.postgres import POSTGRES, PostgresShop, PostgresApiKey

import app.request_state_machines.create_task.India.UPI as upi
import app.request_state_machines.create_task.India.IMPS as imps


# Check trx exists
async def run_state_machine(message: Message, transaction_id: str, shops: list[PostgresShop], message_full_text) -> bool:
    pg_answer = None
    shop = None
    for possible_shop in shops:
        shop_api_key = POSTGRES.get_shop_api_key(possible_shop.pg_api_key_id).pg_api_key
        pg_answer = await ops_pa.check_status(shop_api_key, transaction_id, message)
        if pg_answer is not None:
            shop = possible_shop
            break
    if shop is None:
        await message.reply("This transaction ID doesn't exists\nTry again with correct OPS transaction ID inside")
        return False

    match pg_answer.paymentMethod:
        case "UPI":
            return await upi.run_state(message, pg_answer, shop, message_full_text)
        case "IMPS":
            return await imps.run_state(message, pg_answer, shop, message_full_text)
    return False
