from random import randrange
from secp256k1py import secp256k1
from struct import pack
import hashlib


class Witness:
    def __init__(self):
        self.items = []

    def push_item(self, data):
        self.items.append(data)

    def serialize(self):
        r = b""
        r += pack("<B", len(self.items))
        for item in self.items:
            r += pack("<B", len(item))
            r += item
        return r


class Transaction:
    def __init__(self):
        self.version = 2
        self.flags = bytes.fromhex("0001")
        self.inputs = []
        self.outputs = []
        self.witnesses = []
        self.locktime = 0

    def digest(self, input_index):
        def dsha256(data):
            return hashlib.new('sha256', hashlib.new('sha256', data).digest()).digest()

        # Start with an empty bytes object
        s = b""
        # Append the transaction version in little endian
        s += pack("<I", self.version)

        # Create a temporary bytes object and write the serialized outpoints of every input
        outpoints = b""
        for inp in self.inputs:
            outpoints += inp.outpoint.serialize()
        # double-SHA256 the serialized outpoints and append that to the main buffer
        s += dsha256(outpoints)

        # Create a temporary bytes object and write the sequences of every input in little endian
        sequences = b""
        for inp in self.inputs:
            sequences += pack("<I", inp.sequence)
        # double-SHA256 the serialized sequences and append that to the main buffer
        s += dsha256(sequences)

        # Serialize the outpoint of the one input we are going to sign and add it to the main buffer
        s += self.inputs[input_index].outpoint.serialize()
        # Serialize the scriptcode of the one input we are going to sign and add it to the main buffer
        s += self.inputs[input_index].scriptcode

        # Append the value of the input we are going to spend in little endian to the main buffer
        s += pack("<q", self.inputs[input_index].value)
        # Append the sequence of the input we are going to spend in little endian to the main buffer
        s += pack("<I", self.inputs[input_index].sequence)

        # Create a temporary bytes object and write all the serialized outputs of this transaction
        outputs = b""
        for out in self.outputs:
            outputs += out.serialize()
        # double-SHA256 the serialized outputs and append that to the main buffer
        s += dsha256(outputs)

        # Append the transaction locktime in little endian to the main buffer
        s += pack("<I", self.locktime)
        # Append the sighash flags in little endian to the main buffer
        s += pack("<I", 1)

        # Finally, return the double-SHA256 of the entire main buffer
        return dsha256(s)

    def compute_input_signature(self, index, key):
        # The math:
        #   k = random integer in [1, n-1]
        #   R = G * k
        #   r = x(R) mod n
        #   s = (r * a + m) / k mod n
        #   Extra Bitcoin rule from BIP 146:
        #     if s > n / 2 then s = n - s mod n
        # return (r, s)
        # Hints:
        #   n = the order of the curve secp256k1.GE.ORDER
        #   a = the private key
        #   m = the message value returned by digest()
        #   x(R) = the x-coordinate of the point R
        #   Use the built-in pow() function to turn division into multiplication!

        assert isinstance(key, int)

        msg = self.digest(index)
        k = randrange(1, secp256k1.GE.ORDER)
        k_inverted = pow(k, -1, secp256k1.GE.ORDER)
        R = k * secp256k1.G
        r = int(R.x) % secp256k1.GE.ORDER
        s = ((r * key) + int.from_bytes(msg)) * k_inverted % secp256k1.GE.ORDER
        if s > secp256k1.GE.ORDER // 2:
            s = secp256k1.GE.ORDER - s

        return (r, s)

    def sign_input(self, index, priv, pub, sighash=1):
        def encode_der(r, s):
            # Represent in DER format. The byte representations of r and s have
            # length rounded up (255 bits becomes 32 bytes and 256 bits becomes 33 bytes).
            # See BIP 66
            # https://github.com/bitcoin/bips/blob/master/bip-0066.mediawiki
            rb = r.to_bytes((r.bit_length() + 8) // 8, 'big')
            sb = s.to_bytes((s.bit_length() + 8) // 8, 'big')
            return b'0' + bytes([4 + len(rb) + len(sb), 2, len(rb)]) + rb + bytes([2, len(sb)]) + sb
        (r, s) = self.compute_input_signature(index, priv)
        der_sig = encode_der(r, s)
        wit = Witness()
        wit.push_item(der_sig + bytes([sighash]))
        wit.push_item(pub)
        self.witnesses.append(wit)
