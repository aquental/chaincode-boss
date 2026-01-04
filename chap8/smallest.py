from bitcoin_rpcpy.bitcoin_rpc import Bitcoin
Bitcoin = Bitcoin()

CODE_CHALLENGE_2_HEIGHT = 6929996
answer = None


def get_block_height(height):
    tx_count = float("inf")
    blocks = Bitcoin.rpc("getblocksbyheight", height)
    return find_min_trx(blocks)


def find_min_trx(block_list):
    hash = None
    tx_count = float("inf")
    for block in block_list:
        info = Bitcoin.rpc("getblock", block)
        txs = info["txs"]
        if len(txs) < tx_count:
            tx_count = len(txs)
            hash = info["hash"]
    return hash


answer = get_block_height(CODE_CHALLENGE_2_HEIGHT)
print(answer)
