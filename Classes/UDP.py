import socket
import struct


class UDPIn(object):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    def send(self, signal):
        self.sock.sendto(struct.pack('d', signal), (self.ip, self.port))
        return True


class UDPOut(object):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __init__(self, ip: str, port: int):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))

    def rcv(self):
        byte_signal = self.sock.recvfrom(8)[0]
        return struct.unpack('d', byte_signal)[0]
