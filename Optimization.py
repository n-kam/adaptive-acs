import time

import numdifftools
import numpy
import logging as log


class Optimization(object):
    log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.DEBUG)

    @staticmethod
    def adam(target_func, values: list[float],
             values_precision=0.01,
             tf_precision=1e-6,
             # todo: подобрать более оптимальное значение шага, желательно, в зависимости от степеней входной функции:
             step=0.1,
             beta1=0.9,
             beta2=0.999,
             max_iter=10000) -> list[float]:
        # log.debug("Started Adam optimization algorithm")
        values = numpy.array(values)
        best_values = values
        M = numpy.array([0.0] * len(values))
        V = numpy.array([0.0] * len(values))
        values_prev = values + numpy.array([values_precision * 2] * len(values))
        iteration = 0
        time_start = time.time()
        target_func_curr_value = target_func(values)
        target_func_min_value = 1e10
        # log.debug("Started Adam optimization algorithm while loop")

        while (abs((values - values_prev).any()) > values_precision) & (iteration < max_iter) & (
                target_func_curr_value > tf_precision):
            iteration += 1
            values_prev = values
            # log.debug("Start gradient calculation")
            gradient = numdifftools.Gradient(target_func)(values)
            # log.debug("Finish gradient calculation")
            M = beta1 * M + (1 - beta1) * gradient
            V = beta2 * V + (1 - beta2) * gradient ** 2
            m = M / (1 - beta1 ** iteration)
            v = V / (1 - beta2 ** iteration)
            values = values - step * m / (numpy.sqrt(v) + values_precision)
            target_func_curr_value = target_func(values)

            # Запоминаем лучше значения коэффициентов на случай вылета за отсечку по итерациям, т.к. значение целевой
            # функции может скакать в процессе расчета и последние значения в случае вылета могут не быть лучшими
            if target_func_curr_value < target_func_min_value:
                target_func_min_value = target_func_curr_value
                best_values = values

            log.debug("[{}] tf = {};".format(iteration, target_func_curr_value))
            log.debug("values   = {}".format(values))
            log.debug("gradient = {}".format(gradient))

        time_end = time.time()

        log.info("time of run: {}".format(time_end - time_start))

        if iteration == max_iter:
            log.warning("Maximum number of iterations exceeded. Returned values may be suboptimal")
            values = best_values

        return values
