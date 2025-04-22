import os
from base64 import b64encode

print("Starting...")

key = os.urandom(32)

print("Saving...")

with open("secrets/secret.txt", "w") as f:
    f.write(b64encode(key).decode())

print("Done!")