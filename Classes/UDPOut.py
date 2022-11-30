import socket
import struct


class UDPOut(object):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __init__(self, ip, port):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))

    def rcv(self):
        byte_signal = self.sock.recvfrom(8)[0]
        return struct.unpack('d', byte_signal)[0]
