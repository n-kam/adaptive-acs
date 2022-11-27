class ListIntegrator(object):

    def __init__(self):
        pass

    """ 
    "Интегрируем" две функции, представленные как соразмерные листы значений
    """

    @staticmethod
    def calc(list_1: list[float], list_2: list[float]) -> float:
        integral_sum = 0

        if len(list_2) != len(list_1):
            raise Exception("List sizes mismatch")

        for i in range(len(list_1)):
            integral_sum += abs(list_1[i] - list_2[i])

        return integral_sum
