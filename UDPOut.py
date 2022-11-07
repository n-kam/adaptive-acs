import socket
import struct


class UDPOut(object):
    def __init__(self, udp_ip, udp_port_out):
        self.sock_rcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_rcv.bind((udp_ip, udp_port_out))

    def rcv(self):
        y_byte, addr = self.sock_rcv.recvfrom(8)
        return struct.unpack('d', y_byte)[0]
