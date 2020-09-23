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

### Set parameters

Parameters are defined in `blockchain/util/settings.py`, which are showed as follows:

|Parameter|Description|Type|Range|Default|
|:-------:|:----------|:--:|:---:|:-----:|
|K|Number of FL clients|int|[2, inf]|20|
|R|Number of replicas (miners)|int|[2, inf]|2|
|D|Difficulty in mining|float|[0.0, inf]|1.5|
|PRICE|Amount of FedCoins as rewards|float|[0.0, inf]|1000.0|
|RUNTIME|Time to mine in a round|float|[0.0, inf]|15.0|
|TRAIN_PRICE|Payments to the FL clients|float|[0.0, 1.0]|0.7|
|COM_PRICE|Payments to the FL server for processing the model aggregation|float|[0.0, 1.0]|0.1|
|SAP_PRICE|Payments yo the blockchain network miners for calculating SV|float|[0.0, 1.0]|0.2|

Note: The condition "TRAIN_PRICE + COM_PRICE + SAP_PRICE = 1" should be satisfied.

## Build and run

The shell code `python main.py` will build `fedcoin` and `fedcoin_lw` images, and run several `fedcoin` containers that matches the number of replicas defined in settings.

The batch file `clean.sh` will stop and delete containers, as well as delete images that are untagged.

## References

* Yuan Liu, Shuai Sun, Zhengpeng Ai, Shuangfeng Zhang, Zelei Liu, Han Yu. FedCoin: A Peer-to-Peer Payment System for Federated Learning ([arXiv:2002.11711](https://arxiv.org/abs/2002.11711))
