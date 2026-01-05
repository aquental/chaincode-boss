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

## Block subsidy

The block subsidy is the amount of bitcoin released into circulation from the coinbase of each new block. As there are only ~21 million total bitcoins able to be created there must be some diminishing euqation to allow for a coinbase subisdy that reaches the 21 million amount. The equation below visualizes what exists in bitcoin.

What does this equation do? Well we know that the coinbase reward of the genesis block was 50 bitcoin and this is indicated with the numerator of the fraction on the right side of the equation. The denominator is the part of our equation that indicates by how much the reward will be decreased each halving, in this case 2, or by half. We also know that bitcoin is only aware of individual blocks as a chronological system so we make each halving 210,000 blocks long. Lastly we want to make each halving double each time so we want to double the amount the subsidy is halved by each halving so we raise 2 to the power of the current halving 'i' to the final halving epoch 32 iterations in the future.

# The Coinbase Transaction

There are four block candidates at height 6929851. Only one of them is a valid block, the other three were mined by Vanderpoole's cartel in reckless attempts to inflate the bitcoin money supply.

Using the block subsidy function you wrote in the previous challenge and the JSON-RPC API, write a function to check the validity of a block candidate. Do this by checking if the coinbase output is correct. Your function should return true if the block is valid.

Here's how your code will be used to find the one valid block at height 6929851:

```python
HEIGHT = 6929851
candidates = Bitcoin.rpc("getblocksbyheight", HEIGHT)
for bhash in candidates:
    block = Bitcoin.rpc("getblock", bhash)
    if validate_block(block):
        print(bhash)
        break
```

## Validating blocks

Validating a block is incredibly important to the strength of the network as each block is built on transactions of previous blocks, if any block is discovered to be invalid in the past it can cause huge ramifications as a large chain of blocks comes into question with a previously invalid block.

# Showtime!

The cameras are rolling, two billion humans worldwide are tuned in to the live stream. Only a few minutes remain until the next commercial break. Deborah Chunk is sweating. Somehow, Holocat is also sweating. Somewhere on the other end of the call, Vanderpoole must be sweating, too. This is your moment.

Starting with the valid block just before the one you found at height 6929851, find the longest chain of valid blocks you can. Store the chain as an array of block hashes. While you're at it, maintain an array of every invalid block you find as well, just to show the world how hard Vanderpoole tried to break bitcoin. It doesn't matter what order these invalid block hashes are in, but your valid chain MUST start with the hash of block 6929850 followed by one block hash at each height all the way up to the chain tip.

Vanderpoole is sneaky! He mined valid blocks on top of invalid blocks, and invalid blocks on top of short chains of valid blocks! It's a maze, a minefield, out there. You may need to keep track of several valid branches as you traverse the tree. There will be valid blocks with valid parents that are not in the longest chain! In the end, there will be only one valid leaf with a greater height than all the others.

Remember: Block objects returned by the JSON API have a property "prev" which identifies that block's parent by its hash:

A block is ONLY valid if:

Its coinbase output value is equal to the expected block subsidy plus the total transaction fees in the block.

AND

The block is a child of another VALID block. This is ensures a VALID CHAIN.

Return a JSON object with two arrays labeled "valid" and "invalid":

```json
{
  "valid": [...],
  "invalid": [...]
}
```

## Validating the chain

Validating the blockchain in Bitcoin is crucial for maintaining the integrity and security of the entire network. Each transaction must be verified by miners to ensure that it is legitimate and follows the consensus rules established by the network. This validation process prevents double-spending and fraud, allowing users to trust the system without needing a central authority. Moreover, it enhances transparency, as all validated transactions are recorded on a public ledger, enabling anyone to audit the history of transactions.
