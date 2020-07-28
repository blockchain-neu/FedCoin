from blockchain.network.message import JoinMessage, QuitMessage
from blockchain.consensus.posap import PoSapMessageHandler
from blockchain.application.application import Application


class FedCoin(Application):
    def __init__(self):
        super(FedCoin, self).__init__()
        self.msg_handler = PoSapMessageHandler(self)
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
