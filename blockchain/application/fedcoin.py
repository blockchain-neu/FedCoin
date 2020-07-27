from abc import *
from blockchain.data.chain_structure import ChainStructure
from blockchain.network.message import MessageHandler, JoinMessage, QuitMessage
from blockchain.network.p2p import P2P
from blockchain.util import Printer


class Application:
    def __init__(self):
        self.app_vars = {
            'size': [0],
            'last_hash': '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
            'addr': P2P.get_addr(),
            'local_blk': None,
            'whitelist': [P2P.get_addr()],
            'chain_struct': ChainStructure()
        }
        self.network = P2P()
        self.printer = Printer()
        self.msg_handler = MessageHandler(self)
        return

    @abstractmethod
    def run(self):
        pass

    def set_var(self, key: str, value):
        self.app_vars[key] = value
        return

    def get_var(self, key: str):
        return self.app_vars[key]


class FedCoin(Application):
    def __init__(self):
        super(FedCoin, self).__init__()
        return

    def run(self):
        self.network.send(JoinMessage())
        try:
            while True:
                (msg, addr) = self.network.receive()
                if addr != self.app_vars['addr']:
                    self.msg_handler.msg_handle(msg, addr)
        except KeyboardInterrupt:
            self.network.send(QuitMessage())
        return
