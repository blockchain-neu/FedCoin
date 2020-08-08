# FedCoin

A Peer-to-Peer Payment System for Federated Learning

## Layered Architecture

* Data (Transaction, Block, ChainStructure, etc.)
* Network (Message, P2P, etc.)
* Consensus (Consensus, PoSap, etc.)
* Incentive
* Contract
* Application (Application, FedCoin, etc.)

## Usage

### Prepare

To build and run FedCoin, you must ensure the following software or package(s) are installed in your experimental computer(s):

* [Docker](https://docs.docker.com/engine/install/) (Mirror: [TUNA](https://mirrors.tuna.tsinghua.edu.cn/help/docker-ce/))
* [Python 3.7](https://www.python.org/downloads/)
* [TensorFlow 2.3.0](https://www.tensorflow.org/install) (Mirror: [Google China](https://tensorflow.google.cn/install))

Moreover, Linux distribution like [Ubuntu](https://ubuntu.com/download) and [Kubuntu](https://kubuntu.org/getkubuntu/) are recommended.

### Generate weights

Firstly, you should create a directory named `save_model`, then run the following codes in the Python environment to generate weights:
```python
from blockchain.application.fedcoin import FedCoin
FedCoin.run_fl_server()
```

### Build

To build the container of miners, just run:
```shell script
docker build -t fedcoin .
```

If your computer is in the user mode, you may escalate the privilege using the following command with the `sudo` prefix:
```shell script
sudo docker build -t fedcoin .
```

To build the container of the FL server, you should modify `main.py` by commenting `app.run_full_node()` and uncommenting `app.run_lightweight_node()`, then run:
```shell script
docker build -t fedcoin_lw .
```

And similarly, if your computer is in the user mode, you may escalate the privilege using the following command with the `sudo` prefix:
```shell script
sudo docker build -t fedcoin_lw .
```

### Run

To run a miner or FL server, just using `docker run fedcoin` or `docker run fedcoin_lw`, and the `sudo` prefix may be needed according to the circumstance.

## References

* Yuan Liu, Shuai Sun, Zhengpeng Ai, Shuangfeng Zhang, Zelei Liu, Han Yu. FedCoin: A Peer-to-Peer Payment System for Federated Learning ([arXiv:2002.11711](https://arxiv.org/abs/2002.11711))
