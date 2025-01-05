from aiogram import Router
from aiogram.types import Message, ReactionTypeEmoji

from utils.debugger import TIME_DEBUGGER
from utils.validators import validate_transaction_id

import app.request_state_machines.request_state_machine as state_machine

from app.external_connections.postgres import POSTGRES, PostgresShop

router = Router()

@router.message()
async def detect_message(message: Message):
    TIME_DEBUGGER.debug_time("start")
    # try:
    raw_text = None
    if message.caption != None:
        raw_text = str(message.caption)
    elif message.text != None:
        raw_text = str(message.text)
    if raw_text == None:
        return
    paragraphs = raw_text.split("\n")
    transaction_id = None
    for paragraph in paragraphs:
        texts = paragraph.split(" ")
        for text in texts:
            if validate_transaction_id(text):
                transaction_id = text
                break

    if transaction_id == None:
        return

    # Checker: is chat register
    shops_answer:list[PostgresShop] = POSTGRES.get_shops_by_support_chat_id(message.chat.id)
    if shops_answer == None:
        return
    if len(shops_answer) < 1:
        return
    # Run Request state analizator
    print(message)
    state_machine_success = await state_machine.run_state_machine(message, transaction_id, shops_answer, raw_text)
    if state_machine_success == False:
        print(f"State machine: FALSE. Chat: {message.chat.id}, Trx_id: {transaction_id}")
        return
    TIME_DEBUGGER.debug_time("finish")