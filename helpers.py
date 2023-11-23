import math

import numdifftools
from control import matlab
from matplotlib import pyplot
import logging
import logging as log
import numpy
import socket
import struct

log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.INFO)


class UDPIn(object):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    def send(self, signal):
        self.sock.sendto(struct.pack('d', signal), (self.ip, self.port))
        return True


class UDPOut(object):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __init__(self, ip: str, port: int):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))

    def rcv(self):
        byte_signal = self.sock.recvfrom(8)[0]
        return struct.unpack('d', byte_signal)[0]


def list_integrate(list_1: list[float], list_2: list[float]) -> float:
    """
    Расчет интеграла разности двух функций, представленных в виде списков одинакового размера из значений этих функций
    при одних и тех же значениях входной величины.

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


def plot_results(model_response_times: list[float],
                 model_response_values: list[float],
                 nominator: list[float],
                 denominator: list[float]) -> None:
    """
    Построение графиков переходной характеристики, снятой с модели и подобранной теоретически.

    ПХ модели строится красным цветом. Теоретическая - зеленым.

    :param model_response_times: Список из точек времени, для которых строить график.
    :param model_response_values: Список значений модельной переходной характеристики,
    соответствующей заданным точкам времени.
    :param nominator: Список коэффициентов числителя теоретически подобранной передаточной функции.
    :param denominator: Список коэффициентов знаменателя теоретически подобранной передаточной функции.
    """
    # Очистить логи от мусорных дебажных сообщений из внутренних библиотек pyplot'а
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)

    optimization_tf = matlab.tf(nominator, denominator)
    [tf_values, _] = matlab.step(optimization_tf, model_response_times)

    # todo: избавиться от хардкода:
    pyplot.xticks(numpy.arange(0, 11, 1))
    pyplot.yticks(numpy.arange(0, 1.1, 0.1))

    pyplot.grid(True)
    model_line_color = 'black'
    theor_line_color = 'red'
    pyplot.title("Переходные характеристики")
    pyplot.xlabel("t, с")
    pyplot.ylabel("h(t)")

    pyplot.plot(model_response_times, model_response_values, model_line_color, label="Модельная")
    pyplot.plot(model_response_times, tf_values, theor_line_color, label="Подобранная")

    log.info("На графике: переходная характеристика модельная - {}, подобранная - {}".format(model_line_color,
                                                                                             theor_line_color))
    pyplot.legend(loc="lower right")
    pyplot.show()


def read_tr_from_file(source_file_name: str = "") -> list[list[float, float, float]]:
    """
    Считать переходную характеристику из файла.

    :param source_file_name: Имя файла.
    :return: Переходная характеристика в формате списка из списков вида [время, входной сигнал, выходной сигнал]
    """
    output_signal_list = list()

    log.info("Считываем переходную характеристику из файла {}".format(source_file_name))
    file = open(source_file_name, "r")

    for line in file.read().splitlines():
        lines = line.strip("[]").split(",")
        time = float(lines[0])
        input_val = float(lines[1])
        output_val = float(lines[2])
        output_signal_list.append([time, input_val, output_val])

    return output_signal_list


def read_tr_from_model(ip_in: str = "localhost",
                       ip_out: str = "localhost",
                       port_in: int = 0,
                       port_set_point: int = 0,
                       port_out: int = 0,
                       run_time_sec: float = 10,
                       output_file_name: str = "") -> list[list[float, float, float]]:
    """
    Снять переходную характеристику с модели по UDP. Если задано имя файла, сохранить записать в него П.Х.

    :param ip_in: Адрес входного сигнала.
    :param ip_out: Адрес выходного сигнала.
    :param port_in: Порт входного сигнала.
    :param port_set_point: Порт уставки
    :param port_out: Порт выходного сигнала.
    :param run_time_sec: Время, в течение которого снимать данные с модели.
    :param output_file_name: Имя файла, в который записать выходные данные.
    :return: Переходная характеристика в формате списка из списков вида [время, входной сигнал, выходной сигнал]
    """
    import time
    udp_input_socket = UDPIn(ip_in, port_in)
    udp_set_point_socket = UDPIn(ip_in, port_set_point)
    udp_output_socket = UDPOut(ip_out, port_out)
    output_signal_list = list()

    log.info("Снимаем переходную характеристику с модели MATLAB.")
    log.info("Ожидание запуска модели...")
    set_point_signal = 1.0
    output_signal = udp_output_socket.rcv()
    log.info("Связь с моделью установлена. Снимаем измерения...")

    time_start = time.time()
    time_now = time_start

    while (time_now - time_start) < run_time_sec:
        time_now = time.time()

        input_signal = set_point_signal - output_signal  # Negative feedback
        udp_input_socket.send(input_signal)
        udp_set_point_socket.send(set_point_signal)

        output_signal = udp_output_socket.rcv()
        output_signal_list.append([time_now - time_start, set_point_signal, output_signal])

        log.debug("{:.5f}: Уставка: {:.5f}. Входной сигнал: {:.5f}. Выходной сигнал: {:.5f}"
                  "".format(time_now - time_start, set_point_signal, input_signal, output_signal))

    log.info("Количество снятых точек: {}".format(len(output_signal_list)))

    if output_file_name != "":
        log.info("Сохраняем снятые данные в файл {}".format(output_file_name))
        file = open(output_file_name, "a")
        for i in range(len(output_signal_list)):
            file.write(str(output_signal_list[i]) + "\n")

    return output_signal_list


def preprocess_data(values_list: list[list[float, float, float]], time_step: float = 0.5) \
        -> tuple[list[float], list[float]]:
    """
    Предварительная обработка данных.

    Проходимся по списку снятых значений и находим ближайшие значения времен для каждого желаемого времени
    (от 0 с шагом time_step). Для найденных значений времени складываем значения переходной характеристики из
    последнего столбца в новый список.

    :param values_list: Исходная переходная характеристика. Матрица, в которой каждая строка является списком
    [время, входной сигнал, выходной сигнал].
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


