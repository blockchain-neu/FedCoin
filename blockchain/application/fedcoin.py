from blockchain.network.message import JoinMessage, QuitMessage
from blockchain.consensus.posap import PoSapBlock, PoSapMessageHandler, TaskMessage, BlockMessage
from blockchain.application.application import Application
from blockchain.util.settings import *
import math
import tensorflow as tf
import time


class FedCoin(Application):
    def __init__(self):
        super(FedCoin, self).__init__()
        self.msg_handler = PoSapMessageHandler(self)
        self.app_vars['ave_s'] = [0] * K
        self.app_vars['local_blk'] = PoSapBlock(0, '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                                                   '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self.app_vars['weights_list'] = []
        return

    def run(self):
        msg = JoinMessage()
        self.network.send(msg)
        self.printer.print('Sent a \"' + msg.dict['type'] + '\" message at ' + str(msg.dict['timestamp']))
        try:
            while True:
                (msg, addr) = self.network.receive()
                if addr != self.app_vars['addr']:
                    self.msg_handler.msg_handle(msg, addr)
        except KeyboardInterrupt:
            msg = QuitMessage()
            self.network.send(msg)
            self.printer.print('Sent a \"' + msg.dict['type'] + '\" message at ' + str(msg.dict['timestamp']))
        return

    def run_server(self):
        msg = TaskMessage('model.h5', PRICE, RUNTIME)
        try:
            while True:
                self.network.send(msg)
                self.printer.print('Sent a \"' + msg.dict['type'] + '\" message at ' + str(msg.dict['timestamp']))
                while time.time() < msg.dict['timestamp'] + RUNTIME:
                    (msg, addr) = self.network.receive()
                    if addr != self.app_vars['addr']:
                        self.msg_handler.msg_handle(msg, addr)
        except KeyboardInterrupt:
            pass
        return

    @staticmethod
    def run_fl_server():
        mnist = tf.keras.datasets.mnist

        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        x_train, x_test = x_train / 255.0, x_test / 255.0
        # x_train = x_train.reshape((60000, 28, 28, 1))
        # x_test = x_test.reshape((10000, 28, 28, 1))

        local_size = math.floor(len(x_train) / K)

        for i in range(K):
            model = tf.keras.models.Sequential([
                tf.keras.layers.Flatten(input_shape=(28, 28)),
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(10, activation='softmax')
                # tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
                # tf.keras.layers.MaxPooling2D((2, 2)),
                # tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                # tf.keras.layers.MaxPooling2D((2, 2)),
                # tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                # tf.keras.layers.Flatten(),
                # tf.keras.layers.Dense(64, activation='relu'),
                # tf.keras.layers.Dense(10, activation='softmax')
            ])

            model.compile(optimizer='adam',
                          loss='sparse_categorical_crossentropy',
                          metrics=['accuracy'])

            model.fit(x_train[i * local_size:(i + 1) * local_size],
                      y_train[i * local_size:(i + 1) * local_size],
                      epochs=5)

            model.evaluate(x_test, y_test, verbose=2)

            model.save('save_model/model_' + str(i + 1) + '.h5')

            del model
            tf.keras.backend.clear_session()
        return
