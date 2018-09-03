# -*- coding: utf-8 -*-
from __future__ import print_function

import socket


SERVER_ADDRESS = ('127.0.0.1', 8000)


def main():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(SERVER_ADDRESS)
    tcp_socket.listen(5)

    while True:
        request_socket, client_address = tcp_socket.accept()
        print('CLIENT_ADDRESS:', client_address)
        # handle_tcp(request_socket)
        handle_http(request_socket)


def handle_tcp(request_socket):
    while True:
        data = request_socket.recv(1024)
        if not data:
            break
        print('RECV:', data)


def handle_http(request_socket):
    http_info = parse_http(request_socket)

    first_line = None
    headers = {}
    body = None

    http_path = http_info['http_path']
    if http_path == '/':
        first_line = 'HTTP/1.1 200 OK'
        body = '<html><head><meta charset="UTF-8"></head><body><h1>你好</h1></body></html>'  # noqa E501
        headers['Content-Length'] = len(body)
    elif http_path in ('/post', '/post/'):
        if http_info['http_method'] != 'POST':
            first_line = 'HTTP/1.1 405 Method Not Allowed'
        else:
            first_line = 'HTTP/1.1 200 OK'
            body = '<html><body><h1>post</h1></body></html>'
            headers['Content-Length'] = len(body)
    else:
        first_line = 'HTTP/1.1 404 Not Found'

    request_socket.send(first_line)
    request_socket.send('\r\n')
    if headers:
        for k, v in headers.iteritems():
            request_socket.send('%s: %s' % (k, v))
            request_socket.send('\r\n')
    request_socket.send('\r\n')
    if body:
        request_socket.send(body)
    request_socket.close()


def parse_http(request_socket):
    raw_data = ''
    http_method = http_path = http_version = None
    http_headers = {}
    http_body = ''
    while True:
        data = request_socket.recv(1024)
        if not data:
            print('Connection closed by client.')
            break

        raw_data += data

        if not http_method:
            http_method, http_path, http_version = _parse_request_line(
                raw_data)

        if not http_headers:
            http_headers = _parse_header(raw_data)

        if http_headers:
            content_length = http_headers.get('Content-Length')
            if content_length:
                content_length = int(content_length)
                body_start_position = raw_data.find('\r\n\r\n') + 4
                body_has_been_read_length = len(raw_data[body_start_position:])
                while True:
                    if body_has_been_read_length >= content_length:
                        break

                    data = request_socket.recv(1024)
                    if not data:
                        print('Connection closed by client.')
                        break

                    raw_data += data
                    body_has_been_read_length += len(data)

                body_end_position = body_start_position + content_length
                http_body = raw_data[body_start_position:body_end_position]
            break
    print('http_mothod:', http_method)
    print('http_path:', http_path)
    print('http_version:', http_version)
    print('http_headers:', http_headers)
    print('http_body:', http_body)
    return dict(
        http_method=http_method,
        http_path=http_path,
        http_version=http_version,
        http_headers=http_headers,
        http_body=http_body
    )


def _parse_request_line(raw_data):
    index = raw_data.find('\r\n')
    http_method = http_path = http_version = None
    if index > -1:
        request_line = raw_data[:index]
        words = request_line.split()
        if len(words) == 3:  # GET / HTTP/1.1
            http_method, http_path, http_version = words
        elif len(words) == 2:  # GET /
            http_method, http_path = words
        else:
            raise ValueError('The format of request line is invalid.')
    return (http_method, http_path, http_version)


def _parse_header(raw_data):
    end_index = raw_data.find('\r\n\r\n')
    headers = {}
    if end_index > -1:
        start_index = raw_data.find('\r\n') + 2
        for line in raw_data[start_index:end_index].split('\r\n'):
            k, v = line.split(':', 1)
            headers[k.strip()] = v.strip()
    return headers


if __name__ == '__main__':
    main()
