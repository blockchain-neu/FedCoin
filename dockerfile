From python:3.7-slim

WorkDir /var/FedCoin

Copy blockchain /var/FedCoin/blockchain/
Copy main.py /var/FedCoin/main.py

Run pip install pip -U
Run pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

Cmd ["python3", "-u", "main.py"]
