from blockchain.network.message import JoinMessage, QuitMessage
from blockchain.consensus.posap import PoSapBlock, PoSapMessageHandler, TaskMessage, BlockMessage
from blockchain.application.application import Application
from blockchain.util.settings import *
import time


class FedCoin(Application):
    def __init__(self):
        super(FedCoin, self).__init__()
        self.msg_handler = PoSapMessageHandler(self)
        self.app_vars['avg_s'] = [0] * K
        self.app_vars['local_blk'] = PoSapBlock(0, '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                                                   '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        return

    def run(self):
        msg = JoinMessage()
        self.network.send(msg)
        self.printer.print('Sent a \"' + msg.dict['type'] + '\" message at ' + str(msg.dict['timestamp']))
        try:
            while True:
                (msg, addr) = self.network.receive()
                if addr != self.app_vars['addr']:
                    self.msg_handler.msg_handle(msg, addr)
        except KeyboardInterrupt:
            msg = QuitMessage()
            self.network.send(msg)
            self.printer.print('Sent a \"' + msg.dict['type'] + '\" message at ' + str(msg.dict['timestamp']))
        return

    def run_server(self):
        msg = TaskMessage('model.h5', PRICE, RUNTIME)
        try:
            while True:
                self.network.send(msg)
                self.printer.print('Sent a \"' + msg.dict['type'] + '\" message at ' + str(msg.dict['timestamp']))
                while time.time() < msg.dict['timestamp'] + RUNTIME:
                    (msg, addr) = self.network.receive()
                    if addr != self.app_vars['addr']:
                        self.msg_handler.msg_handle(msg, addr)
        except KeyboardInterrupt:
            pass
        return
