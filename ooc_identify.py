import optimization
from control import matlab
from model import TransferFunction
import helpers
import logging as log

log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.INFO)


class TargetFunction(object):

    def __init__(self, model_transient_response_values: list[float], nominator_len: int, denominator_len: int):
        """
        Инициализация интегратора.

        :param model_transient_response_values: Список из значений переходной характеристики, снятой с модели.
        :param nominator_len: Длина списка коэффициентов числителя передаточной функции, по которой в tf()
        общий список коэффициентов будет разделен обратно на числитель и знаменатель.
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
        [y, _] = matlab.step(matlab_transfer_function, self.timeline)
        optimization_transient_response_values = y

        return helpers.list_integrate(self.model_transient_response_values,
                                      optimization_transient_response_values)


def identify(model_transient_response: list[list[float, float, float]],
             algorithm=optimization.Algorythm.adam,
             transfer_func_nominator_max_order=5,
             transfer_func_denominator_max_order=5,
             preprocess_time_step=0.5,
             results_plotting_enabled=False):
    """
    Идентификация ОУ.

    :param model_transient_response: Переходная характеристика модели в виде списка из списков вида
    [время, входной сигнал, выходной сигнал]
    :param algorithm: Алгоритм оптимизации.
    :param transfer_func_nominator_max_order: Максимальная степень p в числителе передаточной функции.
    :param transfer_func_denominator_max_order: Максимальная степень p в знаменателе передаточной функции.
    :param preprocess_time_step: Шаг времени, с которым из всех снятых точек переходной характеристики создается
    сокращенная выборка.
    :param results_plotting_enabled: Строить ли графики переходной характеристики модели и теоретической.
    :return: Переходная характеристика в виде экземпляра класса TransferFunction.
    """
    # Создаем списки начальных значений для числителя и знаменателя передаточной функции необходимой длины
    nominator = list()
    denominator = list()
    for i in range(transfer_func_nominator_max_order + 1):
        nominator.append(10)
    for i in range(transfer_func_denominator_max_order + 1):
        denominator.append(10)

    # Предварительная обработка входных данных
    [model_transient_response_values,
     model_transient_response_times] = helpers.preprocess_data(model_transient_response, preprocess_time_step)

    # Кладем числитель и знаменатель передаточной функции в один список для передачи его в оптимизатор
    ab_values = list()
    ab_values.extend(nominator)
    ab_values.extend(denominator)

    # Вызов оптимизатора
    log.info("Исходные значения коэффициентов. Числитель: {}. Знаменатель: {}".format(nominator, denominator))
    optimization_target_func = TargetFunction(model_transient_response_values, len(nominator), len(denominator))
    ab_values = optimization.start(optimization_target_func.tf, ab_values, algorithm)

    # Разделяем числитель и знаменатель из одного списка на два
    nominator = ab_values[:len(nominator)]
    denominator = ab_values[len(nominator):]

    # Постобработка данных
    # todo: доделать в включить
    # log.debug("Optimized coefficients without postprocessing: "
    #           "nominator:{}, denominator:{}".format(nominator, denominator))
    # nominator, denominator = postprocess_data(nominator, denominator)
    log.info("Подобранные значения коэффициентов. Числитель: {}. Знаменатель: {}".format(nominator, denominator))
    optimization_transfer_function = TransferFunction(nominator, denominator)

    # Строим графики. Черный - модель, красный - подобранный. При хорошем подборе они могут практически
    # накладываться друг на друга. Приближайте, если хотите убедиться, что оба построились
    if results_plotting_enabled:
        helpers.plot_results(model_transient_response_times,
                             model_transient_response_values,
                             nominator,
                             denominator)

    return optimization_transfer_function
