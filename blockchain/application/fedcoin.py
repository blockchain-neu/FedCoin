from blockchain.network.message import JoinMessage, QuitMessage
from blockchain.consensus.posap import PoSapMessageHandler, TaskMessage
from blockchain.application.application import Application
from blockchain.util.settings import *
import numpy as np
import random
import tensorflow as tf
import time


class FedCoin(Application):
    def __init__(self):
        super(FedCoin, self).__init__()
        self.msg_handler = PoSapMessageHandler(self)
        self.app_vars['t'] = 0
        self.app_vars['s'] = None
        self.app_vars['ave_s'] = [0.0] * K
        self.app_vars['s_dict'] = {}
        self.app_vars['received'] = False
        self.app_vars['weights_list'] = []
        self.app_vars['requester_addr'] = None
        self.app_vars['price'] = 0.0
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
        msg = TaskMessage([], PRICE, RUNTIME)
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
        x_train = x_train.reshape(-1, 28 * 28)
        x_test = x_test.reshape(-1, 28 * 28)

        a = [[], [], [], [], [], [], [], [], [], []]
        b = [[], [], [], [], [], [], [], [], [], []]

        for i in range(len(y_train)):
            a[y_train[i]].append(x_train[i])
            b[y_train[i]].append(y_train[i])

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

        init_weights = model.get_weights()

        for i in range(100):
            current_dataset_x = a[i // 10:]
            current_dataset_y = b[i // 10:]

            current_dataset_xx = []
            current_dataset_yy = []

            for item in current_dataset_x:
                for _ in item:
                    current_dataset_xx.append(_)

            for item in current_dataset_y:
                for _ in item:
                    current_dataset_yy.append(_)

            xxyy = list(zip(current_dataset_xx, current_dataset_yy))
            random.shuffle(xxyy)

            xxyy = random.sample(xxyy, 600)
            current_dataset_xx, current_dataset_yy = zip(*xxyy)

            model.fit(np.asarray(current_dataset_xx), np.asarray(current_dataset_yy), epochs=50,
                      validation_data=(x_test, y_test))
            model.save('save_model/' + str(i + 1) + '.h5')
            model.set_weights(init_weights)
        return
