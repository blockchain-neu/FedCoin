from abc import *
from blockchain.data.chain_structure import ChainStructure
from blockchain.network.message import MessageHandler
from blockchain.network.p2p import P2P
from blockchain.util import Printer


class Application:
    def __init__(self):
        self.app_vars = {
            'size': 0,
            'last_hash': '0000000000000000000000000000000000000000000000000000000000000000',
            'addr': P2P.get_addr(),
            'whitelist': [P2P.get_addr()],
            'chain_struct': ChainStructure()
        }
        self.network = P2P()
        self.printer = Printer()
        self.msg_handler = MessageHandler(self)
        return

    @abstractmethod
    def run_full_node(self):
        pass

    @abstractmethod
    def run_lightweight_node(self):
        pass

    def set_var(self, key: str, value):
        self.app_vars[key] = value
        return

    def get_var(self, key: str):
        return self.app_vars[key]
