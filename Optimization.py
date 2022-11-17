import time

import numdifftools
import numpy


class Optimization(object):

    def adam(self, target_func, values: list,
             precision=0.001,
             step=10,
             beta1=0.9,
             beta2=0.999,
             max_iter=10000,
             *args, **kwargs):

        values = numpy.array(values)
        M = numpy.array([0.0]*len(values))
        V = numpy.array([0.0]*len(values))
        values_prev = values + numpy.array([1]*len(values))
        iteration = 1
        time_start = time.time()

        while (abs((values - values_prev).any()) > precision) & (iteration < max_iter):
            values_prev = values
            gradient = numdifftools.Gradient(target_func)(values)
            M = beta1 * M + (1 - beta1) * gradient
            V = beta2 * V + (1 - beta2) * gradient ** 2
            m = M / (1 - beta1 ** iteration)
            v = V / (1 - beta2 ** iteration)
            values = values - step * m / (numpy.sqrt(v) + precision)
            iteration += 1
            print("[", iteration, "]: values=", values, "; grad=", gradient)

        time_end = time.time()

        print("time of run: ", time_end - time_start)
