import socket
import hashlib

# Client settings
HOST = '127.0.0.1'  # Localhost (same as server)
PORT = 12345        # Port number (same as server)
CHUNK_SIZE = 1024   # Chunk size (1 KB)

# Function to calculate the checksum of the reassembled file
def calculate_checksum(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            hasher.update(chunk)
    return hasher.hexdigest()

# Function to receive and reassemble file chunks
def receive_file_chunks(client_socket):
    received_chunks = {}

    # Receive the checksum first
    print("Client: Waiting to receive checksum...")
    server_checksum = client_socket.recv(1024).decode().strip()  # Read checksum correctly
    print(f"Client: Received checksum {server_checksum}")

    # Receive chunks
    while True:
        print("Client: Waiting for chunk header...")
        header = client_socket.recv(6)  # Try reading the sequence number
        if not header or header == b"\n":  # Check for end of transmission
            print("Client: No more data received. Ending transmission.")
            break

        try:
            seq_num = int(header.decode().strip())  # Convert to integer
        except ValueError:
            print(f"Client: Skipping invalid header {header}")
            continue  # Skip invalid headers and continue receiving chunks

        chunk = client_socket.recv(CHUNK_SIZE)

        received_chunks[seq_num] = chunk  # Store in dictionary

    print("Client: File received. Reassembling...")

    # Sort and write the file
    with open("received_file.txt", "wb") as f:
        for seq_num in sorted(received_chunks.keys()):
            f.write(received_chunks[seq_num])

    # Calculate checksum
    client_checksum = calculate_checksum("received_file.txt")
    print(f"Client: Recalculated checksum {client_checksum}")

    # Verify file integrity
    if server_checksum == client_checksum:
        print("Client: File transfer successful! ✅")
    else:
        print("Client: File corrupted! ❌")

# Main client function
def start_client():
    try:
        print("Client: Attempting to connect to the server...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            print(f"Client: Connected to {HOST}:{PORT}")
            
            receive_file_chunks(client_socket)

            print("Client: Connection closed.")
    except Exception as e:
        print(f"Client Error: {e}")

# Run the client
if __name__ == "__main__":
    start_client()
