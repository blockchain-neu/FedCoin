from blockchain.data.transaction import Transaction
from blockchain.network.message import *
from blockchain.consensus.consensus import Consensus
from blockchain.util.settings import *
import hashlib
import math
import random
import struct


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
        return PoSapBlock(blk_id, prev_hash, winner_id, ave_s, winner_s, difficulty, '', txs)

    def hash(self) -> str:
        return hashlib.sha256(self.serialize()).hexdigest()


# Network Layer
class TaskMessage(Message):
    def __init__(self, model_url: str, price: float, runtime: float):
        super(TaskMessage, self).__init__('task')
        self.update_kv('model_url', model_url)
        self.update_kv('price', price)
        self.update_kv('runtime', runtime)
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
            if len(self.app.get_var('chain_struct').chain) == blk.blk_id and \
                    PoSap.verify_blk(blk, self.msg_handler.app):
                self.msg_handler.lock.acquire()
                self.app.get_var('chain_struct').append(blk)
                self.msg_handler.lock.release()
                if self.app.get_var('size') > blk.blk_id + 1:
                    msg = SyncMessage(blk.blk_id + 1)
                    self.network.send(msg, self.addr)
                    self.printer.print('Sent a \"' + msg.dict['type'] + '\" message to ' + self.addr + ' at ' +
                                       str(self.msg_dict['timestamp']))
        elif self.msg_type == 'task':
            model_url = self.msg_dict['model_url']
            price = self.msg_dict['price']
            timeout = self.msg_dict['timeout']
            # todo
        elif self.msg_type == 'blk':
            blk = PoSapBlock.deserialize(bytes(self.msg_dict['blk']))
            size = len(self.app.get_var('size'))
            if PoSap.verify_blk(blk, self.msg_handler.app):
                if size == blk.blk_id:
                    self.msg_handler.lock.acquire()
                    self.app.get_var('chain_struct').append(blk)
                    self.app.set_var('size', size + 1)
                    self.msg_handler.lock.release()
                elif size == blk.blk_id + 1:
                    old_blk = self.app.get_var('chain_struct')[blk.blk_id]
                    if PoSap.calc_dist(blk.ave_s, blk.winner_s) < PoSap.calc_dist(old_blk.ave_s, old_blk.winner_s):
                        self.msg_handler.lock.acquire()
                        chain_struct = self.app.get_var('chain_struct')
                        chain_struct.pop()
                        chain_struct.append(blk)
                        self.msg_handler.lock.release()
        return


# Consensus Layer
class PoSap(Consensus):
    def __init__(self, app):
        super(PoSap, self).__init__()
        self.app = app
        return

    def run(self):  # todo
        s = [0.0] * K
        t = 0
        s_t = [0.0] * K
        while PoSap.verify_blk(self.app.get_var('local_blk'), self.app):
            r = random.shuffle(range(K))
            s_t[r[0]] = PoSap.calc_loss(r[0])
            for i in range(1, K):
                s_t[r[i]] = PoSap.calc_loss(r[i])
                tmp = 0
                for j in range(0, i - 1):
                    tmp += s_t[r[j]]
                s_t[r[i]] = s_t[r[i]] - tmp
            s = (s * t + s_t) / (t + 1)
            t += 1
        return

    @staticmethod
    def generate_blk() -> PoSapBlock:

        pass

    @staticmethod
    def verify_blk(blk: PoSapBlock, app) -> bool:
        ave_s = app.get_var('ave_s')
        s_t = blk.winner_s
        ave_s_t = blk.ave_s
        if PoSap.calc_dist(s_t, ave_s_t) <= D:
            if PoSap.calc_dist(ave_s, ave_s_t) <= D:
                if blk.blk_id >= app.get_var('size'):
                    return True
        return False

    @staticmethod
    def calc_loss(client_id: int):

        return 0.0

    @staticmethod
    def calc_dist(x: list, y: list) -> float:
        ret = 0.0
        for i in range(len(x)):
            ret += pow(x[i] - y[i], 2)
        ret = math.sqrt(ret)
        return ret
