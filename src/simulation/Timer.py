import asyncio

class Timer:
    def __init__(self, network_running_step_time):
        self.now_time_seconds = 0
        self.network_running_step_time = network_running_step_time

    async def update_time(self):
        while True:
            self.now_time_seconds = self.now_time_seconds + self.network_running_step_time
            print(' ------- Timer: Network has running ' + str(self.now_time_seconds) + ' s. ------- ')
            await asyncio.sleep(1)

    def get_time(self):
        return self.now_time_seconds