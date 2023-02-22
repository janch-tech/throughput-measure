import asyncio
import sys

from throughput_measure.actors.runner import runner
from throughput_measure.do_logging import log
from throughput_measure.measurement_config import measurement_config_dict


def run_throughput_measure(target_response_rate_in_sec):
    try:
        asyncio.run(runner(
            source_config=measurement_config_dict,
            target_response_rate_in_sec=target_response_rate_in_sec
        ))

    except KeyboardInterrupt:
        log("Thanks for using throughput-measure. Bye!!")
        sys.exit()
