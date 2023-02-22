from throughput_measure.do_logging import log
from throughput_measure.example import data_source_example
from throughput_measure.utils.context_util import measurement_config
import aiohttp

from throughput_measure.utils.decorator_util import throughput_target_function
from throughput_measure.utils.run_util import run_throughput_measure


async def test_function():
    async with aiohttp.ClientSession() as session:
        example_url = 'https://www.example.com'
        async with session.get(example_url) as resp:
            await resp.text()


def cli_example_using_context_manager():
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


def cli():
    @throughput_target_function(probabilty=0.1)
    async def my_foo_target():
        await data_source_example.foo()

    @throughput_target_function(probabilty=0.2)
    async def my_bar_target():
        await data_source_example.bar()

    @throughput_target_function(probabilty=0.3)
    async def my_test_function():
        await test_function()

    run_throughput_measure(target_response_rate_in_sec=5)
