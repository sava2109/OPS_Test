from aiogram import Router, types
from aiogram.filters import Command

import os

import utils.debugger
from app.external_connections.postgres import POSTGRES
from app.external_connections.xano import XANO_CLIENT

router = Router()
@router.message(Command("test"))
async def test(message: types.Message):
    utils.debugger.TIME_DEBUGGER.debug_time("start")

    utils.debugger.TIME_DEBUGGER.debug_time("finish")
