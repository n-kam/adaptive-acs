import logging

import numpy
from control import matlab
from matplotlib import pyplot


def plot_results(model_response_times: list[float],
                 model_response_values: list[float],
                 nominator: list[float],
                 denominator: list[float]) -> None:
    """
    Построение графиков переходной характеристики, снятой с модели и подобранной теоретически.

    ПХ модели строится красным цветом. Теоретическая - зеленым.

    :param model_response_times: Список из точек времени, для которых строить график.
    :param model_response_values: Список значений модельной переходной характеристики, соответствующей заданным точкам времени.
    :param nominator: Список коэффициентов числителя теоретически подобранной передаточной функции.
    :param denominator: Список коэффициентов знаменателя теоретически подобранной передаточной функции.
    """
    # Очистить логи от мусорных дебажных сообщений из внутренних библиотек pyplot'а
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)

    pyplot.grid(True)
    # todo: избавиться от хардкода:
    pyplot.xticks(numpy.arange(0, 11, 1))
    pyplot.yticks(numpy.arange(0, 1.1, 0.1))

    pyplot.plot(model_response_times, model_response_values, 'red')

    optimization_tf = matlab.tf(nominator, denominator)
    [tf_values, x1] = matlab.step(optimization_tf, model_response_times)
    pyplot.plot(model_response_times, tf_values, 'green')
    pyplot.show()
