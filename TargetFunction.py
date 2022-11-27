import logging as log

from control import matlab

from ListIntegrator import ListIntegrator


class TargetFunction(object):
    log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.DEBUG)
    list_integrator = ListIntegrator()

    def __init__(self, model_transient_response: list, nominator_len: int, denominator_len: int):
        self.model_transient_response = model_transient_response
        self.nominator_len = nominator_len
        self.denominator_len = denominator_len

        # Выделяем из списка "время / входная / выходная величина" только последний столбец
        model_transient_response_list = list()
        for i in range(len(self.model_transient_response)):
            model_transient_response_list.append(self.model_transient_response[i][2])

        self.model_transient_response_list = model_transient_response_list

    def tf(self, ab_values: list) -> float:

        if (self.nominator_len + self.denominator_len) != len(ab_values):
            raise Exception("Dimensions mismatch")

        # Разделяем числитель и знаменатель из одного входного массива
        nominator = ab_values[:self.nominator_len]
        # log.debug("nominator: {}".format(nominator))
        denominator = ab_values[self.nominator_len:]
        # log.debug("denominator: {}".format(denominator))

        # Находим переходную характеристику для теоретической (подбираемой) функции с высокой частотой дискретизации
        matlab_transfer_function = matlab.tf(nominator, denominator)
        # todo: переделать так, чтобы не было хардкода. список может получиться неправильной длины:
        timeline = [x / 2 for x in range(0, 20)]
        [y, x] = matlab.step(matlab_transfer_function, timeline)
        optimization_transient_response_list = list(y)
        # log.debug("Trans. resp. sizes should match. For model it is: {}; for optimizator: {}".format(
        #     len(self.model_transient_response_list), len(y)))

        return self.list_integrator.calc(self.model_transient_response_list, optimization_transient_response_list)
