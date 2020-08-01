From python:3.7-slim

WorkDir /var/FedCoin
Copy blockchain /var/FedCoin/blockchain/
Copy save_model /var/FedCoin/save_model/
Copy main.py /var/FedCoin/main.py
Copy requirements.txt /var/FedCoin/requirements.txt

Run pip install pip -U
Run pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
Run pip install -r requirements.txt

Cmd ["python3", "-u", "main.py"]
