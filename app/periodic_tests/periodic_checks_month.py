import asyncio
from datetime import datetime,timedelta
async def routine_checks_month(CLICKUP_STATE_MACHINE):
    while True:
        try:
            print(f"Running monthly task at {datetime.now()}")
            await CLICKUP_STATE_MACHINE.update()
        except Exception as e:
            print(f"Error in monthly task: {e}")

        now = datetime.now()
        next_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        wait_time = (next_month - now).total_seconds()
        await asyncio.sleep(wait_time)