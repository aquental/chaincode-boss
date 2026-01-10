def xor_hex_strings_int(s1, s2):
    """XOR two hex strings by converting to integers."""
    # Convert hex strings to integers (base 16)
    int1 = int(s1, 16)
    int2 = int(s2, 16)

    # Perform bitwise XOR
    xored_int = int1 ^ int2

    # Convert the result back to a hex string, ensuring zero padding
    # to match the length of the longer input string.
    # The '{:x}'.format() method is clean and avoids the '0x' prefix.
    # The zfill() ensures leading zeros are included if necessary.
    result_hex = format(xored_int, 'x').zfill(max(len(s1), len(s2)))
    return result_hex


# test
secret_message = "read from environment variable"
saving_key = "read from environment variable"
message = xor_hex_strings_int(secret_message, saving_key)
print(f"XOR of {secret_message} and {saving_key} is: {message}")
# decode the message
url = ''.join(chr(int(message[i:i+2], 16))
              for i in range(0, len(message), 2))

print(url)
