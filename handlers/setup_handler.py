from aiogram import Router, types
from aiogram.filters import Command

import os

import utils.debugger
from app.external_connections.postgres import POSTGRES
from app.external_connections.xano import XANO_CLIENT

router = Router()

@router.message(Command("getchatid"))
async def get_chat_id(message: types.Message):
    user_id = int(os.getenv('SUPERADMIN_TG_ID'))

    if message.from_user.id != user_id:
        await message.answer(f'Access denied for {message.from_user.first_name}')
        return

    await message.answer(f'Chat id: {message.chat.id}\nHave easy setup, {message.from_user.first_name}')

@router.message(Command("addassignee"))
async def add_assignee(message: types.Message):
    user_id = int(os.getenv('SUPERADMIN_TG_ID'))

    if message.from_user.id != user_id:
        await message.answer(f'Access denied for {message.from_user.first_name}')
        return
    

    try:
        command_args = message.text.split()
        if len(command_args) < 2:
            await message.answer('Please provide a ClickUp ID. Usage: /addassignee <ClickUp ID>')
            return

        clickup_id = command_args[1]
        if POSTGRES.create_assignee(clickup_id=clickup_id):
            await message.answer(f'Assignee created with ClickUp ID: {clickup_id}')
        else:
            await message.answer('Failed to create assignee.')
    except Exception as e:
        await message.answer(f'Error: {str(e)}')

@router.message(Command("deleteassignee"))
async def delete_assignee(message: types.Message):
    user_id = int(os.getenv('SUPERADMIN_TG_ID'))

    if message.from_user.id != user_id:
        await message.answer(f'Access denied for {message.from_user.first_name}')
        return
    try:
        command_args = message.text.split()
        if len(command_args) < 2:
            await message.answer('Please provide a ClickUp ID. Usage: /deleteassignee <ClickUp ID>')
            return

        clickup_id = command_args[1]
        if POSTGRES.delete_assignee(clickup_id=clickup_id):
            await message.answer(f'Assignee deleted with ClickUp ID: {clickup_id}')
        else:
            await message.answer('Failed to delete assignee.')
    except Exception as e:
        await message.answer(f'Error: {str(e)}')
        
@router.message(Command("createapikey"))
async def createapikey(message: types.Message):
    utils.debugger.TIME_DEBUGGER.debug_time("start")
    POSTGRES.create_shop_api_key("1xbet_India", 0, "Ld0S5Egl2e5ERhPy7f54XHtpAlsAUY34")
    utils.debugger.TIME_DEBUGGER.debug_time("finish")

@router.message(Command("createshop"))
async def createshop(message: types.Message):
    utils.debugger.TIME_DEBUGGER.debug_time("start")
    POSTGRES.create_shop("1win", "1win_India", -1002149645514, 2)
    POSTGRES.create_shop("1xbet", "1xbet_India", -1002289834936, 3)
    utils.debugger.TIME_DEBUGGER.debug_time("finish")

@router.message(Command("createprovider"))
async def createprovider(message: types.Message):
    utils.debugger.TIME_DEBUGGER.debug_time("start")
    POSTGRES.create_provider("Pay2M", "UPI_701", 701, 901804306790, -1002278906788)
    utils.debugger.TIME_DEBUGGER.debug_time("finish")
