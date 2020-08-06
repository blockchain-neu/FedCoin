from blockchain.network.message import Message
import socket


class P2P:
    def __init__(self, port=2333):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(("", port))
        self.port = port
        return

    def __del__(self):
        self.sock.close()
        return

    def send(self, msg: Message, addr='<broadcast>'):
        self.sock.sendto(msg.serialize(), (addr, self.port))

    def receive(self) -> (Message, str):
        (data, addr) = self.sock.recvfrom(65535)
        return Message.deserialize(data), addr[0]

    @staticmethod
    def get_addr():
        return socket.gethostbyname(socket.getfqdn(socket.gethostname()))
