from blockchain.application.fedcoin import *
from blockchain.consensus.posap import *
import copy
import tensorflow as tf

if __name__ == '__main__':
    FedCoin.run_fl_server()
    app = FedCoin()
    #
    # mnist = tf.keras.datasets.mnist
    #
    # (x_train, y_train), (x_test, y_test) = mnist.load_data()
    # x_train, x_test = x_train / 255.0, x_test / 255.0
    # # x_train = x_train.reshape((60000, 28, 28, 1))
    # # x_test = x_test.reshape((10000, 28, 28, 1))
    #
    # weights = None
    # for i in range(K):
    #     model = tf.keras.models.load_model('save_model/model_' + str(i + 1) + '.h5')
    #
    #     if weights is None:
    #         weights = copy.deepcopy(model.get_weights())
    #     else:
    #         weights = (weights * np.array([i]) + model.get_weights()) / np.array([i + 1])
    #
    #     del model
    #     tf.keras.backend.clear_session()
    #
    # model = tf.keras.models.load_model('save_model/model_1.h5')
    # model.set_weights(weights)
    #
    # [_, accuracy] = model.evaluate(x_test, y_test, verbose=2)
    # print(accuracy)
    #
    # del model
    # tf.keras.backend.clear_session()
    weights_list = app.get_var('weights_list')
    weights_list.clear()
    for i in range(K):
        model = tf.keras.models.load_model('save_model/model_' + str(i + 1) + '.h5')
        weights_list.append(copy.deepcopy(model.get_weights()))
        del model
        tf.keras.backend.clear_session()
    PoSap(app).run()
