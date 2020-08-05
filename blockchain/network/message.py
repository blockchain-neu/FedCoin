from blockchain.data.block import Block
import base64
import json
import threading
import time


class Message:
    def __init__(self, msg_type: str = 'null'):
        self.dict = {
            'type': msg_type,
            'timestamp': time.time()
        }
        return

    def update_kv(self, key: str, value):
        self.dict.update({key: value})
        return

    def serialize(self) -> bytes:
        return json.dumps(self.dict).encode()

    @staticmethod
    def deserialize(data: bytes):
        obj = json.loads(data.decode())
        msg = Message()
        for (key, value) in obj.items():
            msg.update_kv(key, value)
        return msg


class JoinMessage(Message):
    def __init__(self):
        super(JoinMessage, self).__init__('join')
        return


class ReJoinMessage(Message):
    def __init__(self, size: int, last_hash: str):
        super(ReJoinMessage, self).__init__('re_join')
        self.update_kv('size', size)
        self.update_kv('last_hash', last_hash)
        return


class SyncMessage(Message):
    def __init__(self, blk_id: int):
        super(SyncMessage, self).__init__('sync')
        self.update_kv('blk_id', blk_id)
        return


class ReSyncMessage(Message):
    def __init__(self, blk: Block):
        super(ReSyncMessage, self).__init__('re_sync')
        self.update_kv('blk', base64.b64encode(blk.serialize()).decode())
        return


class QuitMessage(Message):
    def __init__(self):
        super(QuitMessage, self).__init__('quit')
        return


class MessageHandler:
    def __init__(self, app):
        self.network = app.network
        self.printer = app.printer
        self.app = app
        self.lock = threading.Lock()
        self.tasks = []
        return

    def __del__(self):
        for task in self.tasks:
            if task.is_alive():
                task.join()
        return

    def msg_handle(self, msg: Message, addr: str):
        t = MessageHandlingTask(self, msg, addr)
        t.start()
        self.tasks.append(t)
        return


class MessageHandlingTask(threading.Thread):
    def __init__(self, msg_handler: MessageHandler, msg: Message, addr: str):
        super(MessageHandlingTask, self).__init__()
        self.network = msg_handler.network
        self.printer = msg_handler.printer
        self.app = msg_handler.app
        self.msg_handler = msg_handler
        self.msg_type = msg.dict['type']
        self.msg_dict = msg.dict
        self.addr = addr
        return

    def base_handle(self):
        self.printer.print('Received a \"' + self.msg_type + '\" message from ' + self.addr + ' at ' +
                           str(self.msg_dict['timestamp']))
        if self.msg_type == 'join':
            if self.addr not in self.app.get_var('whitelist'):
                self.msg_handler.lock.acquire()
                self.app.get_var('whitelist').append(self.addr)
                self.msg_handler.lock.release()
                msg = ReJoinMessage(self.app.get_var('size'), self.app.get_var('last_hash'))
                self.network.send(msg, self.addr)
                self.printer.print('Sent a \"' + msg.dict['type'] + '\" message to ' + self.addr + ' at ' +
                                   str(self.msg_dict['timestamp']))
        elif self.msg_type == 're_join':
            if self.addr not in self.app.get_var('whitelist'):
                self.msg_handler.lock.acquire()
                self.app.get_var('whitelist').append(self.addr)
                if self.app.get_var('size') < self.msg_dict['size']:
                    self.app.set_var('size', self.msg_dict['size'])
                    self.app.set_var('last_hash', self.msg_dict['last_hash'])
                    msg = SyncMessage(len(self.app.get_var('chain_struct').chain))
                    self.network.send(msg, self.addr)
                    self.printer.print('Sent a \"' + msg.dict['type'] + '\" message to ' + self.addr + ' at ' +
                                       str(self.msg_dict['timestamp']))
                self.msg_handler.lock.release()
        elif self.msg_type == 'sync':
            if len(self.app.get_var('chain_struct').chain) > self.msg_dict['blk_id']:
                msg = ReSyncMessage(self.app.get_var('chain_struct').chain[self.msg_dict['blk_id']])
                self.network.send(msg, self.addr)
                self.printer.print('Sent a \"' + msg.dict['type'] + '\" message to ' + self.addr + ' at ' +
                                   str(self.msg_dict['timestamp']))
        elif self.msg_type == 'quit':
            if self.addr in self.app.get_var('whitelist'):
                self.msg_handler.lock.acquire()
                self.app.get_var('whitelist').remove(self.addr)
                self.msg_handler.lock.release()
        return

    def run(self):
        self.base_handle()
        return
