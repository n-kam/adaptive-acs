import numpy
from control import matlab
from matplotlib import pyplot

from Classes.IdentifyOOC import IdentifyOOC

UDP_IP_OUT = "127.0.0.1"
UDP_IP_IN = "127.0.0.1"
UDP_IP_SEND_SET_POINT = UDP_IP_IN
UDP_PORT_IN = 30000  # input signal port
UDP_PORT_SET_POINT = 40000  # set point signal port
UDP_PORT_OUT = 20000  # output signal port
RUN_TIME = 10  # for how long to interact with model in sec

source_file = "Assets/h_teor.txt"

ooc_id = IdentifyOOC(UDP_IP_IN, UDP_IP_OUT, UDP_PORT_IN, UDP_PORT_SET_POINT, UDP_PORT_OUT,
                     algorithm=IdentifyOOC.gauss_seidel,
                     transfer_func_nominator_max_order=0,
                     transfer_func_denominator_max_order=2)

values_list = ooc_id.read_transient_response(source_file)

time_values = list()
signal_values = list()
for line in values_list:
    time_values.append(line[0])
    signal_values.append(line[2])

for xval in time_values:
    print(xval)

pyplot.grid(True)
pyplot.xticks(numpy.arange(0, 11, 1))
pyplot.yticks(numpy.arange(0, 1.1, 0.1))
# pyplot.legend()

pyplot.plot(time_values, signal_values, 'red')

unit1 = matlab.tf([0.9], [0.9, 1.8, 1.6])
[unit1_values, x1] = matlab.step(unit1, time_values)
pyplot.plot(time_values, unit1_values, 'green')
pyplot.show()
