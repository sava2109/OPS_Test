from aiogram import Bot, Dispatcher
import asyncio
from datetime import datetime

import os
from dotenv import load_dotenv

from handlers.transaction_handler import router as transaction_router
from handlers.setup_handler import router as setup_router

from app.trx_state_machines.trx_state_machine import TRX_STATE_MACHINE, Trx_State_Machine
from app.periodic_tests.ticket_reaction_reply import check_pending_messages
from app.periodic_tests.terminal_balance import check_balance
TRX_STATE_MACHINE = Trx_State_Machine()
async def routine_checks(bot):

    while True:
        try:
            print(f"Running hourly task at {datetime.now()} of Checking Tickets, bot Messages , Terminal Balances")
            TRX_STATE_MACHINE.update()
            await check_pending_messages(bot)
            await check_balance(bot)
        except Exception as e:
            print(f"Error in hourly task: {e}")
        now = datetime.now()
        next_hour = now.replace(minute=0, second=0, microsecond=0)
        if now >= next_hour:
            next_hour = next_hour.replace(hour=next_hour.hour + 1)
        
        wait_time = (next_hour - now).total_seconds()
        await asyncio.sleep(wait_time)
async def main():
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN_DEV'))
    await asyncio.gather(
        run_bot(bot),
        run_trx_state_machine(bot),
        routine_checks(bot)
    )
async def run_bot(bot):
    dp = Dispatcher()
    # Register routers
    dp.include_routers(setup_router,
                       transaction_router)
    await dp.start_polling(bot)
async def run_trx_state_machine(bot):
    
    await TRX_STATE_MACHINE.start_polling(bot, polling_timeout=120)

if __name__ == "__main__":
    asyncio.run(main())