import socket
import hashlib
import os
import random
import time

# Server settings
HOST = '127.0.0.1'  # Localhost
PORT = 12345        # Port number
CHUNK_SIZE = 1024   # Chunk size (1 KB)

# Function to calculate the checksum of a file
def calculate_checksum(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            hasher.update(chunk)
    return hasher.hexdigest()

# Function to send file chunks
def send_file_chunks(client_socket, file_path):
    file_size = os.path.getsize(file_path)
    total_chunks = (file_size // CHUNK_SIZE) + (1 if file_size % CHUNK_SIZE else 0)
    
    chunks = []
    with open(file_path, "rb") as f:
        for i in range(total_chunks):
            chunk = f.read(CHUNK_SIZE)
            chunks.append((i, chunk))  # Store sequence number and chunk

    # Shuffle chunks to simulate out-of-order transmission
    random.shuffle(chunks)

    # Send the checksum first
    checksum = calculate_checksum(file_path)
    client_socket.sendall(checksum.encode() + b"\n")  # Send checksum with a newline

    print(f"Server: Sending {total_chunks} chunks with checksum: {checksum}")

    # Send chunks
    for seq_num, chunk in chunks:
        header = f"{seq_num:06d}".encode()  # Sequence number as a 6-digit string
        client_socket.sendall(header + chunk)
        time.sleep(0.01)  # Simulate network delay

    print("Server: File sent successfully!")

# Main server function
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"Server listening on {HOST}:{PORT}...")

        client_socket, addr = server_socket.accept()
        print(f"Connection established with {addr}")

        file_path = "sample.txt"  # File to send
        send_file_chunks(client_socket, file_path)

        client_socket.close()
        print("Server: Connection closed.")

# Run the server
if __name__ == "__main__":
    start_server()
