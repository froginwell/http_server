import socket


SERVER_ADDRESS = ('127.0.0.1', 8000)


def main():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect(SERVER_ADDRESS)

    # _send_hello(tcp_socket)
    _handle_http(tcp_socket)


def _send_hello(tcp_socket):
    tcp_socket.send('hello')
    tcp_socket.close()


def _handle_http(tcp_socket):
    tcp_socket.send('GET / HTTP/1.1\r\n')

    tcp_socket.send('Host: localhost\r\n')
    tcp_socket.send('\r\n')

    raw_data = ''
    while True:
        data = tcp_socket.recv(1024)
        if not data:
            break
        raw_data += data
    print(raw_data)

    tcp_socket.close()


if __name__ == '__main__':
    main()
