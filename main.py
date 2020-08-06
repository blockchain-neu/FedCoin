from blockchain.application.fedcoin import *
import gc


if __name__ == '__main__':
    gc.enable()
    app = FedCoin()
    # run a full node
    app.run_full_node()
    # run a lightweight node
    # app.run_lightweight_node()
