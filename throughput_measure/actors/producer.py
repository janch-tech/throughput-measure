import asyncio
import random

from throughput_measure.do_logging import log


class Producer:
    def __init__(self, queue, count, source_config, delay):
        self.count = count
        self.delay = delay
        self.queue = queue
        self.kill_sig = False
        self.source_config = source_config

    async def produce(self):
        while not self.kill_sig:
            jobs = self.queue

            if jobs.qsize() < self.count / 2:
                while jobs.qsize() < self.count:
                    rand_number = random.random()
                    for k, v in self.source_config.items():
                        if rand_number < v['probability']:
                            jobs.put_nowait(v['function'])
                        else:
                            pass
                log(f"Producer: Job Queue {jobs.qsize()}")
            await asyncio.sleep(self.delay)

    def kill(self):
        self.delay = 0
        self.kill_sig = True

    def set_delay(self, delay):
        self.delay = delay
