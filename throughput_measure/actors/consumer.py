import asyncio
from time import time

from throughput_measure.do_logging import log


class Consumer:
    def __init__(self, job_queue, consumption_queue, consumer_id, delay):
        self.consumer_id = consumer_id
        self.job_queue = job_queue
        self.consumption_queue = consumption_queue
        self.kill_sig = False
        self.delay = delay
        self.is_enabled = False

    async def consume(self):
        while not self.kill_sig:
            if self.is_enabled:
                item = await self.job_queue.get()
                start_time = time()
                await item()
                enqueue_item = {'time': time(), 'response_time': (time() - start_time)}
                self.consumption_queue.put(enqueue_item)
                log(f"Consumer {self.consumer_id}: status {enqueue_item}")
            await asyncio.sleep(self.delay)

    def kill(self):
        self.delay = 0
        self.kill_sig = True

    def set_delay(self, delay):
        self.delay = delay

    def enable(self):
        log(f"Consumer {self.consumer_id} is being enabled")
        self.is_enabled = True

    def disable(self):
        log(f"Consumer {self.consumer_id} is being disabled")
        self.is_enabled = False
