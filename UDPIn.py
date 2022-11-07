import socket
import struct


class UDPIn(object):
    def __init__(self, udp_ip, udp_port_in, udp_port_set_point):
        self.udp_ip = udp_ip
        self.udp_port_in = udp_port_in
        self.udp_port_set_point = udp_port_set_point
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_input(self, input_signal):
        self.sock.sendto(struct.pack('d', input_signal), (self.udp_ip, self.udp_port_in))
        return None

    def send_set_point(self, set_point):
        self.sock.sendto(struct.pack('d', set_point), (self.udp_ip, self.udp_port_set_point))
        return None
