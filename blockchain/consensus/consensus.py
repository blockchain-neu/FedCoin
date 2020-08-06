from abc import *
from blockchain.data.block import Block


class Consensus(ABC):
    def __init__(self):
        return

    @abstractmethod
    def run(self, *args):
        pass

    @staticmethod
    def generate_blk(app) -> Block:
        pass

    @staticmethod
    def verify_blk(blk: Block, app) -> bool:
        pass
