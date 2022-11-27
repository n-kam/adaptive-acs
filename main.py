from IdentifyOOC import IdentifyOOC

# CONFIGURATION

kp = 0.0
ki = 0.0
kd = 0.0
set_point = 0.0
UDP_IP_OUT = "0.0.0.0"
UDP_IP_SEND = "192.168.122.200"
UDP_IP_SEND_SET_POINT = UDP_IP_SEND
UDP_PORT_IN = 30000  # input signal port
UDP_PORT_SET_POINT = 40000  # set point signal port
UDP_PORT_OUT = 20000  # output signal port
RUN_TIME = 10  # for how long to interact with model in sec

# ШАГ 1. Идентификация объекта управления (его W(p))

ooc_id = IdentifyOOC(UDP_IP_SEND, UDP_IP_OUT, UDP_PORT_IN, UDP_PORT_SET_POINT, UDP_PORT_OUT,
                     source_file="h_model_1669571378.7674701.txt")
w_ooc = ooc_id.identify()

# STEP 2. SET UP PID-CONTROLLER
# todo
