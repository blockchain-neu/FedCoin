"""
Copyright (c) 2016, Kevin Lewi
 
Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
"""

"""
Implementation of two-input functional encryption.

The setup algorithm takes the description of the function f.
"""

from fhipe import ipe

def setup(n, f, group_name = 'MNT159', simulated = False):
  """
  Performs the two-input functional encryption setup algorithm, where n is the 
  plaintext space size, f is a function which takes two inputs, and group_name 
  is the name of the pairing group to use.
  """

  (pp_ipe, sk_ipe) = ipe.setup(n, group_name, simulated)
  pp = pp_ipe
  sk = (n, f, sk_ipe)
  return (pp, sk)

def encryptL(sk, x):
  """
  Performs the left-encrypt algorithm, where sk is the secret key and x is an 
  integer in the range [0,n-1].
  """

  (n, _, sk_ipe) = sk
  assert x in range(n), "Input is outside of range"
  u = [0] * n
  u[x] = 1
  skx = ipe.keygen(sk_ipe, u)
  return skx

def encryptR(sk, y):
  """
  Performs the right-encrypt algorithm, where sk is the secret key and y is an 
  integer in the range [0,n-1].
  """

  (n, f, sk_ipe) = sk
  assert y in range(n), "Input is outside of range"
  v = [f(i,y) for i in range(n)]
  cty = ipe.encrypt(sk_ipe, v)
  return cty

def decrypt(pp, ctx, cty):
  """
  Decrypts the two ciphertexts, which is equivalent to evaluating f(x,y), for 
  two ciphertexts ctx and cty.
  """
  
  pp_ipe = pp
  return ipe.decrypt(pp_ipe, ctx, cty)

