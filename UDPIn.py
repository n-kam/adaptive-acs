import socket
import struct


class UDPIn(object):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def send(self, signal):
        self.sock.sendto(struct.pack('d', signal), (self.ip, self.port))
        return True
