from bitcoin_rpcpy.bitcoin_rpc import Bitcoin
Bitcoin = Bitcoin()


def get_subsidy(height):
    halvings = height // 210000
    if halvings >= 64:
        return 0
    subsidy = 5000000000
    subsidy >>= halvings
    return subsidy


print(get_subsidy(6929996))
