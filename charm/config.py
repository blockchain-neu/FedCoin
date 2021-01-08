from charm.toolbox.enum import Enum

libs = Enum('openssl', 'gmp', 'pbc', 'miracl', 'relic')

pairing_lib=libs.pbc
ec_lib=libs.openssl
int_lib=libs.gmp
