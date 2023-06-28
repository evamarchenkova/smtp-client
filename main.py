import base64
import ssl

from constants import HOST, PORT, CRLF, CHUNK_SIZE
from pathes import TEXT, CONFIG, PASSWORD
import socket

from message import Message


def get_ssl_context():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return ssl_context


def request(socket, request):
    socket.send((request + CRLF).encode())
    recv_data = ''
    while True:
        chunk = socket.recv(CHUNK_SIZE)
        if not chunk or not socket.pending():
            recv_data += chunk.decode()
            break
        recv_data += chunk.decode()
    return recv_data


def get_password():
    with open(PASSWORD, 'r') as file:
        return base64.b64encode(file.read().encode()).decode()


def get_login(from_field):
    return base64.b64encode(from_field.encode()).decode()


def authenticate(client, from_field):
    request(client, 'AUTH LOGIN')
    request(client, get_login(from_field))
    request(client, get_password())


def main():
    with socket.create_connection((HOST, PORT)) as sock:
        with get_ssl_context().wrap_socket(sock, server_hostname=HOST) as client:
            message = Message(TEXT, CONFIG)
            client.recv(1024)
            request(client, f'EHLO {message.from_field}')
            authenticate(client, message.from_field)
            request(client, f'MAIL FROM:{message.from_field}')
            for recipient in message.to_field:
                request(client, f'RCPT TO:{recipient}')
            request(client, 'DATA')
            request(client, message.create_message())


if __name__ == '__main__':
    main()
