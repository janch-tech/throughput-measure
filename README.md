# throughput-measure

A tool for measuring throughput. 

This tool is basically a control system where a response rate from a target
is controlled by increasing or decreasing the number of requests sent

# Usage

```bash
pip install -e .
throughput-measure
```

# Explained with Example

In the following example:
- `my_foo_target` is called with a probability of 0.1
- `my_bar_target` is called with a probability of 0.2
- `my_test_function` is called with a probability of 0.3

When run using `run_throughput_measure` with a target response rate of 5 seconds,
the tool starts making repeated calls to the functions. 
1. It constantly measures the average response_rate. 
2. It tries to increase the function call rate if response rate < target
3. It tries to decrease the function rate if response rate > target


```python3
import aiohttp
import asyncio
from throughput_measure.utils.decorator_util import throughput_target_function
from throughput_measure.utils.run_util import run_throughput_measure
async with aiohttp.ClientSession() as session:

@throughput_target_function(probabilty=0.1)
async def my_foo_target():
    await asyncio.sleep(2)


@throughput_target_function(probabilty=0.2)
async def my_bar_target():
    await asyncio.sleep(1)


@throughput_target_function(probabilty=0.3)
async def my_test_function():
    example_url = 'https://www.example.com'
    async with session.get(example_url) as resp:
        await resp.text()


run_throughput_measure(target_response_rate_in_sec=5)


```


# Why

Wrote this so that I can measure the throughput i.e the number of requests 
hitting a server when a response rate needs to be kept constant.

If we hit the server too fast, the server slows down so we need decrease the requests going in
If we hit the server too slow, maybe we can send in requests faster


