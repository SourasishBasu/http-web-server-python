import os
import socket
import threading
import argparse
import gzip

BASE_DIRECTORY = './files/'


def send_response(req):
    status_lines = req.split("\r\n")
    # print(status_lines)
    method, path, _ = status_lines[0].split(" ")

    if path == "/":
        resp = "HTTP/1.1 200 OK\r\n\r\n".encode()

    elif path.startswith('/echo'):
        _, info = path[1:].split("/")

        if status_lines[2].startswith('Accept-Encoding'):
            _, compressions = status_lines[2].split(": ")

            if 'gzip' in (compressions.split(', ')):
                body = gzip.compress(info.encode())
                resp = (b"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: "
                        + str(len(body)).encode()
                        + b"\r\n\r\n"
                        + body
                        )
            else:
                resp = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(info)}\r\n\r\n{info}".encode()

        else:
            resp = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(info)}\r\n\r\n{info}".encode()

    elif path.startswith('/user-agent'):
        _, agent = status_lines[2].split(" ")
        resp = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(agent)}\r\n\r\n{agent}".encode()

    elif path.startswith('/files'):
        _, file = path[1:].split("/")
        if method == 'GET':
            if os.path.exists(os.path.join(BASE_DIRECTORY, file)):
                with open(f'{BASE_DIRECTORY}{file}', 'r') as f:
                    contents = f.read()
                    resp = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(contents)}\r\n\r\n{contents}".encode()
            else:
                resp = "HTTP/1.1 404 Not Found\r\n\r\n".encode()

        elif method == 'POST':
            with open(f'{BASE_DIRECTORY}{file}', 'w') as f:
                f.write(status_lines[4])
                resp = f"HTTP/1.1 201 Created\r\n\r\n".encode()

    else:
        resp = "HTTP/1.1 404 Not Found\r\n\r\n".encode()

    return resp


def handle_client(client_socket, address):
    print(f"Connection established to address {address} from server.")

    req = client_socket.recv(1024).decode()
    resp = send_response(req)
    client_socket.send(resp)
    client_socket.close()


def main():
    parser = argparse.ArgumentParser(description="Simple HTTP Web server")
    parser.add_argument('-d', '--directory', type=str, help='Directory address on server for requesting files')
    args = parser.parse_args()

    global BASE_DIRECTORY
    BASE_DIRECTORY = args.directory

    # reuse_port to be removed for running on windows
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()
    print("Server is running on port 4221...")

    try:
        while True:
            print("Waiting for connection")
            client_socket, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            thread.start()

    except KeyboardInterrupt:
        print("\nServer is shutting down...")
    finally:
        server_socket.close()
        print("Server has been closed.")


if __name__ == "__main__":
    main()
