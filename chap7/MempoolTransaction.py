import json
import heapq
from collections import OrderedDict
from collections import defaultdict

# Standard Bitcoin block weight limit (in weight units)
MAX_BLOCK_WEIGHT = 4_000_000
LOG = 1


class MempoolTransaction:
    def __init__(self, json_data):
        self.txid = json_data["txid"]
        self.weight = json_data["weight"]
        self.fee = json_data["fee"]
        self.parents = json_data.get("parents", [])
        # Pre-compute feerate once
        self.feerate = self.fee / self.weight if self.weight > 0 else 0

    def __lt__(self, other):
        if abs(self.feerate - other.feerate) < 1e-8:  # nearly equal feerate
            return self.fee > other.fee
        return self.feerate > other.feerate


def assemble_block(mempool):
    """
    High-performance block assembly using a priority queue (max-heap by feerate)
    and efficient dependency tracking.
    """
    if not mempool:
        return []

    block = []
    block_weight = 0

    # Build fast lookup structures
    tx_by_id = {tx.txid: tx for tx in mempool}
    # txid → set of unconfirmed parent txids
    unconfirmed_parents = defaultdict(set)

    # Initialize dependency counts: how many parents are still unconfirmed
    dependency_count = {}
    for tx in mempool:
        unconfirmed = 0
        for parent in tx.parents:
            if parent in tx_by_id:  # parent is in mempool
                unconfirmed_parents[parent].add(tx.txid)
                unconfirmed += 1
        dependency_count[tx.txid] = unconfirmed

    # Use a max-heap (priority queue) sorted by feerate
    # Python's heapq is min-heap → use negative feerate or __lt__ override
    candidates = [tx for tx in mempool if dependency_count[tx.txid] == 0]
    heapq.heapify(candidates)  # O(n)

    included = set()

    while candidates:
        tx = heapq.heappop(candidates)  # O(log n)
        if (LOG):
            print(
                f"[assemble_block] Processing tx: {tx.txid}, weight: {tx.weight}, feerate: {tx.feerate:.2f}, % of max weight: {tx.weight / MAX_BLOCK_WEIGHT:.6f}")

        if tx.txid in included:
            if (LOG):
                print(
                    f"[assemble_block] Skipping already included tx: {tx.txid}")
            continue  # Skip if already added (rare race)

        # Check weight
        if block_weight + tx.weight > MAX_BLOCK_WEIGHT:
            if (LOG):
                print(
                    f"[assemble_block] Skipping tx: {tx.txid}, weight: {tx.weight}, feerate: {tx.feerate:.2f}")
            continue  # Can't fit anymore

        # Include it!
        block.append(tx.txid)
        block_weight += tx.weight
        included.add(tx.txid)
        if (LOG):
            print(
                f"[assemble_block] Included tx: {tx.txid}, weight: {tx.weight}, feerate: {tx.feerate:.2f}")

        # Unlock children (reduce their dependency count)
        for child_txid in unconfirmed_parents[tx.txid]:
            dependency_count[child_txid] -= 1
            if dependency_count[child_txid] == 0:
                child_tx = tx_by_id[child_txid]
                heapq.heappush(candidates, child_tx)  # O(log n)

    return block


def import_mempool_from_json_file(file_path):
    with open(file_path, 'r') as file:
        # Preserve order if needed
        data = json.load(file, object_pairs_hook=OrderedDict)
    mempool = []
    for tx in data:
        mempool.append(MempoolTransaction(tx))
    if (LOG):
        print("[import_mempool_from_json_file] txs: ", len(mempool))
    return mempool


def run():
    mempool = import_mempool_from_json_file("mempool.json")
    block = assemble_block(mempool)
    if (LOG):
        print("[run] block has {len(block)} lines")
    return block


if __name__ == "__main__":
    block = run()
    if (LOG):
        print("Assembled Block Transactions (txids):")
        print("number of txs:", len(block))
        # print(block)
    for txid in block:
        print(txid)
