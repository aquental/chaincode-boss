uncompressed_key = (
    "e8e24c60463d469a056be712bd838f8e2bf47771a2ee62ea244069e4e637b317,5ec8433d3801945a105e383c597ec9c0ff6d2bc287d66f61c93e5d31781b1615")

# Determine if the y coordinate is even or odd and prepend
# the corresponding header byte to the x coordinate.
# Return a hex string


def compress_publickey(public_key):
    header_byte = {
        "y_is_even": "02",
        "y_is_odd":  "03"
    }
    x, y = public_key.split(',')
    y_int = int(y, 16)
    prefix = header_byte["y_is_even"] if (
        y_int % 2 == 0) else header_byte["y_is_odd"]
    return prefix + x

# 03e8e24c60463d469a056be712bd838f8e2bf47771a2ee62ea244069e4e637b317
