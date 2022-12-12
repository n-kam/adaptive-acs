from Classes import DataProcessor, Plotter
from Classes.Optimization import Optimization
from Classes.TargetFunction import TargetFunction
from Classes.TransferFunction import TransferFunction
import logging as log

log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.INFO)
adam = "adam"
classic = "classic"
gauss_seidel = "gauss_seidel"


def identify(model_transient_response: list[list[float, float, float]],
             algorithm=adam,
             transfer_func_nominator_max_order=5,
             transfer_func_denominator_max_order=5,
             preprocess_time_step=0.5,
             results_plotting_enabled=False):
    """
    Идентификация ОУ.

    :param model_transient_response: Переходная характеристика модели в виде списка из списков вида [время, входной сигнал, выходной сигнал]
    :param algorithm: Алгоритм оптимизации.
    :param transfer_func_nominator_max_order: Максимальная степень p в числителе передаточной функции.
    :param transfer_func_denominator_max_order: Максимальная степень p в знаменателе передаточной функции.
    :param preprocess_time_step: Шаг времени, с которым из всех снятых точек переходной характеристики создается сокращенная выборка.
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
     model_transient_response_times] = DataProcessor.preprocess(model_transient_response, preprocess_time_step)

    # Кладем числитель и знаменатель передаточной функции в один список для передачи его в оптимизатор
    ab_values = list()
    ab_values.extend(nominator)
    ab_values.extend(denominator)

    # Вызов оптимизатора
    log.info("Исходные значения коэффициентов. Числитель: {}. Знаменатель: {}".format(nominator, denominator))
    optimization_target_func = TargetFunction(model_transient_response_values, len(nominator), len(denominator))
    optimization = Optimization()
    if algorithm == adam:
        log.warning("ИСПОЛЬЗОВАНИЕ ГРАД. СПУСКА АДАМА НЕ РЕКОМЕНДУЕТСЯ")
        ab_values = optimization.adam(optimization_target_func.tf, ab_values)
    elif algorithm == classic:
        ab_values = optimization.classic(optimization_target_func.tf, ab_values)
    elif algorithm == gauss_seidel:
        log.warning("ИСПОЛЬЗОВАНИЕ АЛГОРИТМА ГАУССА-ЗЕЙДЕЛЯ НЕ РЕКОМЕНДУЕТСЯ")
        ab_values = optimization.gauss_seidel(optimization_target_func.tf, ab_values)
    else:
        raise Exception("Неизвестный алгоритм:{}".format(algorithm))

    # Разделяем числитель и знаменатель из одного списка на два
    nominator = ab_values[:len(nominator)]
    denominator = ab_values[len(nominator):]

    # Постобработка данных # todo: доделать в включить
    # log.debug("Optimized coefficients without postprocessing: "
    #           "nominator:{}, denominator:{}".format(nominator, denominator))
    # nominator, denominator = DataProcessor.postprocess(nominator, denominator)
    log.info("Подобранные значения коэффициентов. Числитель: {}. Знаменатель: {}".format(nominator, denominator))
    optimization_transfer_function = TransferFunction(nominator, denominator)

    # Строим графики. Красный - модель. Зеленый - подобранный. При хорошем подборе они могут практически
    # накладываться друг на друга. Приближайте, если хотите убедиться, что оба построились
    if results_plotting_enabled:
        Plotter.plot_results(model_transient_response_times,
                             model_transient_response_values,
                             nominator,
                             denominator)

    return optimization_transfer_function
