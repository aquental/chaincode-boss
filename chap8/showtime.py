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


def showtime():
    height = 6929851
    tips = {}
    prevs = {}
    invalid = []
    valid = []
    last = Bitcoin.rpc("getinfo")["blocks"]
    while height <= last:
        candidates = Bitcoin.rpc("getblocksbyheight", height)
        for bhash in candidates:
            block = Bitcoin.rpc("getblock", bhash)
            # Don't even bother checking blocks with invalid parents
            if block["prev"] in invalid or not validate_block(block):
                invalid.append(bhash)
                continue
            # Valid blocks replace their parents in the tips list, extending the branch
            if block["prev"] in tips:
                del tips[block["prev"]]
            tips[block["hash"]] = block
            # save prev mapping for final output
            prevs[bhash] = block["prev"]
        height += 1
    # this is the tip of the longest valid chain
    best = max(tips.values(), key=lambda block: block["height"])
    # now reconstruct the chain of parent blocks
    best_hash = best["hash"]
    valid.append(best_hash)
    while best_hash in prevs:
        prev = prevs[best_hash]
        valid.append(prev)
        best_hash = prev
    # reverse it because the instructions said to start low and go to tip
    valid.reverse()
    return {
        "valid": valid,
        "invalid": invalid
    }


if __name__ == "__main__":
    result = showtime()
    print(f"\nValid blocks: {len(result['valid'])}")
    # for v in result["valid"]:
    #     print("  valid: ", v)
    print(f"\nInvalid blocks: {len(result['invalid'])}")
    # for iv in result["invalid"]:
    #     print("invalid: ", iv)
