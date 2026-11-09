import socket
import os

from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey
)

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from cryptography.exceptions import InvalidTag


HOST = "127.0.0.1"
PORT = 5000


# ==================================================
# X25519 KEY GENERATION
# ==================================================

bob_private_key = X25519PrivateKey.generate()

print("Bob generated his private key.")


bob_public_key = bob_private_key.public_key()

print("Bob generated his public key.")


bob_public_bytes = bob_public_key.public_bytes_raw()

print("Bob public key:", bob_public_bytes.hex())


# ==================================================
# CONNECT TO SERVER
# ==================================================

bob = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

bob.connect((HOST, PORT))

print("Bob connected to server.")


# ==================================================
# SEND BOB'S PUBLIC KEY
# ==================================================

bob.sendall(bob_public_bytes)

print("Bob sent his public key to server.")


# ==================================================
# RECEIVE ALICE'S PUBLIC KEY
# ==================================================

alice_public_bytes = bob.recv(1024)

print("Bob received Alice's public key:")

print(alice_public_bytes.hex())


alice_public_key = X25519PublicKey.from_public_bytes(
    alice_public_bytes
)

print("Bob reconstructed Alice's public key.")


# ==================================================
# X25519 SHARED SECRET
# ==================================================

bob_shared_secret = bob_private_key.exchange(
    alice_public_key
)

print("Bob calculated the shared secret:")

print(bob_shared_secret.hex())


# ==================================================
# HKDF KEY DERIVATION
# ==================================================

bob_encryption_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b"SecureMessaging",
).derive(bob_shared_secret)


print("Bob derived the encryption key using HKDF:")

print(bob_encryption_key.hex())


# ==================================================
# CREATE CHACHA20-POLY1305
# ==================================================

chacha = ChaCha20Poly1305(bob_encryption_key)

print("Bob created ChaCha20-Poly1305 cipher.")


# ==================================================
# RECEIVE ALICE'S MESSAGE
# ==================================================

encrypted_message = bob.recv(4096)

print("Bob received encrypted message.")


# --------------------------------------------------
# Extract nonce and ciphertext
# --------------------------------------------------

nonce = encrypted_message[:12]

ciphertext = encrypted_message[12:]


# --------------------------------------------------
# Decrypt Alice's message
# --------------------------------------------------

try:

    plaintext = chacha.decrypt(
        nonce,
        ciphertext,
        None
    )

    print("Alice's decrypted message:")

    print(plaintext.decode())


except InvalidTag:

    print("❌ Authentication failed.")

    bob.close()

    exit()


# ==================================================
# BOB SENDS REPLY
# ==================================================

reply = input("Bob, enter your reply: ")

reply = reply.encode()


print("Bob's plaintext:")

print(reply.decode())


# --------------------------------------------------
# Generate nonce
# --------------------------------------------------

reply_nonce = os.urandom(12)


# --------------------------------------------------
# Encrypt reply
# --------------------------------------------------

reply_ciphertext = chacha.encrypt(
    reply_nonce,
    reply,
    None
)


# --------------------------------------------------
# Combine nonce + ciphertext
# --------------------------------------------------

encrypted_reply = reply_nonce + reply_ciphertext


print("Bob encrypted the reply.")


# --------------------------------------------------
# Send reply
# --------------------------------------------------

bob.sendall(encrypted_reply)

print("Bob sent encrypted reply to server.")


# ==================================================
# CLOSE
# ==================================================

bob.close()

print("Bob closed the connection.")