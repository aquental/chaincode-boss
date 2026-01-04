# The Bitcoin API

To answer these questions, you'll need to interact with a bitcoin full node, via its JSON-RPC API. We've imported a library for you called `bitcoin_rpc` which handles the secure HTTP connection from your script to the full node, executes your commands, and returns the responses. Your full node is "pruning" so it only has access to the last 300 blocks, but that should be enough to include the entire timespan of Vanderpoole's recent muckery.

Let's start by getting familiar with the [API](https://github.com/saving-satoshi/bitcoin_rpcpy/blob/main/bitcoin_rpcpy/bitcoin_rpc.py). The library has one function that accepts one required argument, `method` (a string) and one optional argument, `params` (either a string or a number):

```
Bitcoin.rpc(method, params)
```

The API also has a convenient "help" method! Ask it for help to learn more about the available commands, then pass the challenge by printing the current network difficulty.

# Block Data

Each bitcoin full node has a database. That's where blocks are stored and indexed by their hash. The full node keeps track of which blocks are candidates at each height in the chain with a second index that maps height -> [block hashes].

The JSON-RPC API returns block data as JSON objects that include a property `txs` which is an array of transaction objects.

Retrieve all the block candidates at height 6929996 and print the hash of the block with the fewest transactions in it.

# Transaction Data

The transaction objects confirmed in a block are JSON objects that include arrays of "inputs" and "outputs". Both of these arrays are lists of UTXOs, also known as "coins". Coin objects have a "value" property represented in satoshis.

The "inputs" array is the coins spent (destroyed) by the transaction and the "outputs" array is the coins created by the transaction. You may recall from Chapter 6 that transactions always pay a fee to incentivize miners to include them in a block. That fee is exactly the difference in value between the total input and total output values of a transaction.

In other words, the miner gets to keep whatever bitcoin that was sent in to the transaction but not sent back out to the transaction recipients.

There is a transaction with the txid:

```
7bd09aa3b4795be2839d9159edff0811d6d4ec5a64abd81c0da1e73ab00bf520
```

in a block with the hash:

```
dab5708b1b3db05407e35b2004156d74f7bb5bed7f677743945cac1465b5838f
```

Print that transaction's fee in satoshis.

# The Coinbase Transaction

The first transaction in every block is called the coinbase. It may also be referred to as the "0th" transaction (referring to txs[0]) and it has a few very special properties. First of all, it has no inputs! This is because it does not spend any existing coins. Second, its output value is strictly defined by the protocol (despite what Vanderpoole might say!). This is the mechanism by which miners both collect fees from transactions, and generate new coins.

```
BLOCK_SUBSIDY + TOTAL_TRANSACTION_FEES_IN_BLOCK = COINBASE_OUTPUT_VALUE
```

It's fairly easy to understand how total transaction fees in a block are summed up, but where does that block subsidy value come from? How does every participant in the bitcoin network determine exactly how much new bitcoin miners are allowed to generate at any given time?

This is the algorithm written by Satoshi Nakamoto that has remained an immutable core property of the bitcoin system since the beginning:

- Starting with the block #1 mined in 2009, the block subsidy is 50 BTC (or 5,000,000,000 satoshis)
- Every 210,000 blocks that value is cut in half.

At block height 209,999 the subsidy was 50 BTC. In the very next block at height 210,000 the subsidy was 25 BTC, and so on. After 63 "halvings" the subsidy will be one single satoshi. The last halving will drop the subsidy to zero.

AND THAT LAST HALVING WAS YESTERDAY!

Finish the implementation of the following function that accepts a block height as an argument and returns the value of the subsidy in satoshis.
