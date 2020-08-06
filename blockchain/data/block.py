from abc import *
from blockchain.data.transaction import Transaction


class Block(ABC):
    def __init__(self, blk_id: int, prev_hash: str, *args):
        self.blk_id = blk_id
        self.prev_hash = prev_hash
        self.txs = []
        self.readonly = False
        return

    @abstractmethod
    def serialize(self) -> bytes:
        pass

    @staticmethod
    def deserialize(data: bytes):
        pass

    @abstractmethod
    def hash(self) -> str:
        pass

    def append_tx(self, tx: Transaction):
        if not self.readonly:
            self.txs.append(tx)
        return
