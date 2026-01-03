from bech32py.bech32 import encode

compressed_public_key_hash = bytes.fromhex(
    'accd0c131d9df94b40bea948b1cb9cb7dd78989d')

# Insert checksum and metadata, encode using bech32 and return a string
# See the library source code for the exact API.
# https://github.com/saving-satoshi/bech32py/blob/main/bech32py/bech32.py


def hash_to_address(hash):
    bech32_address = encode('tb', 0, compressed_public_key_hash)

    return bech32_address

# tb1q4nxscycanhu5ks9749ytrjuuklwh3xyajtmecm
