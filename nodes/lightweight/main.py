from blockchain.application.fedcoin import FedCoin
import gc

if __name__ == '__main__':
    gc.enable()
    app = FedCoin()
    app.run_lightweight_node()
