# Source can be found at https://github.com/saving-satoshi/challenges/blob/master/chapter8/python/lib/bitcoin_rpc.py

from copy import deepcopy
from json import load
from pathlib import Path


class Bitcoin:
    def __init__(self):
        with open(f"{'chainstate.json'}", "r") as file:
            self.state = load(file)

    def rpc(self, method=None, params=None):
        if not method:
            raise Exception(
                "First argument 'method' is required.\nExecute `rpc('help')` for help")
        if hasattr(self, method):
            func = getattr(self, method)
            if params:
                return func(params)
            else:
                return func()
        else:
            raise Exception(
                f"Method '{method}' not found\nExecute `rpc('help')` for help")

    def help(self):
        return """
Bitcoin Core v253.1.2
RPC commands:

getinfo
    Returns basic node and network information

help
    Returns this message

getblock ( hash )
    Returns JSON-formatted block with the given hash

getblocksbyheight ( height )
    Returns an array of hashes of blocks at the specified height in the tree
"""

    def getblocksbyheight(self, height=None):
        if not height:
            raise Exception(
                "Method 'getblocksbyheight' requires one argument (height)")
        if str(height) not in self.state["blocks_by_height"]:
            raise Exception(f"No blocks available at height {height}")
        return self.state["blocks_by_height"][str(height)]

    def getblock(self, bhash=None):
        if not bhash:
            raise Exception("Method 'getblock' requires one argument (hash)")
        if bhash not in self.state["blocks_by_hash"]:
            raise Exception(f"Block not found with hash {bhash}")
        block = deepcopy(self.state["blocks_by_hash"][bhash])
        del block["valid"]
        return block

    def getinfo(self):
        return {
            "version": "Bitcoin Core v253.1.2",
            "blocks": int(max(list(self.state["blocks_by_height"].keys()))),
            "headers": int(max(list(self.state["blocks_by_height"].keys()))),
            "prune_height": int(min(list(self.state["blocks_by_height"].keys()))),
            "verification_progress": "1.0000",
            "difficulty": "3007592928481984.23",
            "peers": 23
        }
