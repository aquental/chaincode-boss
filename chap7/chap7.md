# Code Challenge

This is the code you find on Vanderpoole's server. It imports the current mempool from a JSON file and stores all the unconfirmed transactions in memory as instances of the MempoolTransaction class. The function that Vanderpoole has crippled is `assemble_block()`. If you run the code as Vanderpoole left it, you will see the problem right away.

You need to fix the block assembly function not only to build valid blocks but also maximize the fees in the block, so the miners can earn the most profit possible given the consensus rules. The most critical consensus rules you will need to pay attention to restrict the total [transaction weight](https://chat.bitcoinsearch.xyz/?author=holocat&question=what%2520are%2520weighted%2520units) and the [order of transactions](https://chat.bitcoinsearch.xyz/?author=holocat&question=what%2520order%2520do%2520transactions%2520need%2520to%2520be%2520in%2520a%2520block) in the block.

You can make the following assumptions to complete your mission:

- All transactions in the mempool have already been verified as valid.
- The coinbase transaction, and the weight it contributes to the block, can be ignored.
  You can view the entire raw mempool JSON file [here](https://github.com/saving-satoshi/resources/blob/main/chapter-7/mempool.json).

Or browse an excerpt of the file in this table for some basic patterns:

| Transaction ID | Fee<br>(Satoshis) | Weight<br>(WU) | Ancestors            |
| -------------- | ----------------- | -------------- | -------------------- |
| b27f86d3       | 43430             | 2020           |                      |
| c27b4d2e       | 30168             | 1676           | bd1d83ca<br>f29aec75 |
| 18725711       | 5520              | 1840           | 3c64a457<br>3c8abf73 |
| 92b1ecf5       | 24302             | 1676           | 398695a6<br>10025d80 |
| 8e8c8624       | 8990              | 1160           | 01f6094b             |
| 5f6c9a80       | 13716             | 1524           | 64121ab1             |
| e140fa46       | 13020             | 1488           | 7675c31c             |
| d7066e71       | 16416             | 1152           |                      |
| 88016f17       | 15200             | 1600           | 5e518bbe             |
| 8fa820d5       | 20221             | 1108           | 38a62dcc             |

View the json file [here](./mempool.json) for the rest of the transaction data

## Bytes vs Weight Units

In bitcoin block construction, "weight units" (WU) and "bytes" are two different metrics used to measure the size of transactions and blocks.

### Bytes

Bytes refer to the raw size of a transaction or block in terms of actual data. It is the literal size of the transaction data when it is serialized (converted into a format that can be stored or transmitted). Before the implementation of Segregated Witness (SegWit), the block size was limited to 1 megabyte (1 MB), measured in bytes.

### Weighted Units

Weighted units are a more complex metric introduced with SegWit in Bitcoin Improvement Proposal 141 BIP 141. This system aims to more fairly allocate block space by considering the impact of witness data separately.

In our lesson here its just important to note we are using weight units to calculate the maximum block size and the same for each tx so make sure your block does not exceed the maximum size of 4000000 weight units.
