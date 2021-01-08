import random
from fhipe import ipe, tife


def test_ipe():
    """
    Runs a test on IPE for toy parameters.
    """

    n = 10
    M = 20
    x = [random.randint(0, M) for i in range(n)]
    y = [random.randint(0, M) for i in range(n)]

    checkprod = sum(map(lambda i: x[i] * y[i], range(n)))

    (pp, sk) = ipe.setup(n)
    skx = ipe.keygen(sk, x)
    cty = ipe.encrypt(sk, y)
    prod = ipe.decrypt(pp, skx, cty, M * M * n)
    assert prod == checkprod, "Failed test_ipe"


def test_tife():
    """
    Runs a test on two-input functional encryption for the comparison function on
    toy parameters.
    """

    N = 30
    f = lambda x, y: 1 if x < y else 0

    x = random.randint(0, N - 1)
    y = random.randint(0, N - 1)

    (pp, sk) = tife.setup(N, f)
    ctx = tife.encryptL(sk, x)
    cty = tife.encryptR(sk, y)
    result = tife.decrypt(pp, ctx, cty)
    assert result == f(x, y), "Failed test_tife"


test_ipe()
test_tife()
