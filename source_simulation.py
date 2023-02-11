import asyncio
from queue import Queue
from time import time


class ConstantResponseRate:
    def __init__(self, delay_in_ms):
        self.response_times = Queue()
        self.response_times.put(time())
        self.delay_in_ms = delay_in_ms

    async def example_get_response_2(self):

        await asyncio.sleep(self.delay_in_ms)
        return 0

    async def example_get_response(self):
        when = self.response_times.get()
        self.response_times.put(when + (self.delay_in_ms/1000))
        now = time()
        await asyncio.sleep(
            (when - now if now <= when else 0)
        )

        return when

    async def test_print_response(self):
        response = await self.example_get_response()
        print(response)

    async def test(self):
        await asyncio.gather(
            self.test_print_response(),
            self.test_print_response(),
            self.test_print_response(),
            self.test_print_response(),
            self.test_print_response(),
            self.test_print_response(),
            self.test_print_response(),
            self.test_print_response(),
            self.test_print_response(),
            self.test_print_response()
        )


if __name__ == '__main__':
    crs = ConstantResponseRate(2000)
    asyncio.run(crs.test())
