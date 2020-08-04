from blockchain.application.fedcoin import *


if __name__ == '__main__':
    # FedCoin.run_fl_server()
    app = FedCoin()
    app.run_full_node()
    #
    # mnist = tf.keras.datasets.mnist
    #
    # (x_train, y_train), (x_test, y_test) = mnist.load_data()
    # x_train, x_test = x_train / 255.0, x_test / 255.0
    # x_train = x_train.reshape((60000, 28, 28, 1))
    # x_test = x_test.reshape((10000, 28, 28, 1))
    #
    # weights = None
    # for i in range(100):
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
    # weights_list = app.get_var('weights_list')
    # weights_list.clear()
    # for i in range(K):
    #     model = tf.keras.models.load_model('save_model/model_' + str(i + 1) + '.h5')
    #     weights_list.append(copy.deepcopy(model.get_weights()))
    #     del model
    #     tf.keras.backend.clear_session()
    # PoSap(app).run()

    # source, _ = tff.simulation.datasets.emnist.load_data()
    #
    #
    # def map_fn(example):
    #     return collections.OrderedDict(
    #         x=tf.reshape(example['pixels'], [-1, 784]), y=example['label'])
    #
    #
    # def client_data(n):
    #     ds = source.create_tf_dataset_for_client(source.client_ids[n])
    #     return ds.repeat(10).shuffle(500).batch(20).map(map_fn)
    #
    #
    # train_data = [client_data(n) for n in range(10)]
    # element_spec = train_data[0].element_spec
    #
    #
    # def model_fn():
    #     model = tf.keras.models.Sequential([
    #         tf.keras.layers.Input(shape=(784,)),
    #         tf.keras.layers.Dense(units=10, kernel_initializer='zeros'),
    #         tf.keras.layers.Softmax(),
    #     ])
    #     return tff.learning.from_keras_model(
    #         model,
    #         input_spec=element_spec,
    #         loss=tf.keras.losses.SparseCategoricalCrossentropy(),
    #         metrics=[tf.keras.metrics.SparseCategoricalAccuracy()])
    #
    #
    # trainer = tff.learning.build_federated_averaging_process(
    #     model_fn, client_optimizer_fn=lambda: tf.keras.optimizers.SGD(0.02))
    #
    #
    # def evaluate(num_rounds=10):
    #     state = trainer.initialize()
    #     for _ in range(num_rounds):
    #         t1 = time.time()
    #         state, metrics = trainer.next(state, train_data)
    #         t2 = time.time()
    #         print('metrics {m}, round time {t:.2f} seconds'.format(
    #             m=metrics, t=t2 - t1))
    #
    # evaluate()
