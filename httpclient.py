#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

debug = 0

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        if data[9] == '4' and data[10] == '0' and data[11] == '4':
            return 404
        elif data[9] == '2' and data[10] == '0' and data[11] == '0':
            return 200
        elif data[9] == '3' and data[10] == '0' and data[11] == '1':
            return 301
        elif data[9] == '3' and data[10] == '0' and data[11] == '2':
            return 302
        # return None

    def get_headers(self,data):
        if len(data) > 0:
            return data.split("\r\n\r\n",1)[0]
        return data.encode('utf-8')

    def get_body(self, data):
        if len(data) > 0:
            return data.split("\r\n\r\n",1)[1]
        return data.encode('utf-8')
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        parsed_url = urllib.parse.urlparse(url)

        if len(parsed_url.path) > 0:
            request = b"GET " + parsed_url.path.encode('utf-8')
        else:
            request = b"GET /"

        if len(parsed_url.params) > 0: 
            request += b";" + parsed_url.params.encode('utf-8') 
        if len(parsed_url.query) > 0:
            request += b"?" + parsed_url.query.encode('utf-8')
        request += b" HTTP/1.1\r\nHost: " + parsed_url.hostname.encode('utf-8') + b"\r\nConnection: close" + b"\r\n\r\n"

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if parsed_url.port is None:
                hostip = socket.gethostbyname(parsed_url.hostname)
                sock.connect((hostip, 80))
            else:
                sock.connect((parsed_url.hostname, parsed_url.port))
            sock.sendall(request)
            result = self.recvall(sock)
        code = self.get_code(result)
        body = self.get_body(result)

        print(result)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        parsed_url = urllib.parse.urlparse(url)

        if len(parsed_url.path) > 0:
            request = b"POST " + parsed_url.path.encode('utf-8') + b" HTTP/1.1\r\nHost:" + parsed_url.hostname.encode('utf-8') + b"\r\nContent-Type: application/x-www-form-urlencoded\r\n"
        else:
            request = b"POST / HTTP/1.1\r\nHost:" + parsed_url.hostname.encode('utf-8') + b"\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n"

        if args != None:
            request_body = urllib.parse.urlencode(args)
        else:
            request_body = ""

        request += b"Content-Length: " + str(len(str(request_body))).encode('utf-8') + b"\r\n\r\n"
        request += request_body.encode('utf-8')
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if parsed_url.port is None:
                hostip = socket.gethostbyname(parsed_url.hostname)
                # print(hostip)
                sock.connect((hostip, 80))
            else:
                sock.connect((parsed_url.hostname, parsed_url.port))
            sock.sendall(request)
            sock.shutdown(socket.SHUT_WR)
            result = self.recvall(sock)

        print(result)

        code = self.get_code(result)
        body = self.get_body(result)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
