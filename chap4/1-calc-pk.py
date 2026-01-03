import secp256k1py.secp256k1 as SECP256K1
# Multiply the private key by the ECDSA generator point G to
# produce a new curve point which is the public key.
# Return that curve point (also known as a group element)
# which will be an instance of secp256k1.GE
# See the library source code for the exact definition
# https://github.com/saving-satoshi/secp256k1py/blob/main/secp256k1py/secp256k1.py
G = SECP256K1.FAST_G

def privatekey_to_publickey(private_key):
    # Convert the hex string private key to an integer
    priv_key_int = int(private_key, 16)

    # Multiply the generator point G by the private key scalar
    public_key_point = G.mul(priv_key_int)

    return public_key_point
