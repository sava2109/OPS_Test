from aiogram import Bot, Dispatcher
import asyncio
from app.periodic_tests.periodic_checks_month import routine_checks_month
from app.periodic_tests.periodic_checks_hour import routine_checks_hour
import os
from dotenv import load_dotenv

from handlers.transaction_handler import router as transaction_router
from handlers.setup_handler import router as setup_router

from app.trx_state_machines.trx_state_machine import TRX_STATE_MACHINE, Trx_State_Machine

from app.periodic_tests.clicup_tickets import clickup_State_Machine
TRX_STATE_MACHINE = Trx_State_Machine()
CLICKUP_STATE_MACHINE = clickup_State_Machine()

async def main():
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN_DEV'))
    await asyncio.gather(
        run_bot(bot),
        run_trx_state_machine(bot),
        routine_checks_hour(bot),
        routine_checks_month(CLICKUP_STATE_MACHINE)
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