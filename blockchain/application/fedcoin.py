from blockchain.network.message import JoinMessage, QuitMessage
from blockchain.consensus.posap import PoSapBlock, PoSapMessageHandler, TaskMessage
from blockchain.application.application import Application
from blockchain.util.settings import *
from blockchain.util.printer import Printer
import base64
import math
import tensorflow as tf


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
        self.app_vars['r_list'] = []
        self.app_vars['requester_addr'] = None
        self.app_vars['price'] = 0.0
        return

    def run_full_node(self):
        msg = JoinMessage()
        self.network.send(msg)
        self.printer.print('Sent a \"' + msg.dict['type'] + '\" message at ' + str(msg.dict['timestamp']))
        try:
            while True:
                (msg, addr) = self.network.receive()
                if addr != self.app_vars['addr'] or msg.dict['type'] == 'shapley':
                    self.msg_handler.msg_handle(msg, addr)
        except KeyboardInterrupt:
            msg = QuitMessage()
            self.network.send(msg)
            self.printer.print('Sent a \"' + msg.dict['type'] + '\" message at ' + str(msg.dict['timestamp']))
        return

    def run_lightweight_node(self):
        msg = TaskMessage([], PRICE, RUNTIME)
        try:
            self.network.send(msg)
            while True:
                (recv_msg, addr) = self.network.receive()
                if addr != self.app_vars['addr']:
                    if recv_msg.dict['type'] == 'block':
                        self.get_var('s_dict').clear()
                        blk = PoSapBlock.deserialize(base64.b64decode(recv_msg.dict['blk'].encode()))
                        self.printer.print(str(blk.winner_s))
                        msg = TaskMessage([], PRICE, RUNTIME)
                        self.network.send(msg)
        except KeyboardInterrupt:
            pass
        return

    @staticmethod
    def run_fl_server():
        (train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.mnist.load_data()

        # Normalize pixel values to be between 0 and 1
        train_images, test_images = train_images / 255.0, test_images / 255.0

        model = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(10)
        ])

        # model.summary()

        model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=0.1),
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=['accuracy'])

        init_weight = model.get_weights()
        client_size = math.floor(len(train_images) / K)

        for i in range(K):
            model.fit(train_images[i * client_size:(i + 1) * client_size],
                      train_labels[i * client_size:(i + 1) * client_size], epochs=10)

            model.save('save_model/model_' + str(i + 1) + '.h5')

            model.set_weights(init_weight)

            # test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=2)

            # print('\nTest accuracy:', test_acc)

        del init_weight
        tf.keras.backend.clear_session()
        return
