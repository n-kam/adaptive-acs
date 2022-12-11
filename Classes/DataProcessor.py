import logging as log

log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.INFO)


def preprocess(values_list: list[list[float, float, float]], time_step: float = 0.5) -> tuple[list[float], list[float]]:
    """
    Предварительная обработка данных.

    Проходимся по списку снятых значений и находим ближайшие значения времен для каждого желаемого времени (от 0 с шагом time_step). Для найденных значений времени складываем значения переходной характеристики из последнего столбца в новый список.

    :param values_list: Исходная переходная характеристика. Матрица, в которой каждая строка является списком [время, входной сигнал, выходной сигнал].
    :param time_step: Шаг времени, с которым проходимся по исходной матрице значений, выбирая ближайшее имеющееся время.
    :return: Кортеж из двух списков: списка найденных значений выходного сигнала, списка найденных значений времени.
    """
    log.info("Предварительная обработка входных данных...")

    desired_time = 0.0
    time_difference = 1e10
    new_time_values_list = list()
    new_values_list = list()

    for i in range(len(values_list)):
        if abs(desired_time - values_list[i][0]) > time_difference:
            new_values_list.append(values_list[i - 1][2])
            new_time_values_list.append(desired_time)
            desired_time += time_step
        time_difference = abs(values_list[i][0] - desired_time)

    return new_values_list, new_time_values_list

# def postprocess(nominator: list[float],
#                denominator: list[float],
#                rounding_precision=1) -> tuple[list[float], list[float]]:
#    """
#    Постобработка данных. Разделить все величины на коэффициент перед старшей степенью числителя. Округлить до
#    rounding_precision знака после запятой
#
#    :param nominator:
#    :param denominator:
#    :param rounding_precision:
#    :return:
#    """
#    nom0 = nominator[0]
#    for i in range(len(nominator)):
#        nominator[i] = round(nominator[i] / nom0, rounding_precision)
#    for i in range(len(denominator)):
#        denominator[i] = round(denominator[i] / nom0, rounding_precision)
#
#    return nominator, denominator
#
