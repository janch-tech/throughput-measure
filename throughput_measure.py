import asyncio
import math
import queue
import random
from do_logging import log
from time import time


job_queue = asyncio.Queue()
consumption_queue = queue.Queue()
statistics = {}
CONSUME_DELAY_IN_MILLIS = 1000.0
CONSUMER_COUNT = 10


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


class Consumer:
    def __init__(self, queue, consumer_id, delay):
        self.consumer_id = consumer_id
        self.queue = queue
        self.kill_sig = False
        self.delay = delay
        self.is_enabled = False

    async def consume(self):
        while not self.kill_sig:
            if self.is_enabled:
                item = await job_queue.get()
                start_time = time()
                await item()
                enqueue_item = {'time': time(), 'response_time': (time() - start_time)}
                consumption_queue.put(enqueue_item)
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


class Statistician:
    def __init__(self, consumption_queue, delay=10):
        self.queue = consumption_queue
        self.delay = delay
        self.kill_sig = False

    async def calculate(self, delay=10):
        while not self.kill_sig:
            cq = self.queue
            if cq.qsize() > 1:
                queue_copy = list(cq.queue)
                average_response_time = sum(i['response_time'] for i in queue_copy) / len(queue_copy)
                statistics.update({
                    'time': queue_copy[len(queue_copy) - 1].get('time'),
                    'average_response_time': average_response_time,
                    'request_count': len(queue_copy),
                    'max_time': queue_copy[len(queue_copy) - 1].get('time'),
                    'min_time': queue_copy[0].get('time'),
                    'requests_per_minute': len(queue_copy) / (
                            queue_copy[len(queue_copy) - 1].get('time') - queue_copy[0].get('time')) * 60
                })

                log(f"Statistician: {statistics}")

            await asyncio.sleep(delay)

    def kill(self):
        self.delay = 0
        self.kill_sig = True

    def set_delay(self, delay):
        self.delay = delay


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


class ConsumerPool:
    def __init__(self, job_queue, consumption_delay, pool_size):
        self.pool_size = pool_size
        self.MAX_POOL_SIZE = 10000
        self.consumption_delay = consumption_delay
        self.queue = job_queue
        self.consumers = {}
        self.enabled = []
        self.disabled = []

        for c in range(self.MAX_POOL_SIZE):
            self.consumers[c] = Consumer(job_queue, c, self.consumption_delay)
            self.disabled.append(c)

        for c in range(self.pool_size):
            self.enabled.append(c)
            self.consumers[c].enable()
            self.disabled.remove(c)

    def get_consumers(self):
        return [c.consume() for c in self.consumers.values()]

    def set_pool_size(self, pool_size):
        if self.pool_size > pool_size:
            log(f"Decreasing Consumers from {self.pool_size} to {pool_size}")
            disable_count = self.pool_size - pool_size
            for d in range(disable_count):
                e = self.enabled.pop()
                self.consumers[e].disable()
                self.disabled.append(e)
        elif self.pool_size < pool_size:
            log(f"Increasing Consumers from {self.pool_size} to {pool_size}")
            for d in range(pool_size - self.pool_size):
                d = self.disabled.pop()
                self.consumers[d].enable()
                self.enabled.append(d)

        self.pool_size = pool_size

    def get_pool_size(self):
        return self.pool_size

    def get_delay(self):
        return self.consumption_delay

    def set_delay(self, delay):
        for k, v in self.consumers.items():
            v.set_delay(delay)
        self.consumption_delay = delay


async def runner(source_config, target_response_rate_in_sec=6):
    log("Running")

    producer = Producer(job_queue, 10000, source_config, 1)
    consumer_pool = ConsumerPool(job_queue, CONSUME_DELAY_IN_MILLIS / 1000, CONSUMER_COUNT)
    statistician = Statistician(consumption_queue, 10)
    cleaner = Cleaner(consumption_queue, delay=10)
    control_system = ControlSystem(60, target_response_rate_in_sec, statistics, consumer_pool, 10)

    await asyncio.gather(
        producer.produce(),
        *consumer_pool.get_consumers(),
        statistician.calculate(),
        cleaner.clean(),
        control_system.control()
    )