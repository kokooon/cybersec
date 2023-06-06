import secrets

def generate_random_key(length):
    num_bytes = length // 2
    random_bytes = secrets.token_bytes(num_bytes)
    random_key = random_bytes.hex()
    return random_key

if __name__ == "__main__":
    key_length = 64
    random_key = generate_random_key(key_length)
    with open("64.key", "wb") as f:
        f.write(random_key.encode())
