import numpy
import sympy

from Optimization import Optimization
from TransferFunction import TransferFunction

# arr = numpy.array()
arr = numpy.repeat(1, 10)
print(arr[4])
print(arr)

v1, v2, v3 = 0.0, 0.0, 0.0
values = [v1, v2, v3]


def tf(var):
    return (var[0] - 10) ** 2 + (var[1] + 4.63) ** 4 + (var[2] - 3.4) ** 2


b0 = 0
b1 = 1
b2 = 0

a0 = 0
a1 = 2
a2 = 1000

pid = TransferFunction()
pid.w(1, 2, 3, )
opt = Optimization()
opt.adam(pid.w, p)
