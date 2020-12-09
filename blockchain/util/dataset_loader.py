import numpy as np


class DatasetLoader:
    @staticmethod
    def load_mnist(path='saves/dataset/mnist.npz'):
        data = np.load(path)
        return (data['x_train'], data['y_train']), (data['x_test'], data['y_test'])
