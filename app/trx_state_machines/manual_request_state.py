from app.external_connections.postgres import POSTGRES, PostgresTicketRequest

from app.external_connections import ops_pa, clickup
from app.external_connections.ops_pa import PG_PAYMENT_TYPE, PG_TRX_STATUS
from app.external_connections.clickup import CU_TaskStatus

async def check_trx(ticket_data: PostgresTicketRequest, bot) -> None:
    return