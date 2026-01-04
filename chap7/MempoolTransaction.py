import json
from collections import OrderedDict

# Standard Bitcoin block weight limit (in weight units)
MAX_BLOCK_WEIGHT = 4_000_000


class MempoolTransaction:
    def __init__(self, json_data):
        self.txid = json_data["txid"]
        self.weight = json_data["weight"]
        self.fee = json_data["fee"]
        # Ensure parents is always a list
        self.parents = json_data.get("parents", [])

    # @prop erty
    def feerate(self):
        return self.fee / self.weight if self.weight > 0 else 0


def assemble_block(mempool):
    """
    Constructs a block by greedily selecting transactions with the highest feerate,
    while allowing inclusion of transactions whose parents are already in the block
    (opportunistic ancestor inclusion).
    """
    block = []
    block_weight = 0

    # Create a mutable list of transactions and compute feerate
    transactions = list(mempool)
    for tx in transactions:
        tx.feerate = tx.fee / tx.weight  # Add feerate as attribute

    def get_sorted_candidates():
        return sorted(
            transactions,
            key=lambda tx: tx.feerate,
            reverse=True
        )

    included_txids = set()  # Track which txids are already in the block

    while True:
        added = False
        candidates = get_sorted_candidates()
        print(
            f"[assemble_block] Candidates left: {len(candidates)}, Block weight: {block_weight}, % of max: {block_weight / MAX_BLOCK_WEIGHT:.2%}")

        for tx in candidates:
            # Check if all parents are either not in mempool or already included
            if any(parent in {t.txid for t in transactions} and parent not in included_txids
                   for parent in tx.parents):
                continue  # Skip: has unconfirmed parent still in mempool

            # Check weight limit
            if block_weight + tx.weight > MAX_BLOCK_WEIGHT:
                print(
                    f"[assemble_block] Block weight exceeded: {block_weight + tx.weight} > {MAX_BLOCK_WEIGHT} - TOO HEAVY")
                continue  # Too heavy

            # Valid to include!
            block.append(tx.txid)
            print(f"[assemble_block] Adding txid: {tx.txid}")
            block_weight += tx.weight
            included_txids.add(tx.txid)
            transactions.remove(tx)  # Remove from consideration
            added = True
            break  # Restart loop to re-evaluate best candidate

        if not added:
            break  # No more valid transactions can be added

    return block


def import_mempool_from_json_file(file_path):
    with open(file_path, 'r') as file:
        # Preserve order if needed
        data = json.load(file, object_pairs_hook=OrderedDict)
    mempool = []
    for tx in data:
        mempool.append(MempoolTransaction(tx))
    print("[import_mempool_from_json_file] txs: ", len(mempool))
    return mempool


def run():
    mempool = import_mempool_from_json_file("mempool.json")
    block = assemble_block(mempool)
    return block


if __name__ == "__main__":
    block = run()
    print("Assembled Block Transactions (txids):")
    for txid in block:
        print(txid)
