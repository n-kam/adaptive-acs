from Classes.UDP import UDPIn
from Classes.UDP import UDPOut
import logging as log

log.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s', level=log.INFO)


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
