import os
import socket
import threading
import argparse
import gzip

# Default directory for serving files
BASE_DIRECTORY = './files/'

# HTTP header contents declared
CONTENT_TYPE_PLAIN = "Content-Type: text/plain\r\n"
CONTENT_TYPE_OCTET_STREAM = "Content-Type: application/octet-stream\r\n"
HTTP_OK = "HTTP/1.1 200 OK\r\n"
HTTP_NOT_FOUND = "HTTP/1.1 404 Not Found\r\n"
HTTP_CREATED = "HTTP/1.1 201 Created\r\n"
ENCODING_HEADER = "Content-Encoding: gzip\r\n"


def send_response(req):
    """
    Returns encoded response based on the endpoint the client socket makes the request to.

    Available Endpoints:
    - /
    - /echo
    - /user-agent
    - /files

    :param req:
    :return res:
    """

    # Parsing HTTP request to get the request line
    status_lines = req.split("\r\n")
    method, path, _ = status_lines[0].split(" ")

    # Responding with 200 OK to client if connection to server is successful
    if path == "/":
        res = HTTP_OK + "\r\n"

    # /echo
    elif path.startswith('/echo'):

        # Extracting data from endpoint path in request
        _, info = path[1:].split("/")

        # Checking for valid compression options from status lines (gzip)
        if status_lines[2].lower().startswith('accept-encoding'):
            _, compressions = status_lines[2].split(": ")

            if 'gzip' in (compressions.split(', ')):
                body = gzip.compress(info.encode())

                return (HTTP_OK.encode()
                        + ENCODING_HEADER.encode()
                        + CONTENT_TYPE_PLAIN.encode()
                        + f"Content-Length: {len(body)}\r\n\r\n".encode()
                        + body)
            else:
                res = (HTTP_OK
                       + CONTENT_TYPE_PLAIN
                       + f"Content-Length: {len(info)}\r\n\r\n"
                       + info)

        else:
            res = (HTTP_OK
                   + CONTENT_TYPE_PLAIN
                   + f"Content-Length: {len(info)}\r\n\r\n"
                   + info)

    # /user-agent
    elif path.startswith('/user-agent'):

        # Extracting client's user-agent from request status lines
        _, agent = status_lines[2].split(" ")

        res = (HTTP_OK
               + CONTENT_TYPE_PLAIN
               + f"Content-Length: {len(agent)}\r\n\r\n"
               + agent)

    # /files
    elif path.startswith('/files'):
        _, file = path[1:].split("/")

        # Checking the request method and serving/writing to correct file
        if method.lower() == 'get':
            if os.path.exists(os.path.join(BASE_DIRECTORY, file)):
                with open(f'{BASE_DIRECTORY}{file}', 'r') as f:
                    contents = f.read()

                    res = (HTTP_OK
                           + CONTENT_TYPE_OCTET_STREAM
                           + f"Content-Length: {len(contents)}\r\n\r\n"
                           + contents)

            else:
                res = HTTP_NOT_FOUND + "\r\n"

        elif method.lower() == 'post':
            with open(f'{BASE_DIRECTORY}{file}', 'w') as f:
                f.write(status_lines[4])

                res = HTTP_CREATED + "\r\n"

    # invalid endpoint
    else:
        res = HTTP_NOT_FOUND + "\r\n"

    # Return the response encoded in byte form
    return res.encode()


def handle_client(client_socket, address):
    """
    Helper function for receiving requests and sending responses between the client and server.
    
    :param client_socket: 
    :param address: 
    """
    print(f"Connection established to address {address} from server.")

    req = client_socket.recv(1024).decode()
    res = send_response(req)
    client_socket.send(res)
    client_socket.close()


def main():
    
    # --directory argument to add local directory PATH for serving/storing files while starting server
    parser = argparse.ArgumentParser(description="Simple HTTP Web server")
    parser.add_argument('-d', '--directory', type=str, help='Directory address on server for requesting files')
    args = parser.parse_args()

    global BASE_DIRECTORY
    BASE_DIRECTORY = args.directory

    # reuse_port to be removed for running on Windows
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()
    print("Server is running on port 4221...")

    try:
        while True:
            print("Waiting for connection")
            client_socket, addr = server_socket.accept()

            # Starting new threads to handle multiple concurrent clients if needed
            thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            thread.start()

    except KeyboardInterrupt:
        print("\nServer is shutting down...")
    finally:
        server_socket.close()
        print("Server has been closed.")


if __name__ == "__main__":
    main()
