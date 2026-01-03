import hashlib

compressed_public_key = '03e8e24c60463d469a056be712bd838f8e2bf47771a2ee62ea244069e4e637b317'

# Get the sha256 digest of the compressed public key.
# Then get the ripemd160 digest of that sha256 hash
# Return 20-byte array


def hash_compressed(compressed_public_key):
    # Convert hex string to bytes
    pubkey_bytes = bytes.fromhex(compressed_public_key)
    # First: SHA-256
    sha256_hash = hashlib.sha256(pubkey_bytes).digest()
    # Then: RIPEMD-160
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    # Convert the 20-byte result to a hexadecimal string
    return ripemd160_hash.hex()

#  accd0c131d9df94b40bea948b1cb9cb7dd78989d
