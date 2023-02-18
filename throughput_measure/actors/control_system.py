import asyncio
import math

from throughput_measure.do_logging import log


class ControlSystem:
    def __init__(self, start_delay, max_response_time, stats, consumer_pool, delay=1):
        self.max_response_time = max_response_time
        self.stats = stats
        self.delay = delay
        self.consumer_pool = consumer_pool
        self.kill_sig = False
        self.start_delay = start_delay

    def _set_pool_size(self, percent_diff, previous_pool_size):
        pool_size = self.consumer_pool.get_pool_size()
        proposed_pool_size = pool_size * (1 + percent_diff)
        corrected_pool_size = max(math.floor((previous_pool_size + pool_size + proposed_pool_size) / 3 + 0.5), 1)

        self.consumer_pool.set_pool_size(corrected_pool_size)
        previous_pool_size = pool_size
        return previous_pool_size, corrected_pool_size

    def _set_delay(self, percent_diff, previous_delay):
        delay = self.consumer_pool.get_delay()
        proposed_delay = delay * (1 - percent_diff)
        corrected_delay = max(((previous_delay + delay + proposed_delay) / 3.0), 0.001)

        self.consumer_pool.set_delay(corrected_delay)
        previous_delay = delay

        return previous_delay, corrected_delay

    async def control(self):
        await asyncio.sleep(self.start_delay)
        stats = self.stats
        previous_pool_size = self.consumer_pool.get_pool_size()
        previous_delay = self.consumer_pool.get_delay()
        while not self.kill_sig:

            if stats:
                percent_diff = (self.max_response_time - stats['average_response_time']) / (
                        self.max_response_time + stats['average_response_time'])

                previous_pool_size, corrected_pool_size = self._set_pool_size(percent_diff, previous_pool_size)

                if previous_pool_size == corrected_pool_size == 1:
                    previous_delay, corrected_delay = self._set_delay(percent_diff, previous_delay)
                    log(f"Controlling: Pool Size 1. Delay {previous_delay} -> {corrected_delay} Response Time Diff: {percent_diff * 100}%. Expected {self.max_response_time}, Actual {stats['average_response_time']}")
                else:
                    log(f"Controlling: Pool Size {previous_pool_size} -> {corrected_pool_size}. Response Time Diff: {percent_diff * 100}%. Expected {self.max_response_time}, Actual {stats['average_response_time']}")

            await asyncio.sleep(self.delay)

    def kill(self):
        self.delay = 0
        self.kill_sig = True

    def set_delay(self, delay):
        self.delay = delay
