import base64
import hashlib
import secp256k1py.secp256k1 as SECP256K1
# View the library source code
# https://github.com/saving-satoshi/secp256k1py/blob/main/secp256k1py/secp256k1.py

GE = SECP256K1.GE
G = SECP256K1.G

public_key_x = 0x11db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5c
public_key_y = 0xb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3

# Defined by Bitcoin message signing protocol
prefix = "Bitcoin Signed Message:\n"

# Provided by Vanderpoole
text =  "I am Vanderpoole and I have control of the private key Satoshi\n"
text += "used to sign the first-ever Bitcoin transaction confirmed in block #170.\n"
text += "This message is signed with the same private key."

# Encoded Signature
vp_sig = "H4vQbVD0pLK7pkzPto8BHourzsBrHMB3Qf5oYVmr741pPwdU2m6FaZZmxh4ScHxFoDelFC9qG0PnAUl5qMFth8k="

def encode_message(text):
    # Given an ascii-encoded text message, serialize a byte array
    # with the Bitcoin protocol prefix string followed by the text
    # and both components preceded by a length byte.
    # Returns a 32-byte hex value.
    prefix = "Bitcoin Signed Message:\n"
    vector = bytes([len(prefix)]) + bytes(prefix, 'ascii') + bytes([len(text)]) + bytes(text, 'ascii')
    single_hash = hashlib.new('sha256', vector).digest()
    double_hash = hashlib.new('sha256', single_hash).digest()
    return int.from_bytes(double_hash, "big")

def decode_sig(base64_sig):
    # Decode a base64-encoded signature string into its ECDSA
    # signature elements r and s, returned as a tuple of integers.
    # Remember to throw away the first byte of metadata from the signature string!
    vp_sig_bytes = base64.b64decode(base64_sig)
    vp_sig_r = int.from_bytes(vp_sig_bytes[1:33])
    vp_sig_s = int.from_bytes(vp_sig_bytes[33:])
    return (vp_sig_r, vp_sig_s)

def verify(sig_r, sig_s, key, msg):
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
  u2 = (sig_r * sig_s_inverted) % GE.ORDER

  # Calculate R = u1 * G + u2 * public key
  # We need to use the appropriate methods for point multiplication and addition
  R1 = GE.mul((u1, G))
  R2 = GE.mul((u2, key))
  R = R1 + R2

  # Verify if the x-coordinate of R modulo ORDER is equal to sig_r
  return sig_r == int(R.x) % GE.ORDER

# Define the necessary params for the verify() function
r, s = decode_sig(vp_sig)
msg = encode_message(text)
key_ge = GE(public_key_x, public_key_y)
