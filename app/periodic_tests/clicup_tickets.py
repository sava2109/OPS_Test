import asyncio
from app.trx_state_machines import manual_request_state, auto_request_state
from app.external_connections.postgres import POSTGRES
class clickup_State_Machine:
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
        # first we need to remove "closed" contraint to get all tickets whatever their status
        # getting all tickets
        all_tickets = POSTGRES.get_all_tickets_v2()
        if all_tickets is None: return
        if len(all_tickets) < 1: return
        for ticket in all_tickets:
            await auto_request_state.check_trx(ticket_data=ticket, bot=self.bot)
            continue 

        # active_tickets = POSTGRES.get_all_tickets(closed=False)
        # if active_tickets is None: return
        # if len(active_tickets) < 1: return
        # for ticket in active_tickets:
        #     if ticket.manual == False:
        #         await auto_request_state.check_trx(ticket_data=ticket, bot=self.bot)
        #         continue
        #     elif ticket.manual == True:
        #         await manual_request_state.check_trx(ticket_data=ticket, bot=self.bot)
        #         continue


TRX_STATE_MACHINE = None