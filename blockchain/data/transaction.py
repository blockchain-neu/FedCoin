import socket
import struct


class Transaction:
    def __init__(self, out_addr: str, in_addr: str, amount: float):
        self.out_addr = socket.inet_aton(out_addr)
        self.in_addr = socket.inet_aton(in_addr)
        self.amount = amount

    def serialize(self) -> bytes:
        return self.out_addr + self.in_addr + struct.pack('!d', self.amount)

    @staticmethod
    def deserialize(data: bytes):
        (amount, ) = struct.unpack('!d', data[8:])
        return Transaction(socket.inet_ntoa(data[0:4]), socket.inet_ntoa(data[4:8]), amount)
