from abc import *
from blockchain.data.chain_structure import ChainStructure
from blockchain.network.message import MessageHandler
from blockchain.network.p2p import P2P
from blockchain.util import Printer


class Application:
    def __init__(self, msg_handler: MessageHandler):
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
        self.msg_handler = msg_handler
        return

    @abstractmethod
    def run(self):
        pass

    def set_var(self, key: str, value):
        self.app_vars[key] = value
        return

    def get_var(self, key: str):
        return self.app_vars[key]