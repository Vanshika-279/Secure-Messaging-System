# Secure Messaging with X25519, HKDF, and ChaCha20-Poly1305

A Python socket-based secure messaging demonstration in which Alice and
Bob establish a shared encryption key, exchange encrypted messages
through a relay server, and verify message integrity. The project also
includes a local attacker simulation that modifies an encrypted message
to demonstrate authenticated-encryption tamper detection.

## Project Overview

This project demonstrates how key agreement, key derivation,
authenticated encryption, and socket communication work together in a
simple client-server messaging system.

There are four Python programs:

  -----------------------------------------------------------------------
  File                                Role
  ----------------------------------- -----------------------------------
  `server.py`                         Relays public keys and encrypted
                                      messages between Alice and Bob
                                      without decrypting them

  `alice.py`                          Generates Alice's key pair, derives
                                      the shared key, sends an encrypted
                                      message, and decrypts Bob's reply

  `bob.py`                            Generates Bob's key pair, derives
                                      the same shared key, decrypts
                                      Alice's message, and sends an
                                      encrypted reply
                                      
`attacker.py`                         Replaces the normal relay server for a local
                                      tampering demonstration. Modifies one byte
                                      of Alice's encrypted message before forwarding
                                      it to Bob.

  
  -----------------------------------------------------------------------

## Cryptographic Concepts Used

### 1. X25519 key exchange

Alice and Bob each generate an X25519 private key and corresponding
public key. They exchange public keys through the server and use their
own private key with the other person's public key to calculate a shared
secret.

Both sides should independently derive the same shared secret:

``` text
Alice private key + Bob public key  -> Shared secret
Bob private key   + Alice public key -> Same shared secret
```

The private keys are not sent over the network.

### 2. HKDF with SHA-256

The shared secret is passed through HKDF (HMAC-based Extract-and-Expand
Key Derivation Function) using SHA-256.

The code derives a 32-byte encryption key and uses the context string
`SecureMessaging`.

### 3. ChaCha20-Poly1305

Alice and Bob use ChaCha20-Poly1305, an authenticated-encryption
algorithm.

It provides: - **Confidentiality:** encrypts the message so the relay
cannot read its contents. - **Integrity:** detects changes to the
encrypted data. - **Authentication:** verifies that the ciphertext and
its authentication tag are valid for the key and nonce.

A fresh 12-byte random nonce is generated for each message. The nonce is
sent together with the ciphertext:

``` text
Encrypted data = nonce + ciphertext and authentication tag
```

The nonce is not secret; the same nonce must not be reused with the same
key.

## Normal Message Flow

``` text
                 Public-key exchange
          +--------------------------------+
          |                                |
       Alice                              Bob
          |                                |
          +---------- Relay Server --------+
          |                                |
          |  Encrypted message: Alice -> Bob
          |  Encrypted reply:   Bob -> Alice
          +--------------------------------+
```

1.  Start `server.py`. It listens on `127.0.0.1:5000`.
2.  Start `alice.py` and `bob.py` in separate terminals.
3.  Alice and Bob generate their X25519 key pairs.
4.  Both clients send their public keys to the server.
5.  The server forwards each public key to the other client.
6.  Alice and Bob independently derive the same shared secret and then
    the same 32-byte encryption key using HKDF.
7.  Alice enters a message. Her program encrypts it with
    ChaCha20-Poly1305 and sends the nonce and ciphertext to the server.
8.  The server forwards the encrypted data to Bob without decrypting it.
9.  Bob decrypts and authenticates the message, then enters a reply.
10. Bob encrypts the reply and sends it through the server to Alice.
11. Alice decrypts and displays Bob's reply.

## Tampering Demonstration

`attacker.py` acts as an alternative local relay for the demonstration.
It listens on the same host and port as `server.py`, accepts Alice and
Bob's connections, and forwards their public keys.

When Alice sends an encrypted message, the program changes one byte of
the received data before forwarding it to Bob. Bob then attempts to
decrypt the modified message using ChaCha20-Poly1305.

Because the authentication check detects that the encrypted data has
changed, decryption raises `InvalidTag`, and Bob prints:

``` text
❌ Authentication failed.
```

This demonstrates why authenticated encryption is important: encrypted
data should not be accepted if its integrity check fails.

**Important:** Run `attacker.py` instead of `server.py` for this
demonstration. Both programs bind to `127.0.0.1:5000`, so they cannot
listen on that same address and port at the same time. Use this only
with the included local clients in an environment you control.

## Requirements

-   Python 3
-   The `cryptography` package
-   Three or four terminal windows

Install the dependency:

``` bash
python -m pip install cryptography
```

The code uses `public_bytes_raw()` for X25519 public-key serialization.
If your installed `cryptography` version does not provide this method,
upgrade the package:

``` bash
python -m pip install --upgrade cryptography
```

## How to Run

### A. Normal secure messaging

Open separate terminals in the project directory.

**Terminal 1 --- start the relay server:**

``` bash
python server.py
```

**Terminal 2 --- start Alice:**

``` bash
python alice.py
```

**Terminal 3 --- start Bob:**

``` bash
python bob.py
```

Enter Alice's message when prompted, then enter Bob's reply when
prompted. Keep the server running until the exchange is complete.

### B. Message-tampering demonstration

Stop the normal server and close any previous client processes.

**Terminal 1 --- start the local attacker simulation instead of the
server:**

``` bash
python attacker.py
```

**Terminal 2 --- start Alice:**

``` bash
python alice.py
```

**Terminal 3 --- start Bob:**

``` bash
python bob.py
```

Enter a message from Alice. The attacker simulation modifies the
encrypted data before forwarding it. Bob should report an authentication
failure when attempting to decrypt the modified message.

## Project Structure

``` text
.
├── alice.py
├── bob.py
├── server.py
├── attacker.py
└── README.md
```

## Security Scope and Limitations

This is an educational localhost demonstration, not a production-ready
messaging application.

-   The programs use `127.0.0.1`, so the demonstration runs on the local
    machine.
-   The relay forwards public keys but does not authenticate who
    supplied them. X25519 key exchange on its own does not prevent a
    man-in-the-middle attack.
-   The demonstration does not implement certificates, identity
    verification, or a trusted public-key authentication mechanism.
-   The socket code uses basic `recv()` calls. TCP is a byte stream, so
    a production implementation should add message framing and robust
    handling of partial reads and writes.
-   Nonces must never be reused with the same ChaCha20-Poly1305 key.
-   The attacker simulation changes encrypted data to demonstrate
    integrity protection; it does not recover plaintext or break the
    encryption.

Use the project to understand the interaction between X25519 key
agreement, HKDF key derivation, authenticated encryption, and message
forwarding.

## Author

Vanshika Chiratanagalla
vanshikachiratanagalla@gmail.com
