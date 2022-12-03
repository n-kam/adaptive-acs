import logging as log


class ListIntegrator(object):
    log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.DEBUG)

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

        # log.debug("list 1 (len = {}):{}".format(len(list_1), list_1))
        # log.debug("list 2 (len = {}):{}".format(len(list_2), list_2))

        for i in range(len(list_1)):
            # log.debug("list1[{}]: {}".format(i, list_1[i]))
            # log.debug("list2[{}]: {}".format(i, list_2[i]))

            integral_sum += abs(list_1[i] - list_2[i])
            # log.debug("curr diff: {}".format(abs(list_1[i] - list_2[i])))
            # log.debug("curr sum: {}".format(integral_sum))

        # exit(228)

        return integral_sum
