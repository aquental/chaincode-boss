from bitcoin_rpcpy.bitcoin_rpc import Bitcoin
Bitcoin = Bitcoin()


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


def get_subsidy(height):
    halvings = height // 210000
    if halvings >= 64:
        return 0
    subsidy = 5000000000
    subsidy >>= halvings
    return subsidy


def validate_block(block):
    fees = 0
    subsidy = get_subsidy(block["height"])
    # Don't include the coinbase in this sum!
    for tx in block["txs"][1:]:
        fees += get_tx_fee(tx)
    return subsidy + fees == block["txs"][0]["outputs"][0]["value"]
