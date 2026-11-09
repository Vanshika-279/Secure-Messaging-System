# import socket


# HOST = "127.0.0.1"
# PORT = 5000


# # --------------------------------------------------
# # 1. Create server socket
# # --------------------------------------------------

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# # --------------------------------------------------
# # 2. Bind server to IP and port
# # --------------------------------------------------

# server.bind((HOST, PORT))


# # --------------------------------------------------
# # 3. Listen for Alice and Bob
# # --------------------------------------------------

# server.listen(2)

# print("Server is waiting for Alice and Bob...")


# # --------------------------------------------------
# # 4. Accept Alice
# # --------------------------------------------------

# alice_connection, alice_address = server.accept()

# print("Alice connected:", alice_address)


# # --------------------------------------------------
# # 5. Receive Alice's public key
# # --------------------------------------------------

# alice_public_bytes = alice_connection.recv(1024)

# print("Server received Alice's public key.")


# # --------------------------------------------------
# # 6. Accept Bob
# # --------------------------------------------------

# bob_connection, bob_address = server.accept()

# print("Bob connected:", bob_address)


# # --------------------------------------------------
# # 7. Receive Bob's public key
# # --------------------------------------------------

# bob_public_bytes = bob_connection.recv(1024)

# print("Server received Bob's public key.")


# # --------------------------------------------------
# # 8. Send Alice's public key to Bob
# # --------------------------------------------------

# bob_connection.sendall(alice_public_bytes)

# print("Server sent Alice's public key to Bob.")


# # --------------------------------------------------
# # 9. Send Bob's public key to Alice
# # --------------------------------------------------

# alice_connection.sendall(bob_public_bytes)

# print("Server sent Bob's public key to Alice.")


# # --------------------------------------------------
# # 10. Receive encrypted message from Alice
# # --------------------------------------------------

# encrypted_message = alice_connection.recv(4096)

# print("Server received encrypted message from Alice.")


# # --------------------------------------------------
# # 11. Forward encrypted message to Bob
# # --------------------------------------------------

# bob_connection.sendall(encrypted_message)

# print("Server forwarded encrypted message to Bob.")


# # --------------------------------------------------
# # 12. Receive encrypted reply from Bob
# # --------------------------------------------------

# encrypted_reply = bob_connection.recv(4096)

# print("Server received encrypted reply from Bob.")


# # --------------------------------------------------
# # 13. Forward encrypted reply to Alice
# # --------------------------------------------------

# alice_connection.sendall(encrypted_reply)

# print("Server forwarded encrypted reply to Alice.")


# # --------------------------------------------------
# # 14. Close connections
# # --------------------------------------------------

# alice_connection.close()
# bob_connection.close()
# server.close()

# print("Server closed.")

import socket
import threading


HOST = "127.0.0.1"
PORT = 5000


# ==================================================
# CREATE SERVER
# ==================================================

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind((HOST, PORT))

server.listen(2)

print("Server is waiting for Alice and Bob...")


# ==================================================
# ACCEPT ALICE
# ==================================================
 
alice_connection, alice_address = server.accept()

print("Alice connected:", alice_address)


# ==================================================
# RECEIVE ALICE PUBLIC KEY
# ==================================================

alice_public_bytes = alice_connection.recv(1024)

print("Server received Alice's public key.")


# ==================================================
# ACCEPT BOB
# ==================================================

bob_connection, bob_address = server.accept()

print("Bob connected:", bob_address)


# ==================================================
# RECEIVE BOB PUBLIC KEY
# ==================================================

bob_public_bytes = bob_connection.recv(1024)

print("Server received Bob's public key.")


# ==================================================
# EXCHANGE PUBLIC KEYS
# ==================================================

bob_connection.sendall(alice_public_bytes)

print("Server sent Alice's public key to Bob.")


alice_connection.sendall(bob_public_bytes)

print("Server sent Bob's public key to Alice.")


# ==================================================
# ALICE → BOB
# ==================================================

def forward_alice_to_bob():

    while True:

        try:

            data = alice_connection.recv(4096)

            if not data:
                break

            bob_connection.sendall(data)

            print("Encrypted message: Alice → Bob")

        except:

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

            print("Encrypted message: Bob → Alice")

        except:

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

server.close()

print("Server closed.")