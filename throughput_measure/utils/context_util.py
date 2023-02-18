from contextlib import contextmanager
import asyncio
import sys

from throughput_measure.actors.runner import runner
from throughput_measure.do_logging import log


@contextmanager
def measurement_config(target_response_rate_in_sec):
    measurement_config_dict = {}
    yield measurement_config_dict

    if measurement_config_dict:
        log(measurement_config_dict)

        for k, v in measurement_config_dict.items():
            log(v)
            assert 'probability' in v, 'Must set a field called probability e.g. 0.1'
            assert 'function' in v, 'Must set a function callback'

        try:
            asyncio.run(runner(
                source_config=measurement_config_dict,
                target_response_rate_in_sec=target_response_rate_in_sec
            ))

        except KeyboardInterrupt:
            log("Thanks for using throughput-measure. Bye!!")
            sys.exit()
    else:
        log('Nothing to do')