def postprocess_data(nominator: list[float],
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


def partial_derivative(func: callable(list[float]), values: list[float], mutable_var_number: int,
                       value_shift: float = 1e-10) -> float:
    """
    Рассчитать частную производную по одной из переменных быстрым способом. Метод увеличивает выбранную переменную
    на очень малую величину value_shift и рассчитывает dy/dx.

    :param func: Вызываемоая функция.
    :param values: Список всех переменных вызываемой функции.
    :param mutable_var_number: Порядковый номер в списке values переменной, по которой необходимо рассчитать
    частную производную.
    :param value_shift: Величина, на которую изменяется переменная для расчета производной
    :return: Значение частной производной.
    """
    values_shifted_up = list(values)
    values_shifted_down = list(values)
    values_shifted_up[mutable_var_number] += value_shift
    values_shifted_down[mutable_var_number] -= value_shift
    partial_derivative_value = ((func(values_shifted_up) - func(values_shifted_down)) / (
            values_shifted_up[mutable_var_number] - values_shifted_down[mutable_var_number]))

    return partial_derivative_value


def gradient(func: callable(list[float]), values: list[float]) -> list[float]:
    """
    Для каждого элемента из списка переменных рассчитать частную производную функции func и сложить результаты в
    один список.

    :param func: Вызываемая функция.
    :param values: Список переменных вызываемой функции.
    :return: Список-вектор градиента.
    """
    grad = list()
    for i in range(len(values)):
        grad.append(partial_derivative(func, values, i))

    return grad


def test_gradient() -> None:
    """
    Метод для тестов и дебага. Сравнивает градиент определенной функции, рассчитанный быстрым способом с градиентом,
    рассчитанным с помощью библиотеки numdifftools.
    """

    def fun(vals) -> float:
        x = vals[0]
        y = vals[1]
        z = vals[2]
        return numpy.sin(x + 2 * y) + 2 * numpy.sqrt(x * y * z)

    xyz_vals = [math.pi / 2, math.pi * 3 / 2, 3]

    print("fast pd 0: ", partial_derivative(fun, xyz_vals, 0))
    print("fast pd 1: ", partial_derivative(fun, xyz_vals, 1))
    print("fast pd 2: ", partial_derivative(fun, xyz_vals, 2))
    print("fast grad: ", gradient(fun, xyz_vals))
    xyz_vals = numpy.array(xyz_vals)
    print("ndt grad: ", numdifftools.Gradient(fun)(xyz_vals))

# Раскомментировать для тестирования:
# test()
