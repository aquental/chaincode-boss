# Looking at the Input class implementation

Here we have code for two classes: an Input class and an Outpoint (not "output"!) class.

Inputs come from unspent transaction outputs. If you provide the description of an output to the from_output() method, it will create an instance of the Input class:

```python
from_output(txid: str, vout: int, value: int, scriptcode: bytes)
```

The first two arguments are:

1. txid: the ID of the transaction that created the output, and

2. vout: the index of the output in the transaction's entire list of outputs

Together, these two pieces of information make up an Outpoint. Eventually we will pass in the txid and vout values that came from executing the listunspent command in the previous exercise.

The second two arguments are the value of the output we want to spend (in satoshis) and something called a scriptcode. That data is not needed until later so let's temporarily use an empty byte array.

---

Hashes in bitcoin are reversed
Why do we reverse hashes in bitcoin?

Avatar
, but only when presented to or entered by a user. When a hash is provided in hexadecimal format, the byte order must be reversed before storing or transmitting the data as raw bytes.

You can see an example of this in the `from_output()` method where it handles the txid argument.

---

We also need a `serialize()` method that returns a byte array according to the specification. This is how the transaction is actually sent between nodes on the network, and how it is expressed in a block:

# Outpoint

| Description                                                      | Name  | Type  | Size |
| ---------------------------------------------------------------- | ----- | ----- | ---- |
| Hash of transaction being spent from                             | txid  | bytes | 32   |
| Position of output being spent in the transaction's output array | index | int   | 4    |

# Input

| Description                                                        | Name     | Type  | Size |
| ------------------------------------------------------------------ | -------- | ----- | ---- |
| txid and output index being spent from                             | outpoint | bytes | 36   |
| ScriptSig length (always 0 for Segregated Witness)                 | length   | int   | 1    |
| Always empty for Segregated Witness                                | script   | bytes | 0    |
| Default value is 0xffffffff but can be used for relative timelocks | sequence | int   | 4    |

