import time

import numpy
import logging as log

from Classes.StupidGradient import StupidGradient


class Optimization(object):
    log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.DEBUG)
    stupid_gradient = StupidGradient()

    def adam(self, target_func, values: list[float],
             tf_precision=1e-6,
             # todo: подобрать более оптимальное значение шага, желательно, в зависимости от степеней входной функции:
             step=0.1,
             beta1=0.9,
             beta2=0.999,
             max_iter=15_000) -> list[float]:
        log.info("Started Adam optimization algorithm")
        values = numpy.array(values)
        best_values = values
        biased_first_estimate = numpy.array([0.0] * len(values))
        biased_second_estimate = numpy.array([0.0] * len(values))
        iteration = 0
        time_start = time.time()
        time_prev_output = time.time()
        target_func_curr_value = target_func(values)
        target_func_min_value = 1e10

        while (iteration < max_iter) & (target_func_curr_value > tf_precision):
            iteration += 1
            # gradient = numdifftools.Gradient(target_func)(values)
            # log.warning("ndt grad {}".format(gradient))
            gradient = numpy.array(self.stupid_gradient.gradient(target_func, values))
            # log.warning("stup grad {}".format(gradient))
            biased_first_estimate = beta1 * biased_first_estimate + (1 - beta1) * gradient
            biased_second_estimate = beta2 * biased_second_estimate + (1 - beta2) * gradient ** 2
            corrected_first_estimate = biased_first_estimate / (1 - beta1 ** iteration)
            corrected_second_estimate = biased_second_estimate / (1 - beta2 ** iteration)
            values = values - step * corrected_first_estimate / (numpy.sqrt(corrected_second_estimate))
            target_func_curr_value = target_func(values)

            # Запоминаем лучше значения коэффициентов на случай вылета за отсечку по итерациям, т.к. значение целевой
            # функции может скакать в процессе расчета и последние значения в случае вылета могут не быть лучшими
            if target_func_curr_value < target_func_min_value:
                target_func_min_value = target_func_curr_value
                best_values = values

            # Вывод в лог по ходу расчетов каждые N итераций
            output_iter_step = 10
            if iteration % output_iter_step == 0:
                time_now = time.time()
                run_speed = output_iter_step / (time_now - time_prev_output)
                time_prev_output = time_now
                eta_minutes = (max_iter - iteration) / run_speed / 60
                log.debug("({}) Running Adam optimization. Speed: {:.1f} iter/s. Time passed: {:.1f} min. "
                          "Max iter ETA: {:.1f} min.".format(iteration,
                                                             run_speed,
                                                             (time_now - time_start) / 60,
                                                             eta_minutes))
                log.debug("val  = {}; tf = {}".format(values, target_func_curr_value))
                log.debug("grad = {};\n".format(gradient))

        time_end = time.time()

        log.info("Time of run: {}. Integral quality current: {}, min: {}".format(time_end - time_start,
                                                                                 target_func_curr_value,
                                                                                 target_func_min_value))

        if iteration == max_iter:
            log.warning("Maximum number of iterations exceeded. Returned values may be suboptimal")
            values = best_values

        return values

    def classic(self, target_func, values: list[float],
                tf_precision=0.05,
                step=0.1,
                max_iter=10_000,
                # max_iter=1000,
                stepdown_enabled=True) -> list[float]:
        log.info("Started Classic optimization algorithm")
        # values = numpy.array(values)
        best_values = values
        iteration = 0
        time_start = time.time()
        time_prev_output = time.time()
        target_func_curr_value = target_func(values)
        target_func_min_value = 1e10

        while (iteration < max_iter) & (target_func_curr_value > tf_precision):
            # gradient = numdifftools.Gradient(target_func)(values)
            gradient = numpy.array(self.stupid_gradient.gradient(target_func, values))

            # Если целевая функция на следующем шаге станет больше, чем на текущем, или перескочит экстремум,
            # сделать градиентный шаг поменьше, в надежде снизить ее скачки. (Получается фигня полная, шаг уходит в
            # ноль и ЦФ стоит на месте в итоге. Поэтому пока флаг выключен)
            target_func_next_value = target_func(values - step * gradient)
            # target_func_curr_value = target_func(values)
            if stepdown_enabled & (target_func_next_value > target_func_curr_value):
                step /= 2
            else:
                # todo: подобрано на глаз. Это максимальное значение, которое можно поставить, при котором у меня не
                #  начиналось расхождение. Но это только для текущей функции. При других снятых значениях,
                #  может иметь смысл этот коэффициент поменять
                step *= 1.8
            values = values - step * gradient
            target_func_curr_value = target_func(values)

            # Запоминаем лучше значения коэффициентов на случай вылета за отсечку по итерациям, т.к. значение целевой
            # функции может скакать в процессе расчета и последние значения в случае вылета могут не быть лучшими
            if target_func_curr_value < target_func_min_value:
                target_func_min_value = target_func_curr_value
                best_values = values

            # Вывод в лог по ходу расчетов каждые N итераций
            output_iter_step = 100
            if iteration % output_iter_step == 0:
                time_now = time.time()
                run_speed = output_iter_step / (time_now - time_prev_output)
                time_prev_output = time_now
                eta_minutes = (max_iter - iteration) / run_speed / 60
                log.debug("({}) Running Classic optimization. Speed: {:.1f} iter/s. Time passed: {:.1f} min. "
                          "Max iter ETA: {:.1f} min.".format(iteration,
                                                             run_speed,
                                                             (time_now - time_start) / 60,
                                                             eta_minutes))
                log.debug("val  = {}; tf = {}; step = {}".format(values, target_func_curr_value, step))
                log.debug("grad = {};\n".format(gradient))
            iteration += 1

        time_end = time.time()

        log.info("Time of run: {:.0f} sec. Integral quality current: {}, min: {}".format(time_end - time_start,
                                                                                         target_func_curr_value,
                                                                                         target_func_min_value))

        if iteration == max_iter:
            log.warning("Maximum number of iterations exceeded. Returned values may be suboptimal")
            values = best_values

        return values
