from struct import pack
from struct import pack
from bech32py import bech32
from random import randrange
from secp256k1py import secp256k1
import hashlib
# UTXO from chapter 6 step 1 (mining pool payout)
txid = "8a081631c920636ed71f9de5ca24cb9da316c2653f4dc87c9a1616451c53748e"
vout = 1
value = 161000000

# From chapter 4 (we will reuse address for change)
priv = 0x93485bbe0f0b2810937fc90e8145b2352b233fbd3dd7167525401dd30738503e
compressed_pub = bytes.fromhex(
    "038cd0455a2719bf72dc1414ef8f1675cd09dfd24442cb32ae6e8c8bbf18aaf5af")
pubkey_hash = "b234aee5ee74d7615c075b4fe81fd8ace54137f2"
addr = "bc1qkg62ae0wwntkzhq8td87s87c4nj5zdlj2ga8j7"

# Explained in step 6
scriptcode = "1976a914" + pubkey_hash + "88ac"


class Outpoint:
    def __init__(self, txid: bytes, index: int):
        assert isinstance(txid, bytes)
        assert len(txid) == 32
        assert isinstance(index, int)
        self.txid = txid
        self.index = index

    def serialize(self):
        r = b""
        r += self.txid
        r += pack("<I", self.index)
        return r


class Input:
    def __init__(self):
        self.outpoint = None
        self.script = b""
        self.sequence = 0xffffffff
        self.value = 0
        self.scriptcode = b""

    @classmethod
    def from_output(cls, txid: str, vout: int, value: int, scriptcode: bytes):
        self = cls()
        self.outpoint = Outpoint(bytes.fromhex(txid)[::-1], vout)
        self.value = value
        self.scriptcode = bytes.fromhex(scriptcode)
        return self

    def serialize(self):
        r = b""
        r += self.outpoint.serialize()
        r += pack("<B", len(self.script))
        r += pack("<I", self.sequence)
        return r
# Use the bech32 library to find the version and data components from the address
# See the library source code for the exact definition
# https://github.com/saving-satoshi/bech32py/blob/main/bech32py/bech32.py

# Use the bech32 library to find the version and data components from the address
# See the library source code for the exact definition
# https://github.com/saving-satoshi/bech32py/blob/main/bech32py/bech32.py


class Output:
    def __init__(self):
        self.value = 0
        self.witness_version = 0
        self.witness_data = b""

    @classmethod
    def from_options(cls, addr, value):
        assert isinstance(value, int)
        self = cls()
        (ver, data) = bech32.decode("bc", addr)
        self.witness_version = ver
        self.witness_data = bytes(data)
        self.value = value
        return self

    def serialize(self):
        r = b""
        r += pack("<q", self.value)
        r += pack("<B", len(self.witness_data) + 2)
        r += pack("<B", self.witness_version)
        r += pack("<B", len(self.witness_data))
        r += self.witness_data
        return r


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

        def serialize(self):
            r = b""
            r += pack("<I", self.version)
            r += self.flags
            r += pack("<B", len(self.inputs))
            for inp in self.inputs:
                r += inp.serialize()
            r += pack("<B", len(self.outputs))
            for out in self.outputs:
                r += out.serialize()
            for wit in self.witnesses:
                r += wit.serialize()
            r += pack("<I", self.locktime)
            return r


tx = Transaction()
in0 = Input.from_output(txid, vout, value, scriptcode)
out0 = Output.from_options(
    "bc1qgghq08syehkym52ueu9nl5x8gth23vr8hurv9dyfcmhaqk4lrlgs28epwj", 100000000)
# The output below is all the remaining change from this transaction, are you sure you want to send yourself all the change?
# out1 = Output.from_options(addr, 61000000)
out1 = Output.from_options(addr, 60999000)
tx.inputs.append(in0)
tx.outputs.append(out0)
tx.outputs.append(out1)
tx.sign_input(0, priv, compressed_pub)

print(tx.serialize().hex())

# 020000000001018e74531c4516169a7cc84d3f65c216a39dcb24cae59d1fd76e6320c93116088a0100000000ffffffff0200e1f50500000000220020422e079e04cdec4dd15ccf0b3fd0c742eea8b067bf06c2b489c6efd05abf1fd158c5a20300000000160014b234aee5ee74d7615c075b4fe81fd8ace54137f202473044022031c7bf725914e0eceee9de2acfee60e636583fb147ea18d12772af4493a78d94022054581602b1d64032920bdccecd0848cb55c62ca6f453f01ec35e4a50c26292540121038cd0455a2719bf72dc1414ef8f1675cd09dfd24442cb32ae6e8c8bbf18aaf5af00000000
