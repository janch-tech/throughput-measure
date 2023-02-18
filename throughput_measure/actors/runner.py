import asyncio
import queue

from throughput_measure.actors.cleaner import Cleaner
from throughput_measure.actors.consumer_pool import ConsumerPool
from throughput_measure.actors.control_system import ControlSystem
from throughput_measure.do_logging import log
from throughput_measure.actors.producer import Producer

from throughput_measure.actors.statistician import Statistician

job_queue = asyncio.Queue()
consumption_queue = queue.Queue()
statistics = {}
CONSUME_DELAY_IN_MILLIS = 1000.0
CONSUMER_COUNT = 10


async def runner(source_config, target_response_rate_in_sec=6):
    log("Running")

    producer = Producer(job_queue, 10000, source_config, 1)
    consumer_pool = ConsumerPool(job_queue, consumption_queue, CONSUME_DELAY_IN_MILLIS / 1000, CONSUMER_COUNT)
    statistician = Statistician(consumption_queue, statistics, 10)
    cleaner = Cleaner(consumption_queue, delay=10)
    control_system = ControlSystem(60, target_response_rate_in_sec, statistics, consumer_pool, 10)

    await asyncio.gather(
        producer.produce(),
        *consumer_pool.get_consumers(),
        statistician.calculate(),
        cleaner.clean(),
        control_system.control()
    )