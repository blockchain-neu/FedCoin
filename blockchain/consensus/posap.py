from blockchain.data.transaction import Transaction
from blockchain.network.message import *
from blockchain.consensus.consensus import Consensus
import hashlib
import struct


D = 0.5  # Difficulty


# Data Layer
class PoSapBlock(Block):
    def __init__(self, blk_id: int, prev_hash: str, *args):
        super(PoSapBlock, self).__init__(blk_id, prev_hash)
        if len(args) == 6:
            (self.winner_id, self.ave_s, self.winner_s, self.difficulty, self.task_spec, self.txs) = args
            self.readonly = True
        else:
            self.winner_id = 0
            self.ave_s = []
            self.winner_s = []
            self.difficulty = D
            self.task_spec = []
            self.txs = []
            self.readonly = False
        return

    def serialize(self) -> bytes:
        ret = struct.pack('!III', self.blk_id, self.winner_id, len(self.ave_s))
        for val in self.ave_s:
            ret += struct.pack('!I', val)
        ret += self.prev_hash
        ret += struct.pack('!I', len(self.winner_s))
        for val in self.winner_s:
            ret += struct.pack('!I', val)
        ret += struct.pack('!dI', self.difficulty, len(self.txs))
        for tx in self.txs:
            ret += tx.serialize()
        return ret

    @staticmethod
    def deserialize(data: bytes):
        (blk_id, winner_id, len_ave_s) = struct.unpack('!III', data[0:12])
        pointer = 12
        ave_s = []
        for i in range(len_ave_s):
            (val) = struct.unpack('!I', data[pointer:pointer+4])
            pointer += 4
            ave_s.append(val)
        (prev_hash) = struct.unpack('!s', data[pointer:pointer + 32])
        pointer += 32
        (len_winner_s) = struct.unpack('!I', data[pointer:pointer+4])
        pointer += 4
        winner_s = []
        for i in range(len_winner_s):
            (val) = struct.unpack('!I', data[pointer:pointer+4])
            pointer += 4
            winner_s.append(val)
        (difficulty, len_txs) = struct.unpack('!dI', data[pointer:pointer+12])
        pointer += 12
        txs = []
        for i in range(len_txs):
            txs.append(Transaction.deserialize(data[pointer:pointer+16]))
            pointer += 16
        return Block(blk_id, prev_hash, winner_id, ave_s, winner_s, difficulty, '', txs)

    def hash(self) -> str:
        return hashlib.sha256(self.serialize()).hexdigest()


# Network Layer
class TaskMessage(Message):
    def __init__(self, model_url: str, price: float):
        super(TaskMessage, self).__init__('task')
        self.update_kv('model_url', model_url)
        self.update_kv('price', price)
        return


class BlockMessage(Message):
    def __init__(self, blk: Block):
        super(BlockMessage, self).__init__('block')
        self.update_kv('blk', blk)
        return


class PoSapMessageHandler(MessageHandler):
    def __init__(self, app):
        super(PoSapMessageHandler, self).__init__(app)
        return

    def msg_handle(self, msg: Message, addr: str):
        t = MessageHandlingTask(self, msg, addr)
        t.start()
        self.tasks.append(t)
        return


class PoSapMessageHandlingTask(MessageHandlingTask):
    def __init__(self, msg_handler: MessageHandler, msg: Message, addr: str):
        super(PoSapMessageHandlingTask, self).__init__(msg_handler, msg, addr)
        return

    def run(self):
        self.base_handle()
        if self.msg_type == 're_sync':
            blk = PoSapBlock.deserialize(bytes(self.msg_dict['blk']))
            if len(self.app.get_var('chain_struct').chain) == blk.blk_id and PoSap.verify_blk(blk):
                self.msg_handler.lock.acquire()
                self.app.app_vars['chain_struct'].append(blk)
                self.msg_handler.lock.release()
                if self.app.get_var('size') > blk.blk_id + 1:
                    msg = SyncMessage(blk.blk_id + 1)
                    self.network.send(msg, self.addr)
                    self.printer.print('Sent a \"' + self.msg_type + '\" message to ' + self.addr + ' at ' +
                                       str(self.msg_dict['timestamp']))
        elif self.msg_type == 'task':
            pass
        elif self.msg_type == 'blk':
            pass
        return


# Consensus Layer
class PoSap(Consensus):
    def __init__(self):
        super(PoSap, self).__init__()
        return

    def run(self):

        return

    @staticmethod
    def generate_blk() -> Block:

        pass

    @staticmethod
    def verify_blk(blk: Block) -> bool:

        return False
