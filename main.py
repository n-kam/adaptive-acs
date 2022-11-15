import time

from UDPIn import UDPIn
from UDPOut import UDPOut
from OOCId import OOCId

# CONFIGURATION

kp = 0.0
ki = 0.0
kd = 0.0
set_point = 0.0
UDP_IP = "127.0.0.1"
UDP_PORT_IN = 30000  # input signal port
UDP_PORT_SET_POINT = 40000  # set point signal port
UDP_PORT_OUT = 20000  # output signal port
RUN_TIME = 10  # for how long to interact with model in sec

# STEP 1. IDENTIFY OBJECT OF CONTROL W(p)

udp_input_socket = UDPIn(UDP_IP, UDP_PORT_IN)
udp_set_point_socket = UDPIn(UDP_IP, UDP_PORT_SET_POINT)
udp_output_socket = UDPOut(UDP_IP, UDP_PORT_OUT)

# 1.1. Send 1(t) to model and get h(t)

time_start = int(time.time())
time_now = time_start
set_point_signal_array = [0, 1]  # 1(t)
output_signal_array = []
i = 0

while (time_now - time_start) < RUN_TIME:

    # iterate through array of set_point signal, but don't exceed its size
    set_point = set_point_signal_array[i]
    if i + 2 <= len(set_point_signal_array):
        i += 1

    udp_set_point_socket.send(set_point)

    output_signal = udp_output_socket.rcv()
    output_signal_array.append(output_signal)
    input_signal = set_point - output_signal  # Negative feedback
    udp_input_socket.send(input_signal)

    print(time_now - time_start, ": set_point=", set_point, ", input_signal=", input_signal, ", output_signal=",
          output_signal)

    time_now = int(time.time())

print("output_signal_array size:", len(output_signal_array))

# 1.2. Get object of control W(p)
ooc_id = OOCId()
w_ooc = ooc_id.id(output_signal_array)

# STEP 2. SET UP PID-CONTROLLER
# todo
