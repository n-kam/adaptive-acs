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


def postprocess(nominator: list[float],
                denominator: list[float],
                rounding_precision=1) -> tuple[list[float], list[float]]:
    """
    Постобработка данных. Недоделано, пока отключена.

    :param nominator:
    :param denominator:
    :param rounding_precision:
    :return:
    """

    nominator = list(nominator)
    denominator = list(denominator)

    division_is_ok = True
    min_coef = 1e10

    for i in range(len(nominator)):
        if 1 < nominator[i]:
            min_coef = min(min_coef, nominator[i])
        if 1 < nominator[i] < 10:
            division_is_ok = False

    for i in range(len(denominator)):
        if 1 < denominator[i] < 10:
            division_is_ok = False

    if division_is_ok:
        for i in range(len(nominator)):
            if nominator[0] < 1:
                nominator.pop(0)
        for i in range(len(denominator)):
            if denominator[0] < 1:
                denominator.pop(0)

    for i in range(len(nominator)):
        nominator[i] /= min_coef
    for i in range(len(denominator)):
        denominator[i] /= min_coef

    if division_is_ok:
        for i in range(len(nominator)):
            nominator[i] = round(nominator[i], rounding_precision)
        for i in range(len(denominator)):
            denominator[i] = round(denominator[i], rounding_precision)

    for i in range(len(nominator)):
        if nominator[0] == 0:
            nominator.pop(0)

    for i in range(len(denominator)):
        if denominator[0] == 0:
            denominator.pop(0)

    return nominator, denominator
