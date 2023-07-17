import socket
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def handle_request(client_socket, request):
    request_lines = request.split("\r\n")
    request_line = request_lines[0]

    method, path, protocol = request_line.split(" ")
    path = urlparse(path)

    if method == "GET":
        if path.path == "/":
            with open(os.path.join(BASE_DIR, "front-init", "index.html"), "r") as file:
                html_content = file.read()
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-type: text/html\r\n"
            response += "Content-Length: {}\r\n\r\n".format(len(html_content))
            response += html_content

        elif path.path == "/message.html":
            with open(os.path.join(BASE_DIR, "front-init", "message.html"), "r") as file:
                response = "HTTP/1.1 200 OK\r\n"
                response += "Content-type: text/html\r\n\r\n"
                response += file.read()

        else:
            with open(os.path.join(BASE_DIR, "front-init", "error.html"), "r") as file:
                response = "HTTP/1.1 404 Not Found\r\n"
                response += "Content-type: text/html\r\n\r\n"
                response += file.read()

    elif method == "POST":
        content_length = 0
        for line in request_lines:
            if line.startswith("Content-Length:"):
                content_length = int(line.split(":")[1].strip())

        post_data = client_socket.recv(content_length).decode("utf-8")
        post_params = parse_qs(post_data)

        if path.path == "/message.html":
            username = post_params["username"][0]
            message = post_params["message"][0]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

            DATA_FILE = os.path.join(BASE_DIR, "front-init", "storage", "data.json")

            message_data = {
                "username": username,
                "message": message,
                "timestamp": timestamp
            }

            try:
                with open(DATA_FILE, "r") as file:
                    messages = json.load(file)
            except FileNotFoundError:
                messages = {}

            messages[timestamp] = message_data

            with open(DATA_FILE, "w") as file:
                json.dump(messages, file, indent=4)

            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-type: text/html\r\n\r\n"
            response += "Message received and saved"

        else:
            with open(os.path.join(BASE_DIR, "front-init", "error.html"), "r") as file:
                response = "HTTP/1.1 404 Not Found\r\n"
                response += "Content-type: text/html\r\n\r\n"
                response += file.read()

    else:
        response = "HTTP/1.1 501 Not Implemented\r\n"
        response += "Content-type: text/html\r\n\r\n"
        response += "<h1>501 Not Implemented</h1>"

    client_socket.sendall(response.encode("utf-8"))
    client_socket.close()


def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("", 3000)
    server_socket.bind(server_address)
    server_socket.listen(1)
    print("Server started on port 3000")

    while True:
        client_socket, client_address = server_socket.accept()
        request = client_socket.recv(4096).decode("utf-8")
        handle_request(client_socket, request)


if __name__ == "__main__":
    run_server()
