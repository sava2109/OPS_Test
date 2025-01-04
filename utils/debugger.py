from datetime import datetime


class TimeDebugger():
    def __init__(self):
        self.prevtime = datetime.now()

    def debug_time(self, message: str):
        delta = datetime.now() - self.prevtime
        print(f"{delta}: {message}")
        self.prevtime = datetime.now()


TIME_DEBUGGER = TimeDebugger()
