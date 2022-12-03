from random import random

from Classes.Optimization import Optimization
from Classes.TargetFunction import TargetFunction
from Classes.TransferFunction import TransferFunction
from Classes.UDPIn import UDPIn
from Classes.UDPOut import UDPOut
import logging as log


class IdentifyOOC(object):
    import time
    log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.DEBUG)

    def __init__(self,
                 ip_in: str, ip_out: str,
                 port_in: int, port_set_point: int, port_out: int,
                 run_time_sec=10,
                 source_file="",
                 transfer_func_nominator_max_order=5,
                 transfer_func_denominator_max_order=5,
                 preprocess_time_step=0.5,
                 values_precision=3):

        self.udp_input_socket = UDPIn(ip_in, port_in)
        self.udp_set_point_socket = UDPIn(ip_in, port_set_point)
        self.udp_output_socket = UDPOut(ip_out, port_out)
        self.run_time_sec = run_time_sec
        self.source_file = source_file
        self.TRANSFER_FUNC_NOM_MAX_ORDER = transfer_func_nominator_max_order
        self.TRANSFER_FUNC_DENOM_MAX_ORDER = transfer_func_denominator_max_order
        self.PREPROCESS_TIME_STEP = preprocess_time_step
        self.VALUES_PRECISION = values_precision
        log.info("Start IdenfifyOOC.py")

    '''
    Снимаем переходную характеристику. Если задано имя файла, то считываем из него, иначе, снимаем с модели
    '''

    def __read_transient_response(self, source_file="") -> list[list[float, float, float]]:
        output_signal_list = list()

        if source_file == "":
            log.info("Reading transient response from matlab model")
            log.info("Waiting for the model to start...")
            set_point_signal = 1.0
            output_signal = 0.0

            time_start = self.time.time()
            time_now = time_start

            while (time_now - time_start) < self.run_time_sec:
                time_now = self.time.time()

                input_signal = set_point_signal - output_signal  # Negative feedback
                self.udp_input_socket.send(input_signal)

                output_signal = self.udp_output_socket.rcv()
                output_signal_list.append([time_now - time_start, set_point_signal, output_signal])

                log.info("{}: set_point={}, input_signal={}, output_signal={}".format(time_now - time_start,
                                                                                      set_point_signal, input_signal,
                                                                                      output_signal))

            log.info("output_signal_list size:{}".format(len(output_signal_list)))

        else:
            # Считываем файл
            log.info("Reading transient response from file {}".format(source_file))
            file = open(source_file, "r")

            for line in file.read().splitlines():
                lines = line.strip("[]").split(",")
                time = float(lines[0])
                input_val = float(lines[1])
                output_val = float(lines[2])
                output_signal_list.append([time, input_val, output_val])

        return output_signal_list

    '''Предварительная обработка данных. Нам не нужно 1000 точек, чтобы описать функцию 5-й степени. Переходной 
    процесс длится до 10 секунд. Поэтому можно проредить список, сократив точность до 1/2 секунды. Также можно 
    округлить данные до 3 знака после запятой '''

    def __preprocess(self, values_list: list[list[float, float, float]]) -> list[float]:
        log.info("Preprocessing transient response data")

        time_step = self.PREPROCESS_TIME_STEP
        values_precision = self.VALUES_PRECISION
        time_precision = len(str(time_step).removeprefix("0."))
        # log.debug("time prec: {}; val prec: {}".format(time_precision, values_precision))
        desired_time = 0.0
        time_difference = 1e10
        new_values_list = list()

        # Проходимся по списку снятых значений и находим ближайшие значения времен для каждого желаемого времени (от
        # 0 с шагом time_step). Складываем последний столбец из найденных значений в новый список
        for i in range(len(values_list)):
            if time_difference > abs(desired_time - values_list[i][0]):
                time_difference = abs(desired_time - values_list[i][0])
            else:
                # new_values_list.append([round(values_list[i][0], time_precision),
                #                         round(values_list[i][1], values_precision),
                #                         round(values_list[i][2], values_precision)])
                new_values_list.append(round(values_list[i][2], values_precision))
                desired_time += time_step
                time_difference = 1e10

        return new_values_list

    @staticmethod
    def __save_transient_response_to_file(output_file: str, values_list: list):
        log.info("Saving transient response to file {}".format(output_file))
        file = open(output_file, "a")
        for i in range(len(values_list)):
            file.write(str(values_list[i]) + "\n")

    '''
    Временный публичный метод, выдающий два приватных наружу. Для дебага
    '''

    def read_transient_response_and_save_to_file(self, output_basename="h_model_") -> str:
        output_file = output_basename + str(self.time.time()) + ".txt"
        self.__save_transient_response_to_file(output_file, self.__read_transient_response())
        return output_file

    '''
    Основной метод, который вызывает все служебные методы
    '''

    def identify(self) -> TransferFunction:
        # Создаем списки рандомных начальных значений для числителя и знаменателя передаточной функции
        nominator = list()
        denominator = list()
        # todo: переделать так, чтобы не было хардкода для сдвига начальных значений (какие обычно у коэффициентов
        #  передаточных функций диапазоны, чтобы можно было выбрать выбрать оптимальные пределы для рандома начальных
        #  значений?):
        multiplication_shift = 5
        addition_shift = 0
        for i in range(self.TRANSFER_FUNC_NOM_MAX_ORDER + 1):
            nominator.append(random() * multiplication_shift + addition_shift)
        for i in range(self.TRANSFER_FUNC_DENOM_MAX_ORDER + 1):
            denominator.append(random() * multiplication_shift + addition_shift)

        model_transient_response = self.__read_transient_response(self.source_file)
        model_transient_response_values = self.__preprocess(model_transient_response)
        log.debug("Preprocessed model transient response: {}".format(model_transient_response_values))

        # Кладем числитель и знаменатель передаточной функции в один список для передачи его в оптимизатор
        ab_values = list()
        ab_values.extend(nominator)
        ab_values.extend(denominator)
        # log.debug("ab_values: {}".format(ab_values))

        # Вызов оптимизатора
        log.info("Initial coefficients: nominator:{}, denominator:{}".format(nominator, denominator))
        optimization_target_func = TargetFunction(model_transient_response_values, len(nominator), len(denominator))
        optimization = Optimization()
        ab_values = optimization.adam(optimization_target_func.tf, ab_values)

        # Разделяем числитель и знаменатель из одного входного списка на два
        nominator = ab_values[:len(nominator)]
        denominator = ab_values[len(nominator):]
        log.info("Final (optimized) coefficients: nominator:{}, denominator:{}".format(nominator, denominator))
        optimization_transfer_function = TransferFunction(nominator, denominator)

        return optimization_transfer_function
