import os.path

from Classes import DataReader, IdentifyOOC
from Classes.TransferFunction import TransferFunction

# CONFIGURATION

kp = 0.0
ki = 0.0
kd = 0.0
set_point = 0.0
UDP_IP_OUT = "127.0.0.1"
UDP_IP_IN = "127.0.0.1"
# UDP_IP_OUT = "0.0.0.0"
# UDP_IP_IN = "192.168.122.200"           # У меня другие ip-шники, т.к. матлаб в виртуалке. Не удалять.  / n-kam
UDP_IP_SEND_SET_POINT = UDP_IP_IN
UDP_PORT_IN = 30000
UDP_PORT_SET_POINT = 40000
UDP_PORT_OUT = 20000
RUN_TIME = 9.9
MODEL_DATA_FILENAME = "Assets/h_model.txt"

# ШАГ 1. Идентификация объекта управления (определение его W(p))

# Если файл существует, считываем данные из него. Если нет, то считываем из модели и сохраняем в него.
if os.path.exists(MODEL_DATA_FILENAME):
    model_transient_response = DataReader.read_tr_from_file(MODEL_DATA_FILENAME)
else:
    model_transient_response = DataReader.read_tr_from_model(ip_in=UDP_IP_IN,
                                                             ip_out=UDP_IP_OUT,
                                                             port_in=UDP_PORT_IN,
                                                             port_out=UDP_PORT_OUT,
                                                             port_set_point=UDP_PORT_SET_POINT,
                                                             run_time_sec=RUN_TIME,
                                                             output_file_name=MODEL_DATA_FILENAME)

# Идентификация ОУ
w_ooc = IdentifyOOC.identify(model_transient_response,
                             algorithm=IdentifyOOC.classic,
                             transfer_func_nominator_max_order=1,
                             transfer_func_denominator_max_order=3,
                             results_plotting_enabled=True)

# ШАГ2. Подбор параметров ПИД-регулятора.

# Чтобы не ждать каждый раз завершения первого шага, можно его закомментировать и забить результат напрямую:
w_ooc = TransferFunction([1], [1, 2, 2])
# Кому нужно будет получить числитель и знаменатель подобранной передаточной функции модели, делать это следует так:
[transfer_func_nominator, transfer_func_denominator] = w_ooc.get_coefficients()
