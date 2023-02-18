from throughput_measure.do_logging import log
from throughput_measure.actors.consumer import Consumer


class ConsumerPool:
    def __init__(self, job_queue, consumption_queue, consumption_delay, pool_size):
        self.pool_size = pool_size
        self.MAX_POOL_SIZE = 10000
        self.consumption_delay = consumption_delay
        self.job_queue = job_queue
        self.consumption_queue = consumption_queue
        self.consumers = {}
        self.enabled = []
        self.disabled = []

        for c in range(self.MAX_POOL_SIZE):
            self.consumers[c] = Consumer(job_queue, consumption_queue, c, self.consumption_delay)
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
