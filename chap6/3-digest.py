from struct import pack
import hashlib


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
