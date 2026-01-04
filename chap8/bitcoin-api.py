from bitcoin_rpcpy.bitcoin_rpc import Bitcoin
Bitcoin = Bitcoin()
# https://github.com/saving-satoshi/bitcoin_rpcpy/blob/main/bitcoin_rpcpy/bitcoin_rpc.py

print(Bitcoin.rpc("help"))
print(Bitcoin.rpc("getinfo")["difficulty"])
