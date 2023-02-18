from throughput_measure.example.source_simulation import ConstantResponseRate

fooSource = ConstantResponseRate(1000)
barSource = ConstantResponseRate(200)


async def foo():
    # log("Foo")
    await fooSource.example_get_response()


async def bar():
    # log("Bar")
    await barSource.example_get_response()


example_config_file = {
    'foo': {'probability': 0.1, 'function': foo},
    'bar': {'probability': 0.2, 'function': bar}
}