import logging as log

from control import matlab

from Classes import ListIntegrator


class TargetFunction(object):
    log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.INFO)

    def __init__(self, model_transient_response_values: list[float], nominator_len: int, denominator_len: int):
        """
        Инициализация интегратора.

        :param model_transient_response_values: Список из значений переходной характеристики, снятой с модели.
        :param nominator_len: Длина списка коэффициентов числителя передаточной функции, по которой в tf() общий список коэффициентов будет разделен обратно на числитель и знаменатель.
        :param denominator_len: Длина списка коэффициентов знаменателя передаточной функции.
        """
        self.model_transient_response_values = model_transient_response_values
        self.nominator_len = nominator_len
        self.denominator_len = denominator_len
        # todo: переделать так, чтобы не было хардкода. список может получиться неправильной длины:
        self.timeline = [x / 2 for x in range(0, 20)]

    def tf(self, ab_values: list) -> float:
        """
        Целевая функция.

        :param ab_values: Числитель и знаменатель передаточной функции, объединенный в общий список коэффициентов.
        :return: Интегральная разница между переходной характеристикой, снятой с модели и подобранной оптимизатором.
        """
        # Разделяем числитель и знаменатель из одного входного массива
        nominator = ab_values[:self.nominator_len]
        denominator = ab_values[self.nominator_len:]

        # Находим переходную характеристику для теоретической (подбираемой) функции
        matlab_transfer_function = matlab.tf(nominator, denominator)
        [y, x] = matlab.step(matlab_transfer_function, self.timeline)
        optimization_transient_response_values = y

        return ListIntegrator.calc(self.model_transient_response_values, optimization_transient_response_values)
