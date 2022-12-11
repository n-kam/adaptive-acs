import math

import numdifftools
import numpy


class FastGradient(object):

    def __init__(self, value_shift=1e-10):
        """
        Инициализация класса рассчета быстрого градиента.

        :param value_shift: Величина, на которую будет сдвинута выбранная переменная при расчете dy/dx.
        """
        self.value_shift = value_shift

    def gradient(self, func: callable(list[float]), values: list[float]) -> list[float]:
        """
        Для каждого элемента из списка переменных рассчитать частную производную функции func и сложить результаты в один список.

        :param func: Вызываемая функция.
        :param values: Список переменных вызываемой функции.
        :return: Список-вектор градиента.
        """
        gradient = list()
        for i in range(len(values)):
            gradient.append(self.partial_derivative(func, values, i))

        return gradient

    def partial_derivative(self, func: callable(list[float]), values: list[float], mutable_var_number: int) -> float:
        """
        Рассчитать частную производную по одной из переменных быстрым способом. Метод увеличивает выбранную переменную на очень малую величину value_shift и рассчитывает dy/dx.

        :param func: Вызываемоая функция.
        :param values: Список всех переменных вызываемой функции.
        :param mutable_var_number: Порядковый номер в списке values переменной, по которой необходимо рассчитать частную производную.
        :return: Значение частной производной.
        """
        values_shifted_up = list(values)
        values_shifted_down = list(values)
        values_shifted_up[mutable_var_number] += self.value_shift
        values_shifted_down[mutable_var_number] -= self.value_shift
        partial_derivative_value = ((func(values_shifted_up) - func(values_shifted_down)) / (
                values_shifted_up[mutable_var_number] - values_shifted_down[mutable_var_number]))

        return partial_derivative_value


def test() -> None:
    """
    Метод для тестов и дебага. Сравнивает градиент определенной функции, рассчитанный быстрым способом с градиентом, рассчитанным с помощью библиотеки numdifftools.
    """

    def fun(vals) -> float:
        x = vals[0]
        y = vals[1]
        z = vals[2]
        return numpy.sin(x + 2 * y) + 2 * numpy.sqrt(x * y * z)

    M = [math.pi / 2, math.pi * 3 / 2, 3]

    sg = FastGradient
    print("fast pd 0: ", sg.partial_derivative(sg(), fun, M, 0))
    print("fast pd 1: ", sg.partial_derivative(sg(), fun, M, 1))
    print("fast pd 2: ", sg.partial_derivative(sg(), fun, M, 2))
    print("fast grad: ", sg.gradient(sg(), fun, M))
    M = numpy.array(M)
    print("ndt grad: ", numdifftools.Gradient(fun)(M))

# Раскомментировать для тестирования:
# test()
