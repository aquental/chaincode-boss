import secp256k1py.secp256k1 as SECP256K1

GE = SECP256K1.GE
G = SECP256K1.G

# Message digest from step 9:
msg = 0x73a16290e005b119b9ce0ceea52949f0bd4f925e808b5a54c631702d3fea1242

# Signature values from step 10:
sig_r = 0x8bd06d50f4a4b2bba64ccfb68f011e8babcec06b1cc07741fe686159abef8d69
sig_s = 0x3f0754da6e85699666c61e12707c45a037a5142f6a1b43e7014979a8c16d87c9

# Public key values (uncompressed hex strings)
keys = [
    "04bbb554daf8811b95c8af5272fa8b4e2d6335bf19fff24d3187b8781497299aa4d27c900c367e4e506d671a4ea3aa50843f182a090d701f3bc8e6578d2455d81e",
    "04cc679cd88b28444049aa9db8f88864ace38f79ba6310d0d3f027c9462a9f420befaaf888ce372cbf6f0ece99e5ada86436c960c1c0840a588ea7dbd78187445d",
    "049d57ded01d3a7652a957cf86fd4c3d2a76e76e83d3c965e1dca45f1ee06630636b8bcbc3df3fbc9669efa2ccd5d7fa5a89fe1c0045684189f01ea915b8a746a6",
    "0461bfb73040740c12f57146b3a7f2ccfd75b6cd2a0d5df7a789cfaeb77bda4dcd222df570946cb6de62d6b1a939f55da85859f575e84ba86c67c4aa97d85ba516",
    "042a87d97397b2c43dff63670e38e78db159daa0e1070ec42181d0ed44a7d1aa508d42bd9759659c4a3194dea56da71325fb25acda6ee931cd8b93172b5d0f3c8f",
    "04d1cdabaea3be5d8161b93b7e20b0375cefee0a36259d654185555deff881406a421384e927328e2dcb5ed87103365ef3007bd31e12591e5d1c56c83516db26ec"
]


def verify(r, s, key, msg):
    if r == 0 or r >= GE.ORDER:
        print("FALSE - invalid r value")
        return False

    if s == 0 or s >= GE.ORDER:
        print("FALSE - invalid s value")
        return False

    # Calculate the inverse of sig_s modulo ORDER
    sig_s_inverted = pow(sig_s, -1, GE.ORDER)

    # Calculate u1 and u2
    u1 = (msg * sig_s_inverted) % GE.ORDER
    # Note: use r, not sig_r (but same value)
    u2 = (r * sig_s_inverted) % GE.ORDER

    # Point multiplication: G * u1 + key * u2
    R1 = G.mul(u1)
    R2 = key.mul(u2)
    R = R1.add(R2)

    # Check if R.x % ORDER == r
    return (int(R.x) % GE.ORDER) == r


def verify_keys(keys):
    for key_hex in keys:
        # Extract x and y coordinates from uncompressed public key (starts with 04)
        x_hex = key_hex[2:66]   # bytes 1-32 (after 04 prefix)
        y_hex = key_hex[66:]    # bytes 33-64

        # Convert hex strings to integers
        x_int = int(x_hex, 16)
        y_int = int(y_hex, 16)

        # Create GE point: key_ge = GE(x_int, y_int)
        key_ge = GE(x_int, y_int)

        # Verify this key against the signature and message
        if verify(sig_r, sig_s, key_ge, msg):
            return key_hex  # Return the matching key (as hex string)

    # If no key matches
    return None


if __name__ == "__main__":
    matching_key = verify_keys(keys)
    if matching_key:
        print("Matching public key found:")
        print(matching_key)
    else:
        print("No matching public key found.")
