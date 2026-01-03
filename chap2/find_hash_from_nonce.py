from hashlib import sha256

# Create a program that finds a sha256 hash starting with 5 zeroes.
# To submit your answer, return it from the function.


def find_hash_from_nonce(nonce):
    current = nonce
    while True:
        # Convert the current number to string and hash it
        hash_input = str(current).encode('utf-8')
        hash_result = sha256(hash_input).hexdigest()

        # Check if the hash starts with five zeros
        if hash_result.startswith('00000'):
            return current

        # Increment the nonce
        current += 1


# 0000029b76ad3cf9d86ad430754fb1d4478069affda61e8adaf4c57e9aa4b37b
# 7555928
