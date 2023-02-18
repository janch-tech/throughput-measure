from throughput_measure.do_logging import log
from throughput_measure.example import data_source_example
from throughput_measure.utils.context_util import measurement_config
import aiohttp


async def test_function():
    async with aiohttp.ClientSession() as session:
        example_url = 'https://www.example.com'
        async with session.get(example_url) as resp:
            await resp.text()


def cli():
    log("Starting")
    with measurement_config(5) as config:
        config['foo'] = {
            'probability': 0.1,
            'function': data_source_example.foo
        }

        config['bar'] = {
            'probability': 0.2,
            'function': data_source_example.bar
        }

        config['my_function'] = {
            'probability': 0.5,
            'function': test_function
        }
