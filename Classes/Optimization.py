import time

import numpy
import logging as log

from Classes.FastDerivative import FastGradient


class Optimization(object):
    log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.INFO)
    stupid_gradient = FastGradient()

    def adam(self, target_func, values: list[float],
             tf_precision=0.01,
             step=0.001,
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

        log.info("Time of run: {:.0f} sec. Integral quality current: {}, min: {}".format(time_end - time_start,
                                                                                         target_func_curr_value,
                                                                                         target_func_min_value))

        if iteration == max_iter:
            log.warning("Maximum number of iterations exceeded. Returned values may be suboptimal")
            values = best_values

        return values

    def classic(self,
                target_func: callable(list[float]),
                values: list[float],
                tf_precision: float = 0.025,
                # tf_precision: float = 0.05,  # todo: revert before commit!!!
                step: float = 0.1,
                max_iter: int = 10_000,
                output_iter_step: int = 1000,
                # max_iter: int = 10,  # todo: revert before commit!!!
                stepdown_enabled: bool = True) -> list[float]:
        """
        Не-очень-классический градиентный спуск. Отличается от классического переменным шагом, который в зависимости от значения целевой функции на следующем шаге может как уменьшаться, так и увеличиваться.

        :param target_func: Целевая функция, значение которой необходимо минимизировать в результате рассчета.
        :param values: Список исходных значений, передаваемых в целевую функцию.
        :param tf_precision: Необходимая точность целевой функции.
        :param step: Начальный шаг градиентного спуска.
        :param output_iter_step: Выводить промежуточные результаты каждые N итераций.
        :param max_iter: Отсечка по итерациям, при превышении которой алгоритм будет остановлен.
        :param stepdown_enabled: Использовать ли спуск с переменным шагом или без (классический).
        :return: Список из оптимизированных по минимуму целевой функции входных параметров.
        """

        log.info("Начало расчета методом классического градиентного спуска. Промежуточные результаты будут выводиться "
                 "каждые {} итераций. Можете пока пойти заварить себе чай...".format(output_iter_step))
        best_values = values
        iteration = 0
        time_start = time.time()
        time_prev_output = time.time()
        target_func_curr_value = target_func(values)
        target_func_min_value = 1e10

        while (iteration < max_iter) & (target_func_curr_value > tf_precision):
            iteration += 1
            gradient = numpy.array(self.stupid_gradient.gradient(target_func, values))

            # Если целевая функция на следующем шаге станет больше, чем на текущем, или перескочит экстремум,
            # сделать градиентный шаг поменьше
            target_func_next_value = target_func(values - step * gradient)
            if stepdown_enabled & (target_func_next_value > target_func_curr_value) & (step > 1e-8):
                step /= 2
            elif stepdown_enabled:
                # todo: подобрано на глаз. Это максимальное значение, которое можно поставить, при котором у меня не начиналось расхождение. Но это только для текущей функции. При других снятых значениях, может иметь смысл этот коэффициент поменять
                step *= 1.8

            values = values - step * gradient
            target_func_curr_value = target_func(values)

            # Запоминаем лучше значения коэффициентов на случай вылета за отсечку по итерациям, т.к. значение целевой функции может скакать в процессе расчета и последние значения в случае вылета могут не быть лучшими
            if target_func_curr_value < target_func_min_value:
                target_func_min_value = target_func_curr_value
                best_values = values

            # Вывод в лог по ходу расчетов каждые N итераций
            if iteration % output_iter_step == 0:
                time_now = time.time()
                run_speed = output_iter_step / (time_now - time_prev_output)
                time_prev_output = time_now
                eta_minutes = (max_iter - iteration) / run_speed / 60
                log.info("({}) Классический метод. Скорость: {:.1f} итер./с. Время работы: {:.1f} мин. "
                         "Прибл. время до отсечки по итерациям: {:.1f} min.".format(iteration,
                                                                                  run_speed,
                                                                                  (time_now - time_start) / 60,
                                                                                  eta_minutes))
                log.info("Значения параметров: {}".format(values))
                log.info("Вектор градиента:    {}".format(gradient))
                log.info("Целевая функция = {}; Текущий град. шаг = {}\n".format(target_func_curr_value, step))

        time_end = time.time()

        log.info("Время работы: {:.0f} с. Значение целевой функции последнее: {:.5f}, минимальное: {:.5f}".format(
            time_end - time_start,
            target_func_curr_value,
            target_func_min_value))

        if iteration == max_iter:
            log.warning("Выход за отсечку по итерациям. Итоговые значения могут быть неоптимальными")
            values = best_values

        return values

    def gauss_seidel(self, target_func, values: list[float],
                     # tf_precision=0.01,  # если порядок теоретический заведомо больше, чем модельный
                     tf_precision=0.05,
                     tf_derivative_precision=1e-3,
                     step=0.1,
                     max_iter=50_000,
                     stepdown_enabled=True) -> list[float]:
        """
        Метод Гаусса-Зейделя. Шаг делает не сразу по всем переменным, а по каждой по отдельности
        """
        log.info("Started Gauss-Seidel optimization algorithm")
        # values = numpy.array(values)
        best_values = values
        iteration = 0
        inner_iteration = 0
        time_start = time.time()
        time_prev_output = time.time()
        target_func_curr_value = target_func(values)
        target_func_min_value = 1e10
        curr_step = step

        while (inner_iteration < max_iter) & (target_func_curr_value > tf_precision):
            iteration += 1
            log.debug("({}); tf = {}; tf_grad={}".format(iteration, target_func_curr_value,
                                                         self.stupid_gradient.gradient(target_func, values)))
            for i in range(len(values) - 1, -1, -1):
                curr_step = step
                tf_partial_derivative = self.stupid_gradient.partial_derivative(target_func, values, i)
                log.debug("({}:{}); tf = {}; tf_part_deriv={}".format(iteration, i, target_func_curr_value,
                                                                      tf_partial_derivative))
                while (inner_iteration < max_iter) & \
                        (abs(tf_partial_derivative) > tf_derivative_precision) & \
                        (target_func_curr_value > tf_precision):
                    values_save = list(values)
                    values[i] -= tf_partial_derivative * curr_step

                    # Если производная на следующем шаге поменяет знак, снизить шаг
                    tf_partial_derivative_next = self.stupid_gradient.partial_derivative(target_func, values, i)
                    derivative_will_step_over_zero = ((tf_partial_derivative_next > 0) & (
                            tf_partial_derivative < 0)) | ((tf_partial_derivative_next < 0) & (
                            tf_partial_derivative > 0))
                    derivative_value_will_rise = abs(tf_partial_derivative_next) >= abs(tf_partial_derivative)
                    stepdown_needed = derivative_will_step_over_zero  # | derivative_value_will_rise
                    if stepdown_enabled & stepdown_needed:
                        curr_step /= 2
                        values = list(values_save)
                        values[i] -= tf_partial_derivative * curr_step
                    elif stepdown_enabled:  # & (curr_step < step):
                        curr_step *= 1.2

                    # Вывод в лог по ходу расчетов каждые N ВНУТРЕННИХ итераций
                    output_iter_step = 1000
                    if inner_iteration % output_iter_step == 0:
                        tf_partial_derivative = self.stupid_gradient.partial_derivative(target_func, values, i)
                        log.debug("({}:{}:{}); val  = {}; tf = {}; tf_deriv = {},"
                                  " curr step = {}".format(inner_iteration,
                                                           iteration, i,
                                                           values,
                                                           target_func_curr_value,
                                                           tf_partial_derivative,
                                                           curr_step))
                        target_func_curr_value = target_func(values)
                    target_func_curr_value = target_func(values)

                    inner_iteration += 1

                # Вывод в лог по ходу расчетов каждые N ВНУТРЕННИХ итераций
                output_iter_step = 10
                if inner_iteration % output_iter_step == 0:
                    time_now = time.time()
                    run_speed = output_iter_step / (time_now - time_prev_output)
                    time_prev_output = time_now
                    eta_minutes = (max_iter - iteration) / run_speed / 60
                    log.debug("({}) Running Classic optimization. Speed: {:.1f} iter/s. Time passed: {:.1f} min. "
                              "Max iter ETA: {:.1f} min.".format(iteration,
                                                                 run_speed,
                                                                 (time_now - time_start) / 60,
                                                                 eta_minutes))
                    log.debug("val  = {}; tf = {}; step = {}".format(values, target_func_curr_value, curr_step))
                    # log.debug("grad = {};\n".format(gradient))

        time_end = time.time()

        log.info("Time of run: {:.0f} sec. Integral quality current: {}, min: {}".format(time_end - time_start,
                                                                                         target_func_curr_value,
                                                                                         target_func_min_value))

        if iteration == max_iter:
            log.warning("Maximum number of iterations exceeded. Returned values may be suboptimal")
            values = best_values

        return values
