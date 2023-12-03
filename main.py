import os.path

import ooc_identify
import helpers
import optimization
from model import TransferFunction

#
# НАСТРОЙКА ПАРАМЕТРОВ
#

# Дефолтные значения
kp = 0.0
ki = 0.0
kd = 0.0
set_point = 0.0
MODEL_IP_OUT = "0.0.0.0"
MODEL_PORT_OUT = 20000
MODEL_IP_IN = "192.168.122.200"
MODEL_PORT_IN = 30000
MODEL_PORT_SET_POINT = 40000
MODEL_RUN_TIME = 9.9
MODEL_DATA_FILENAME = "resources/h_model.txt"

# Опциональный конфиг
if os.environ.get('AACS_MODEL_IP_OUT') is not None:
    MODEL_IP_OUT = os.environ.get('AACS_MODEL_IP_OUT')
if os.environ.get('AACS_MODEL_PORT_OUT') is not None:
    MODEL_PORT_OUT = os.environ.get('AACS_MODEL_PORT_OUT')
if os.environ.get('AACS_MODEL_IP_IN') is not None:
    MODEL_IP_IN = os.environ.get('AACS_MODEL_IP_IN')
if os.environ.get('AACS_MODEL_PORT_IN') is not None:
    MODEL_PORT_IN = os.environ.get('AACS_MODEL_PORT_IN')
if os.environ.get('AACS_MODEL_PORT_SET_POINT') is not None:
    MODEL_PORT_SET_POINT = os.environ.get('AACS_MODEL_PORT_SET_POINT')
if os.environ.get('AACS_RUN_TIME') is not None:
    MODEL_RUN_TIME = os.environ.get('AACS_RUN_TIME')
if os.environ.get('AACS_MODEL_DATA_FILENAME') is not None:
    MODEL_DATA_FILENAME = os.environ.get('AACS_MODEL_DATA_FILENAME')

#
# ШАГ 1. Идентификация объекта управления (определение его передаточной функции W(p))
#

# Если файл существует, считываем данные из него. Если нет, то считываем из модели и сохраняем в него.
if os.path.exists(MODEL_DATA_FILENAME):
    model_transient_response = helpers.read_tr_from_file(MODEL_DATA_FILENAME)
else:
    model_transient_response = helpers.read_tr_from_model(ip_in=MODEL_IP_IN,
                                                          ip_out=MODEL_IP_OUT,
                                                          port_in=MODEL_PORT_IN,
                                                          port_out=MODEL_PORT_OUT,
                                                          port_set_point=MODEL_PORT_SET_POINT,
                                                          run_time_sec=MODEL_RUN_TIME,
                                                          output_file_name=MODEL_DATA_FILENAME)

# Идентификация ОУ
w_ooc = ooc_identify.identify(model_transient_response,
                              algorithm=optimization.Algorythm.classic,
                              transfer_func_nominator_max_order=1,
                              transfer_func_denominator_max_order=3,
                              results_plotting_enabled=True)

#
# ШАГ2. Подбор параметров ПИД-регулятора.
#

# Чтобы не ждать каждый раз завершения первого шага, можно его закомментировать и забить результат напрямую:
w_ooc = TransferFunction([1], [1, 2, 2])
# Кому нужно будет получить числитель и знаменатель подобранной передаточной функции модели, делать это следует так:
[transfer_func_nominator, transfer_func_denominator] = w_ooc.get_coefficients()
