import math

import numdifftools
import numpy


class StupidGradient(object):
    def __init__(self, value_shift=1e-10):
        self.value_shift = value_shift

    def gradient(self, func: callable(list[float]), values: list[float]) -> list[float]:
        gradient = list()
        for i in range(len(values)):
            # print("i:", i)
            # print("vals: ", values)
            values_shifted_up = list(values)
            values_shifted_down = list(values)
            values_shifted_up[i] += self.value_shift
            values_shifted_down[i] -= self.value_shift
            # print("val_sf_up:{}; val_sh_dn:{}".format(values_shifted_up, values_shifted_down))
            gradient_val = ((func(values_shifted_up) - func(values_shifted_down)) / (
                    values_shifted_up[i] - values_shifted_down[i]))
            # print("grad_val: ", gradient_val)
            # gradient.append(
            #     (func(values_shifted_up) - func(values_shifted_down)) / (values_shifted_up[i] - values_shifted_down[i]))
            gradient.append(gradient_val)

        return gradient


def main():
    def fun(vals) -> float:
        x = vals[0]
        y = vals[1]
        z = vals[2]
        return numpy.sin(x + 2 * y) + 2 * numpy.sqrt(x * y * z)

    M = [math.pi / 2, math.pi * 3 / 2, 3]

    sg = StupidGradient
    print("stupid grad: ", sg.gradient(fun, M))
    M = numpy.array(M)
    print("ndt grad: ", numdifftools.Gradient(fun)(M))


