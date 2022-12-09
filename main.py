from Classes.IdentifyOOC import IdentifyOOC

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
UDP_PORT_IN = 30000  # input signal port
UDP_PORT_SET_POINT = 40000  # set point signal port
UDP_PORT_OUT = 20000  # output signal port
RUN_TIME = 10  # for how long to interact with model in sec

# ШАГ 1. Идентификация объекта управления (его W(p))

ooc_id = IdentifyOOC(UDP_IP_IN, UDP_IP_OUT, UDP_PORT_IN, UDP_PORT_SET_POINT, UDP_PORT_OUT,
                     # source_file="Assets/h_teor.txt",
                     source_file="Assets/h_model_1669583451.0397856.txt",
                     algorithm=IdentifyOOC.classic,
                     transfer_func_nominator_max_order=0,
                     transfer_func_denominator_max_order=2,
                     results_plotting_enabled=True)
w_ooc = ooc_id.identify()

# STEP 2. SET UP PID-CONTROLLER
# todo

# Кому нужно будет получить числитель и знаменатель подобранной передаточной функции модели, делать это следует так:
[transfer_func_nominator, transfer_func_denominator] = w_ooc.get_coefficients()
