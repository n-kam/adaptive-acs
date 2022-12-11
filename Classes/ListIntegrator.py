def calc(list_1: list[float], list_2: list[float]) -> float:
    """
    Расчет интеграла разности двух функций, представленных в виде списков одинакового размера из значений этих функций при одних и тех же значениях входной величины.

    :param list_1: Список значений первой функции.
    :param list_2: Список значений второй функции.
    :return: Интеграл разности.
    """

    integral_sum = 0

    if len(list_2) != len(list_1):
        raise Exception("List sizes mismatch")

    for i in range(len(list_1)):
        integral_sum += abs(list_1[i] - list_2[i])

    return integral_sum
