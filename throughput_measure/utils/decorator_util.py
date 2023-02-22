from throughput_measure.measurement_config import measurement_config_dict


def throughput_target_function(probabilty):
    def wrapper_inner(func):
        def wrapper_outer(*args, **kwargs):
            return func(args, kwargs)

        measurement_config_dict[str(func)] = {'probability': probabilty, 'function': func}

        return wrapper_outer

    return wrapper_inner
