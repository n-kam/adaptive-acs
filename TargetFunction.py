import logging as log

from control import matlab

from ListIntegrator import ListIntegrator
from TransferFunction import TransferFunction


class TargetFunction(object):
    log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.DEBUG)
    list_integrator = ListIntegrator()

    def __init__(self, model_transient_response: list, nominator_len: int, denominator_len: int):
        self.model_transient_response = model_transient_response
        self.nominator_len = nominator_len
        self.denominator_len = denominator_len

    def tf(self, ab_values: list) -> float:

        if (self.nominator_len + self.denominator_len) != len(ab_values):
            raise Exception("Dimensions mismatch")

        # Разделяем числитель и знаменатель из одного входного массива
        nominator = ab_values[:self.nominator_len]
        log.debug("nominator: {}".format(nominator))
        denominator = ab_values[self.nominator_len:]
        log.debug("denominator: {}".format(denominator))

        # Находим переходную характеристику для теоретической (подбираемой) функции с высокой частотой дискретизации
        matlab_transfer_function = matlab.tf(nominator, denominator)
        timeline = [x / 1000 for x in range(0, 11000)]
        # log.debug("timeline:{}".format(timeline))
        [y, x] = matlab.step(matlab_transfer_function, timeline)
        y = list(y)
        x = list(x)
        # log.debug("y: ".format(y))

        # Выделяем из этой переходной характеристики только те временнЫе точки, которые имеются в модельной п.х.
        # также собираем список чисто из значений модельной п.х. из списка "время / входной сигнал / выходной сигнал"
        optimization_transient_response_list = list()
        model_transient_response_list = list()
        for i in range(len(self.model_transient_response)):
            time_value = round(self.model_transient_response[i][0], 3)
            index = x.index(time_value)
            optimization_transient_response_list.append(y[index])
            model_transient_response_list.append(self.model_transient_response[i][2])
            # log.debug("time_value: {}".format(time_value))

        return self.list_integrator.calc(model_transient_response_list, optimization_transient_response_list)
