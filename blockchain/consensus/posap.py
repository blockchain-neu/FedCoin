from blockchain.data.transaction import Transaction
from blockchain.network.message import *
from blockchain.consensus.consensus import Consensus
from blockchain.util.settings import *
from blockchain.util.downloader import Downloader
import copy
import hashlib
import math
import numpy as np
import random
import struct
import tensorflow as tf


# Data Layer
class PoSapBlock(Block):
    def __init__(self, blk_id: int, prev_hash: str, *args):
        super(PoSapBlock, self).__init__(blk_id, prev_hash)
        if len(args) == 6:
            (self.winner_id, self.ave_s, self.winner_s, self.difficulty, self.task_spec, self.txs) = args
            self.readonly = True
        else:
            self.winner_id = 0
            self.ave_s = [0] * K
            self.winner_s = [1] * K
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
    def __init__(self, model_urls: list, price: float, runtime: float):
        super(TaskMessage, self).__init__('task')
        self.update_kv('model_urls', model_urls)
        self.update_kv('price', price)
        self.update_kv('runtime', runtime)
        return


class ShapleyMessage(Message):
    def __init__(self, s: list):
        super(ShapleyMessage, self).__init__('shapley')
        self.update_kv('s', s)
        return


class AverageMessage(Message):
    def __init__(self, ave_s: list, winner_s: list):
        super(AverageMessage, self).__init__('average')
        self.update_kv('ave_s', ave_s)
        self.update_kv('winner_s', winner_s)
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
        t = PoSapMessageHandlingTask(self, msg, addr)
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
            price = self.msg_dict['price']
            runtime = self.msg_dict['runtime']
            model_urls = self.msg_dict['model_urls']
            i = 0
            for url in model_urls:
                d = Downloader(url, 'save_model/model_' + str(i + 1) + '.h5')
                d.start()
                d.join()
                i += 1
            weights_list = self.app.get_var('weights_list')
            self.msg_handler.lock.acquire()
            weights_list.clear()
            self.app.set_var('requester_addr', self.addr)
            self.app.set_var('price', price)
            self.msg_handler.lock.release()
            for i in range(K):
                model = tf.keras.models.load_model('save_model/model_' + str(i + 1) + '.h5')
                self.msg_handler.lock.acquire()
                weights_list.append(copy.deepcopy(model.get_weights()))
                self.msg_handler.lock.release()
                del model
                tf.keras.backend.clear_session()
            PoSap(self.msg_handler).run(runtime)
        elif self.msg_type == 'shapley':
            s_dict = self.app.get_var('s_dict')
            ave_s = self.app.get_var('ave_s')
            count = len(s_dict)
            ave_s = (ave_s * np.array([count]) + self.msg_dict['s']) / np.array([count + 1])
            self.msg_handler.lock.acquire()
            s_dict[self.addr] = self.msg_dict['s']
            self.app.set_var('ave_s', ave_s)
            self.msg_handler.lock.release()
            if count + 1 == K:
                tmp_dict = {}
                min_dist = 65535
                min_addr = ""
                for (addr, s) in s_dict:
                    tmp_dict[addr] = PoSap.calc_dist(s, ave_s)
                    if tmp_dict[addr] < min_dist:
                        min_dist = tmp_dict[addr]
                        min_addr = addr
                msg = AverageMessage(ave_s, s_dict[min_addr])
                self.network.send(msg, self.addr)
                self.printer.print('Sent a \"' + msg.dict['type'] + '\" message to ' + self.addr + ' at ' +
                                   str(self.msg_dict['timestamp']))
        elif self.msg_type == 'average':
            if self.msg_dict['winner_s'] == self.app.get_var('s'):
                self.msg_handler.lock.acquire()
                self.app.set_var('ave_s', self.msg_dict['ave_s'])
                self.msg_handler.lock.release()
                blk = PoSap.generate_blk(self.app)
                msg = BlockMessage(blk)
                self.network.send(msg, self.addr)
                self.printer.print('Sent a \"' + msg.dict['type'] + '\" message to ' + self.addr + ' at ' +
                                   str(self.msg_dict['timestamp']))
        elif self.msg_type == 'block':
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
    mnist = tf.keras.datasets.mnist

    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0
    x_train = x_train.reshape(-1, 28 * 28)
    x_test = x_test.reshape(-1, 28 * 28)

    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(512, activation='tanh', input_shape=(784,)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(256, activation='tanh'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(128, activation='tanh'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(10, activation='softmax')
    ])

    model.compile(
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        optimizer=tf.keras.optimizers.SGD(learning_rate=0.02),
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy()])

    def __init__(self, msg_handler: MessageHandler):
        super(PoSap, self).__init__()
        self.app = msg_handler.app
        self.lock = msg_handler.lock
        self.weights_list = self.app.get_var('weights_list')
        return

    def run(self, runtime: float = 600.0):
        s = [0.0] * K
        t = 0
        s_t = [0.0] * K
        start_time = time.time()
        while time.time() > start_time + runtime or not self.app.get_var('received'):
            r = [*range(K)]
            random.shuffle(r)
            weights = PoSap.aggregate(self.weights_list[r[0]])
            s_t[r[0]] = PoSap.calc_accuracy(weights)
            for i in range(1, K):
                weights = PoSap.aggregate(PoSap.aggregate(self.weights_list[r[i]]), weights, i)
                s_t[r[i]] = PoSap.calc_accuracy(weights)
                tmp = 0
                for j in range(0, i - 1):
                    tmp += s_t[r[j]]
                s_t[r[i]] = s_t[r[i]] - tmp
            s = (s * np.array([t]) + s_t) / np.array([t + 1])
            t += 1
        self.lock.acquire()
        self.app.set_var('s', s)
        self.lock.release()
        return

    @staticmethod
    def generate_blk(app) -> PoSapBlock:
        ave_s = app.get_var('ave_s')
        s = app.get_var('s')
        price = app.get_var('price')
        blk = PoSapBlock(app.get_var('size'), app.get_var('last_hash'))
        blk.winner_id = int(app.get_var('addr').split('.')[3])
        blk.ave_s = ave_s
        blk.winner_s = s
        blk.txs.append(Transaction(app.get_vars('requester_addr'), app.get_var('addr'), price * SAP_PRICE))
        return blk

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
    def calc_accuracy(weights):
        PoSap.model.set_weights(weights)
        [loss, accuracy] = PoSap.model.evaluate(PoSap.x_test, PoSap.y_test)
        return accuracy

    @staticmethod
    def calc_dist(x: list, y: list) -> float:
        ret = 0.0
        for i in range(len(x)):
            ret += pow(x[i] - y[i], 2)
        ret = math.sqrt(ret)
        return ret

    @staticmethod
    def aggregate(weights, prev_weights=None, count: int = 0):
        if prev_weights is None:
            return weights
        else:
            return (prev_weights * np.array([count]) + weights) / np.array([count + 1])
