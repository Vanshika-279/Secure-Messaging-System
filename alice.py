import socket
import os

from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey
)

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


HOST = "127.0.0.1"
PORT = 5000


# ==================================================
# X25519 KEY GENERATION
# ==================================================

alice_private_key = X25519PrivateKey.generate()

print("Alice generated her private key.")


alice_public_key = alice_private_key.public_key()

print("Alice generated her public key.")


alice_public_bytes = alice_public_key.public_bytes_raw()

print("Alice public key:", alice_public_bytes.hex())


# ==================================================
# CONNECT TO SERVER
# ==================================================

alice = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

alice.connect((HOST, PORT))

print("Alice connected to server.")
 

# ==================================================
# SEND ALICE'S PUBLIC KEY
# ==================================================

alice.sendall(alice_public_bytes)

print("Alice sent her public key to server.")


# ==================================================
# RECEIVE BOB'S PUBLIC KEY
# ==================================================

bob_public_bytes = alice.recv(1024)

print("Alice received Bob's public key:")

print(bob_public_bytes.hex())


bob_public_key = X25519PublicKey.from_public_bytes(
    bob_public_bytes
)

print("Alice reconstructed Bob's public key.")


# ==================================================
# X25519 SHARED SECRET
# ==================================================

alice_shared_secret = alice_private_key.exchange(
    bob_public_key
)

print("Alice calculated the shared secret:")

print(alice_shared_secret.hex())


# ==================================================
# HKDF KEY DERIVATION
# ==================================================

alice_encryption_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b"SecureMessaging",
).derive(alice_shared_secret)


print("Alice derived the encryption key using HKDF:")

print(alice_encryption_key.hex())


# ==================================================
# CREATE CHACHA20-POLY1305
# ==================================================

chacha = ChaCha20Poly1305(alice_encryption_key)

print("Alice created ChaCha20-Poly1305 cipher.")


# ==================================================
# ALICE SENDS MESSAGE
# ==================================================

message = input("Alice, enter your message: ")

message = message.encode()

print("Alice's plaintext:")

print(message.decode())


# --------------------------------------------------
# Generate nonce
# --------------------------------------------------

nonce = os.urandom(12)


# --------------------------------------------------
# Encrypt message
# --------------------------------------------------

ciphertext = chacha.encrypt(
    nonce,
    message,
    None
)


# --------------------------------------------------
# Combine nonce + ciphertext
# --------------------------------------------------

encrypted_message = nonce + ciphertext


print("Alice encrypted the message.")

print("Alice is sending encrypted data to server...")


# --------------------------------------------------
# Send encrypted message
# --------------------------------------------------

alice.sendall(encrypted_message)


# ==================================================
# RECEIVE BOB'S REPLY
# ==================================================

encrypted_reply = alice.recv(4096)

print("Alice received encrypted reply.")


# --------------------------------------------------
# Extract nonce
# --------------------------------------------------

reply_nonce = encrypted_reply[:12]

reply_ciphertext = encrypted_reply[12:]


# --------------------------------------------------
# Decrypt Bob's message
# --------------------------------------------------

plaintext = chacha.decrypt(
    reply_nonce,
    reply_ciphertext,
    None
)


print("Bob's decrypted reply:")

print(plaintext.decode())


# ==================================================
# CLOSE
# ==================================================

alice.close()

print("Alice closed the connection.")