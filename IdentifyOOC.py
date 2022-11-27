from Optimization import Optimization
from TargetFunction import TargetFunction
from TransferFunction import TransferFunction
from UDPIn import UDPIn
from UDPOut import UDPOut
import logging as log


class IdentifyOOC(object):
    import time
    log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.DEBUG)
    TRANSFER_FUNC_MAX_ORDER = 5

    def __init__(self, ip_in: str, ip_out: str, port_in: int, port_set_point: int, port_out: int, run_time_sec=10,
                 source_file=""):
        self.udp_input_socket = UDPIn(ip_in, port_in)
        self.udp_set_point_socket = UDPIn(ip_in, port_set_point)
        self.udp_output_socket = UDPOut(ip_out, port_out)
        self.run_time_sec = run_time_sec
        self.source_file = source_file
        log.info("Start IdenfifyOOC.py")

    '''
    Снимаем переходную характеристику. Если задано имя файла, то считываем из него, иначе, снимаем с модели
    '''

    def __read_transient_response(self, source_file="") -> list[list[float, float, float]]:
        output_signal_list = list()

        if source_file == "":
            log.info("Reading transient response from matlab model")
            set_point_signal = 1.0

            log.info("Waiting for the model to start...")
            output_signal = self.udp_output_socket.rcv()
            self.udp_set_point_socket.send(set_point_signal)

            time_start = self.time.time()
            time_now = time_start

            while (time_now - time_start) < self.run_time_sec:
                time_now = self.time.time()

                input_signal = set_point_signal - output_signal  # Negative feedback
                self.udp_input_socket.send(input_signal)

                output_signal = self.udp_output_socket.rcv()
                output_signal_list.append([time_now - time_start, set_point_signal, output_signal])

                log.info(time_now - time_start, ": set_point=", set_point_signal, ", input_signal=", input_signal,
                         ", output_signal=", output_signal)
                log.info("{}: set_point={}, input_signal={}, output_signal={}".format(time_now - time_start,
                                                                                      set_point_signal, input_signal,
                                                                                      output_signal))

            # print("output_signal_list:", output_signal_list)
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

    '''
    Нормализуем данные, убирая нулевые значения в начале и сдвигая выходные величины, если они запаздывают 
    относительно входных. Снятие данных переделано, больше не требуется
    '''

    # @staticmethod
    # def __normalize(values_list: list[list[float, float, float]]) -> list[list[float, float, float]]:
    #     log.info("Normalizing transient response data")
    #
    #     # Remove first reading with time = 0
    #     if values_list[0][0] == 0.0:
    #         values_list.pop(0)
    #
    #     # # remove values from start if set point or output equals 0
    #     # i = 0
    #     # while (i < len(values_list)) & ((values_list[0][1] == 0.0) | (values_list[0][2] == 0.0)):
    #     #     values_list.pop(0)
    #
    #     return values_list

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
        # Создаем списки начальных значений определенного размера для числителя и знаменателя передаточной функции
        nominator = list([1.0] * self.TRANSFER_FUNC_MAX_ORDER)
        # nominator = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
        denominator = list([1.0] * self.TRANSFER_FUNC_MAX_ORDER)

        model_transient_response = self.__read_transient_response(self.source_file)
        # model_transient_response = self.__normalize(model_transient_response)

        # Кладем числитель и знаменатель передаточной функции в один список для передачи его в оптимизатор
        ab_values = list()
        ab_values.extend(nominator)
        ab_values.extend(denominator)
        log.debug("ab_values: {}".format(ab_values))

        # Вызов оптимизатора
        optimization_target_func = TargetFunction(model_transient_response, len(nominator), len(denominator))
        log.debug("opt targ func: {}".format(optimization_target_func))
        optimization = Optimization()
        ab_values = optimization.adam(optimization_target_func.tf, ab_values)

        # Разделяем числитель и знаменатель из одного входного списка на два
        nominator = ab_values[:len(nominator)]
        log.debug("nominator: {}".format(nominator))
        denominator = ab_values[len(nominator):]
        log.debug("denominator: {}".format(denominator))
        optimization_transfer_function = TransferFunction(nominator, denominator)

        return optimization_transfer_function
