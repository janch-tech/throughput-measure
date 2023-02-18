import asyncio
from time import time

from throughput_measure.do_logging import log


class Cleaner:
    def __init__(self, queue, delay=1):
        self.queue = queue
        self.delay = delay
        self.kill_sig = False

    async def clean(self):
        cq = self.queue
        while not self.kill_sig:
            current_time = time()
            remove_count = 0
            while (
                    cq.qsize() and
                    cq.queue[0].get('time') < (current_time - 60)
            ):
                cq.get()
                remove_count += 1

            log(f"Cleaner: Removed {remove_count} from consumption queue. Now {self.queue.qsize()}")
            await asyncio.sleep(self.delay)

    def kill(self):
        self.delay = 0
        self.kill_sig = True

    def set_delay(self, delay):
        self.delay = delay
