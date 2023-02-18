import asyncio

from throughput_measure.do_logging import log



class Statistician:
    def __init__(self, consumption_queue, statistics,  delay=10):
        self.queue = consumption_queue
        self.delay = delay
        self.kill_sig = False
        self.statistics = statistics

    async def calculate(self, delay=10):
        while not self.kill_sig:
            cq = self.queue
            if cq.qsize() > 1:
                queue_copy = list(cq.queue)
                average_response_time = sum(i['response_time'] for i in queue_copy) / len(queue_copy)
                self.statistics.update({
                    'time': queue_copy[len(queue_copy) - 1].get('time'),
                    'average_response_time': average_response_time,
                    'request_count': len(queue_copy),
                    'max_time': queue_copy[len(queue_copy) - 1].get('time'),
                    'min_time': queue_copy[0].get('time'),
                    'requests_per_minute': len(queue_copy) / (
                            queue_copy[len(queue_copy) - 1].get('time') - queue_copy[0].get('time')) * 60
                })

                log(f"Statistician: {self.statistics}")

            await asyncio.sleep(delay)

    def kill(self):
        self.delay = 0
        self.kill_sig = True

    def set_delay(self, delay):
        self.delay = delay
