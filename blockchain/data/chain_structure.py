from blockchain.data.block import Block


class ChainStructure:
    def __init__(self):
        self.chain = []
        return

    def append_blk(self, blk: Block):
        self.chain.append(blk)
        return

    def get_last_blk(self):
        if len(self.chain) == 0:
            return None
        else:
            return self.chain[len(self.chain) - 1]
