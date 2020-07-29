from abc import *
from blockchain.data.block import Block


class Consensus(ABC):
    def __init__(self):
        return

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def generate_blk(self) -> Block:
        pass

    @abstractmethod
    def verify_blk(self, blk: Block) -> bool:
        pass
