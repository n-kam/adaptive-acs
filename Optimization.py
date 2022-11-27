import time

import numdifftools
import numpy
import logging as log


class Optimization(object):
    log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.DEBUG)

    @staticmethod
    def adam(target_func, values: list[float],
             values_precision=0.01,
             tf_precision=0.0001,
             step=10,
             beta1=0.9,
             beta2=0.999,
             max_iter=10000) -> list:
        values = numpy.array(values)
        M = numpy.array([0.0] * len(values))
        V = numpy.array([0.0] * len(values))
        values_prev = values + numpy.array([values_precision * 2] * len(values))
        iteration = 1
        time_start = time.time()

        while (abs((values - values_prev).any()) > values_precision) & (iteration < max_iter) & (
                target_func(values) > tf_precision):
            values_prev = values
            gradient = numdifftools.Gradient(target_func)(values)
            M = beta1 * M + (1 - beta1) * gradient
            V = beta2 * V + (1 - beta2) * gradient ** 2
            m = M / (1 - beta1 ** iteration)
            v = V / (1 - beta2 ** iteration)
            values = values - step * m / (numpy.sqrt(v) + values_precision)
            iteration += 1
            print("tf: ", target_func(values), " [", iteration, "]: values=", values, "; grad=", gradient)

        time_end = time.time()

        print("time of run: ", time_end - time_start)
        return list(values)
