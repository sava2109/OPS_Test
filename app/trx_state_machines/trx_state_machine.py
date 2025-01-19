import asyncio
from app.trx_state_machines import manual_request_state, auto_request_state
from app.external_connections.postgres import POSTGRES
class Trx_State_Machine:
    def __init__(self):
        self.polling_timeout = None
        self.active_session = True
        self.bot = None
    async def start_polling(self, bot, polling_timeout: int = 10) -> None:
        self.bot = bot
        self.polling_timeout = polling_timeout
        await self.run_polling()
        return None
    async def stop_polling(self) -> None:
        self.active_session = False

    async def run_polling(self) -> None:
        try:
            while self.active_session:
                await self.update()
                await asyncio.sleep(self.polling_timeout)
        finally:
            print("Trx state machine Polling stopped by error")
            await self.emit_shutdown()
        return

    async def emit_shutdown(self) -> None:
        return

    async def update(self) -> None:

        all_tickets = POSTGRES.get_all_tickets_v2()
        if all_tickets is not None and len(all_tickets) > 1:
            for ticket in all_tickets:
                if ticket.manual == False:
                    await auto_request_state.check_trx(ticket_data=ticket, bot=self.bot)
                    continue
                elif ticket.manual == True:
                    await manual_request_state.check_trx(ticket_data=ticket, bot=self.bot)
                    continue
        else:
            return



TRX_STATE_MACHINE = None