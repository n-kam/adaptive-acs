import logging as log

from control import matlab

from Classes.ListIntegrator import ListIntegrator


class TargetFunction(object):
    log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.DEBUG)
    list_integrator = ListIntegrator()

    def __init__(self, model_transient_response_values: list, nominator_len: int, denominator_len: int):
        self.model_transient_response_values = model_transient_response_values
        self.nominator_len = nominator_len
        self.denominator_len = denominator_len
        # todo: переделать так, чтобы не было хардкода. список может получиться неправильной длины:
        self.timeline = [x / 2 for x in range(0, 20)]

    def tf(self, ab_values: list) -> float:

        # if (self.nominator_len + self.denominator_len) != len(ab_values):
        #     raise Exception("Dimensions mismatch")

        # Разделяем числитель и знаменатель из одного входного массива
        nominator = ab_values[:self.nominator_len]
        # log.debug("nominator: {}".format(nominator))
        denominator = ab_values[self.nominator_len:]
        # log.debug("denominator: {}".format(denominator))

        # Находим переходную характеристику для теоретической (подбираемой) функции с высокой частотой дискретизации
        matlab_transfer_function = matlab.tf(nominator, denominator)
        [y, x] = matlab.step(matlab_transfer_function, self.timeline)
        optimization_transient_response_values = list(y)
        # log.debug("Trans. resp. sizes should match. For model it is: {}; for optimizator: {}".format(
        #     len(self.model_transient_response_list), len(y)))

        return self.list_integrator.calc(self.model_transient_response_values, optimization_transient_response_values)
