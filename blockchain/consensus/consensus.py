from abc import *
from blockchain.data.block import Block


class Consensus(ABC):
    def __init__(self):
        return

    @abstractmethod
    def run(self):
        pass

    @staticmethod
    def generate_blk() -> Block:
        pass

    @staticmethod
    def verify_blk(blk: Block) -> bool:
        pass
