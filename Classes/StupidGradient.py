import math

import numdifftools
import numpy


class StupidGradient(object):

    def __init__(self, value_shift=1e-10):
        self.value_shift = value_shift

    def gradient(self, func: callable(list[float]), values: list[float]) -> list[float]:
        gradient = list()
        for i in range(len(values)):
            gradient.append(self.partial_derivative(func, values, i))

        return gradient

    def partial_derivative(self, func: callable(list[float]), values: list[float], mutable_var_number: int) -> float:
        values_shifted_up = list(values)
        values_shifted_down = list(values)
        values_shifted_up[mutable_var_number] += self.value_shift
        values_shifted_down[mutable_var_number] -= self.value_shift
        partial_derivative_value = ((func(values_shifted_up) - func(values_shifted_down)) / (
                values_shifted_up[mutable_var_number] - values_shifted_down[mutable_var_number]))

        return partial_derivative_value


def test():
    def fun(vals) -> float:
        x = vals[0]
        y = vals[1]
        z = vals[2]
        return numpy.sin(x + 2 * y) + 2 * numpy.sqrt(x * y * z)

    M = [math.pi / 2, math.pi * 3 / 2, 3]

    sg = StupidGradient
    print("stupid pd 0: ", sg.partial_derivative(sg(), fun, M, 0))
    print("stupid pd 1: ", sg.partial_derivative(sg(), fun, M, 1))
    print("stupid pd 2: ", sg.partial_derivative(sg(), fun, M, 2))
    print("stupid grad new: ", sg.gradient(sg(), fun, M))
    M = numpy.array(M)
    print("ndt grad: ", numdifftools.Gradient(fun)(M))


# Раскомментировать для тестирования:
# test()
