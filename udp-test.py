import time

from UDPIn import UDPIn
from UDPOut import UDPOut

UDP_IP = "localhost"
UDP_PORT = 20000
UDP_IP_SEND = "localhost"
UDP_PORT_SEND = 30000
UDP_IP_SEND_SET_POINT = "localhost"
UDP_PORT_SEND_SET_POINT = 40000

# sock_rcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock_rcv.bind((UDP_IP, UDP_PORT))
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# udpIn = UDP("localhost", 30000)
# udpSp = UDP("localhost", 40000)
# udpOut = UDP("localhost", 20000)

udpInputSignal = UDPIn("localhost", 30000)
udpSetPointSignal = UDPIn("localhost", 40000)
udpOutputSignal = UDPOut("localhost", 20000)

y = udpOutputSignal.rcv()
count = 0

for setPoint in 1, 10, 5, 0, 10:
    print("setPoint: ", setPoint)
    timeStart = int(time.time())
    timeNow = timeStart
    while (timeNow - timeStart) < 5:
        count += 1
        y = udpOutputSignal.rcv()
        x = setPoint - y
        # sp = int(random.randrange(1, 10, 1))
        # print("x: ", x, "; sp: ", setPoint)
        udpInputSignal.send(x)
        udpSetPointSignal.send(setPoint)
        timeNow = int(time.time())
        # print("time: ", timeNow - timeStart )

print("count: ", count)
