import socket
import threading


HOST = "127.0.0.1"
PORT = 5000


# ==================================================
# CREATE ATTACKER SOCKET
# ==================================================

attacker = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

attacker.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

attacker.bind((HOST, PORT))

attacker.listen(2)

print("Attacker is waiting for Alice and Bob...")


# ==================================================
# ACCEPT ALICE
# ==================================================

alice_connection, alice_address = attacker.accept()

print("Alice connected to attacker:", alice_address)


# ==================================================
# RECEIVE ALICE PUBLIC KEY
# ==================================================

alice_public_bytes = alice_connection.recv(1024)

print("Attacker received Alice's public key.")


# ==================================================
# ACCEPT BOB
# ==================================================

bob_connection, bob_address = attacker.accept()

print("Bob connected to attacker:", bob_address)


# ==================================================
# RECEIVE BOB PUBLIC KEY
# ==================================================

bob_public_bytes = bob_connection.recv(1024)

print("Attacker received Bob's public key.")


# ==================================================
# FORWARD PUBLIC KEYS
# ==================================================

bob_connection.sendall(alice_public_bytes)

print("Attacker forwarded Alice's public key to Bob.")


alice_connection.sendall(bob_public_bytes)

print("Attacker forwarded Bob's public key to Alice.")


# ==================================================
# ALICE → BOB
# ==================================================

def forward_alice_to_bob():

    while True:

        try:

            data = alice_connection.recv(4096)

            if not data:
                break

            print("\n[ATTACKER] Intercepted encrypted message from Alice.")

            # ------------------------------------------
            # SIMULATE TAMPERING
            # ------------------------------------------

            tampered_data = bytearray(data)

            # Change one byte
            tampered_data[-1] ^= 1

            tampered_data = bytes(tampered_data)

            print("[ATTACKER] Modified 1 byte of encrypted data.")

            # ------------------------------------------
            # SEND MODIFIED DATA TO BOB
            # ------------------------------------------

            bob_connection.sendall(tampered_data)

            print("[ATTACKER] Forwarded tampered message to Bob.")

        except Exception as e:

            print("[ATTACKER] Error:", e)

            break


# ==================================================
# BOB → ALICE
# ==================================================

def forward_bob_to_alice():

    while True:

        try:

            data = bob_connection.recv(4096)

            if not data:
                break

            alice_connection.sendall(data)

            print("[ATTACKER] Forwarded Bob's encrypted reply to Alice.")

        except Exception as e:

            print("[ATTACKER] Error:", e)

            break


# ==================================================
# CREATE THREADS
# ==================================================

alice_to_bob = threading.Thread(
    target=forward_alice_to_bob
)

bob_to_alice = threading.Thread(
    target=forward_bob_to_alice
)


# ==================================================
# START THREADS
# ==================================================

alice_to_bob.start()

bob_to_alice.start()


# ==================================================
# WAIT FOR THREADS
# ==================================================

alice_to_bob.join()

bob_to_alice.join()


# ==================================================
# CLOSE
# ==================================================

alice_connection.close()

bob_connection.close()

attacker.close()

print("Attacker closed.")