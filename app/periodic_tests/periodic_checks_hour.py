import asyncio
from datetime import datetime,timedelta
from app.periodic_tests.terminal_balance import check_balance
async def routine_checks_hour(bot):
    while True:
        try:
            print(f"Running hourly task at {datetime.now()}")
            await check_balance(bot)
        except Exception as e:
            print(f"Error in hourly task: {e}")

        now = datetime.now()
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        wait_time = (next_hour - now).total_seconds()
        await asyncio.sleep(wait_time)
