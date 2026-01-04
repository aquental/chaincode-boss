from bitcoin_rpcpy.bitcoin_rpc import Bitcoin
Bitcoin = Bitcoin()

BLOCK_HASH = "dab5708b1b3db05407e35b2004156d74f7bb5bed7f677743945cac1465b5838f"
TX_HASH = "7bd09aa3b4795be2839d9159edff0811d6d4ec5a64abd81c0da1e73ab00bf520"

# First we need to find the transaction with the corresponding tx hash
# build a function that will call get_tx_Fee when it finds a transaction with the correct TX_HASH
# this is the function that we will call for validation


def get_block_tx_fee():
    # Retrieve the full block data (verbosity 2 to get full transaction details)
    block = Bitcoin.rpc("getblock", BLOCK_HASH)
    # print(block)
    # Iterate through all transactions in the block
    for tx in block["txs"]:
        if tx["txid"] == TX_HASH:
            # Found the transaction — calculate its fee
            # print(f"Found transaction {TX_HASH} in block {BLOCK_HASH}: {tx}")
            return get_tx_fee(tx)

    # If transaction not found (should not happen in challenge)
    raise ValueError(f"Transaction {TX_HASH} not found in block {BLOCK_HASH}")

# Now let's find the miner's fee for this transaction.
# with the transaction from above determine the fee paid to miners


def get_tx_fee(tx):
    total_input_value = 0
    total_output_value = 0

    # print(f"Calculating fee for transaction {tx['txid']}")
    # Sum up all input values (vout of previous outputs)
    for vin in tx["inputs"]:
        total_input_value += vin["value"]

    # Sum up all output values in the current transaction
    for vout in tx["outputs"]:
        total_output_value += vout["value"]

    # The fee is the difference: inputs - outputs (in BTC)
    fee = total_input_value - total_output_value
    # print(f"Calculated fee: {fee} BTCs: inputs {total_input_value} - outputs {total_output_value}")

    return fee


# Example usage (for testing)
if __name__ == "__main__":
    fee = get_block_tx_fee()
    print(f"The miner fee for transaction {TX_HASH} is: {fee} satoshis")
