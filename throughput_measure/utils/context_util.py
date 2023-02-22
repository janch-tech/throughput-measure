from contextlib import contextmanager

from throughput_measure.do_logging import log
from throughput_measure.measurement_config import measurement_config_dict
from throughput_measure.utils.run_util import run_throughput_measure


@contextmanager
def measurement_config(target_response_rate_in_sec):
    yield measurement_config_dict

    if measurement_config_dict:
        log(measurement_config_dict)

        for k, v in measurement_config_dict.items():
            log(v)
            assert 'probability' in v, 'Must set a field called probability e.g. 0.1'
            assert 'function' in v, 'Must set a function callback'

        run_throughput_measure(target_response_rate_in_sec)
    else:
        log('Nothing to do')
