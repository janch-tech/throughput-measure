import asyncio
import sys

from data_source_example import example_config_file
from do_logging import log
from throughput_measure import runner

if __name__ == '__main__':
    log("Starting")
    try:
        asyncio.run(runner(
            source_config=example_config_file,
            target_response_rate_in_sec=5
        ))
    except KeyboardInterrupt:
        log("Bye!!")
        sys.exit()
