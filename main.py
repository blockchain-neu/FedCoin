from blockchain.util.settings import *
import docker


if __name__ == '__main__':
    client = docker.from_env()
    client.images.build(path='.', dockerfile='nodes/full/dockerfile', tag='fedcoin')
    client.images.build(path='.', dockerfile='nodes/lightweight/dockerfile', tag='fedcoin_lw')
    containers = []
    for i in range(R):
        container = client.containers.run('fedcoin', detach=True)  # , mem_limit='1536m')
        containers.append(container)