Remember: integers in bitcoin are serialized [little-endian](https://chat.bitcoinsearch.xyz/?author=holocat&question=What%2520is%2520endianness%253F)

# Output

| Description                                                              | Name    | Type  | Size |
| ------------------------------------------------------------------------ | ------- | ----- | ---- |
| Number of satoshis being sent                                            | value   | bytes | 8    |
| Total length of the following script (the "witness program")             | length  | int   | 1    |
| The segregated witness version. Derived from the bech32 address          | version | int   | 1    |
| Length of the following witness program data                             | length  | int   | 1    |
| The data component derived from the bech32 address (20 bytes for P2WPKH) | data    | bytes | 20   |

# Transaction digest

In chapter 5 we learned that to sign a transaction we first need to rearrange and hash its data into a message, which becomes one of the raw inputs to our signing algorithm. Since we are using segregated witness now, we also need to implement the updated transaction digest algorithm which is specified in [BIP 143](https://github.com/bitcoin/bips/blob/master/bip-0143.mediawiki).

Remember each transaction input needs its own signature, and so some components of the digest algorithm can be cached and reused but others will be different depending on which input is being signed! Finish the transaction method `digest(input_index)` that computes the 32-byte message for signing an input.

Some notes:

- "Double SHA-256" or dSHA256 = sha256(sha256(data))
- value is the amount of the satoshis in the output being spent from. We added it to our Input class back in step 2, and just saved it there inside the class until now.
- scriptcode is the raw bitcoin script being evaluated. We also added this to our Input class back in step 2.
- all integers are encoded as little-endian!

We'll dive in to this more in the next section, but to spend from your pay-to-witness-public-key-hash (P2WPKH) address, your scriptcode would be:

```
0x1976a914{20-byte-pubkey-hash}88ac
```

...which decodes to the following bitcoin script.

```
OP_PUSHBYTES_25
OP_DUP
OP_HASH160
OP_PUSHBYTES_20
<20-byte-public-key-hash>
OP_EQUALVERIFY
OP_CHECKSIG
```

For more information about scriptcode see [BIP 143](https://github.com/bitcoin/bips/blob/master/bip-0143.mediawiki).

The raw transaction has a preimage that is the serialization of:

| Description                                                        | Name       | Type  | Size |
| ------------------------------------------------------------------ | ---------- | ----- | ---- |
| Transaction version, default 2                                     | version    | int   | 4    |
| The dSHA256 of all outpoints from all inputs, serialized           | (hash)     | bytes | 32   |
| The dSHA256 of all sequence values from all inputs, serialized     | sequences  | bytes | 32   |
| The serialized outpoint of the single input being signed           | outpoint   | bytes | 36   |
| The output script being spent from                                 | scriptcode | bytes | var  |
| The value in satoshis being spent by the single input being signed | value      | int   | 8    |
| The sequence value of the single input being signed                | sequence   | int   | 4    |
| The dSHA256 of all outputs, serialized                             | outputs    | bytes | 32   |
| Transaction locktime, default 0                                    | locktime   | int   | 4    |
| Signature hash type, we will use 1 to indicate "ALL"               | sighash    | int   | 4    |

Finally, the message we sign is the double SHA-256 of all this serialized data.

# Sign and Populate the Witness!

In the last chapter, we wrote some important ECDSA signature verification code. Now, in order to create a valid signature, we are going to take that code and rearrange it a bit.

In this exercise we'll be implementing some of the math behind the ECDSA signing algorithm. For more information on how that works, check out these resources:

• The Wikipedia page for [Elliptic Curve Digital Signature Algorithm](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)

• [Standards for Efficient Cryptography 1 (SEC 1)](https://www.secg.org/sec1-v2.pdf#subsubsection.4.1.3): Page 44, Section 4.1.3

---

Step 1

In the Transaction class, there is a method, `compute_input_signature(index, key)` that accepts the index number of an input and a private key (a 32-byte integer, or BigInt in JavaScript). Finish this method so it computes the message digest for the chosen input. Use the `digest()` method from our last step, then return an ECDSA signature in the form of two 32-byte integers: r and s.

---

Step 2

For the signing algorithm, the bitcoin protocol requires one more thing. The s value needs to be "low", meaning less than the order of the curve divided by 2. Add this check to `compute_input_signature()`.

See [BIP 146](https://github.com/bitcoin/bips/blob/master/bip-0146.mediawiki#low_s) to learn more.

---

Step 3

Complete the method `sign_input(index, priv, pub, sighash)` so that it calls `compute_input_signature(index, key)`. When handling the return value, r and s need to be encoded with an algorithm called DER which we have implemented for you.

---

Step 4

Bitcoin requires an extra byte appended to the end of the DER-signature. This byte represents the "sighash type". For now we'll always use the byte `0x01` for this, indicating "SIGHASH ALL".

---

Step 5

The last step is to create a Witness object with two stack items: the DER encoded signature blob we just made, and your compressed public key. Push the signature first, followed by the public key.

Append the witness stack object to the transaction object's array of witnesses.

# Finish the implementation of Class Transaction

To complete our transaction we will need a `serialize()` method that outputs the entire transaction as bytes formatted for broadcast on the bitcoin p2p network.

Our script should create and sign a Transaction object. It will have one input (the UTXO we identified in The input class) and two outputs:

- Mika 3000 gets 100,000,000 satoshis to `bc1qgghq08syehkym52ueu9nl5x8gth23vr8hurv9dyfcmhaqk4lrlgs28epwj`
- You get 61,000,000 back to your address bc1qm2dr49zrgf9wc74h5c58wlm3xrnujfuf5g80hs

We know our input, we know our output. Are we ready to build and sign a transaction? Not quite. We have a 1.61 BTC input and a 1 BTC output... what happens to the other 0.61 BTC? Most of that will be "change" and we need to send it back to our own address!

| Description                                   | Name      | Type        | Size |
| --------------------------------------------- | --------- | ----------- | ---- |
| Currently 2                                   | version   | int         | 4    |
| Must be exactly 0x0001 for segregated witness | flags     | bytes       | 2    |
| The number of inputs                          | in count  | int         | 1    |
| All transaction inputs, serialized            | inputs    | Inputs[]    | var  |
| The number of outputs                         | out count | int         | 1    |
| All transaction outputs, serialized           | outputs   | Outputs[]   | var  |
| All witness stacks, serialized                | witness   | Witnesses[] | var  |
| Setting to 0 indicates finality               | locktime  | int         | 4    |

Notice that there is no "count" value for witnesses. That is because the number of witness stacks must always be exactly equal to the number of inputs.

But wait! We need to include a "fee". We'll shave off a tiny piece of our change output for the mining pools to incentivize them to include our transaction in a block. Let's reduce our change from 61,000,000 to 60,999,000 satoshis.

Finally our work is done. Your script should end by returning the result of the transaction serialize() method. This is a valid signed bitcoin transaction and we can broadcast it to the network to send Mika 3000 the money she needs!
