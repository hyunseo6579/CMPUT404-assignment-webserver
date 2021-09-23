#  coding: utf-8 
import socketserver, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    # sends data back to client
    def send(self, msg):
        self.request.sendall(bytearray(msg,'utf-8'))

    # send requested file from file_path
    def serve_file(self, file_path):
        file = open("www"+file_path, "r")
        content = file.read()
        self.send(content)
    
    def handle(self):
        self.data = self.request.recv(1024).strip()

        # decode, grab first line, then split by spaces in each line
        request_list = self.data.decode().split('\n')[0].split(' ')
        # obtain the method
        method = request_list[0]
        # obtain the requested path
        file_path = request_list[1]
        path_fixed = False

        # check if given path is a directory that exists but doesn't end in '/' (301 error)
        new_path = ''
        if os.path.isdir('www'+file_path) and file_path[-1] != '/':
            # fix the link and mark that path is fixed
            file_path += '/'
            # keep new_path to use for simple fixed url;
            # file_path will be altered in the next few checks
            new_path = file_path
            path_fixed = True

        # if file path ends in '/', call index.html
        if file_path[-1] == '/':
            file_path += 'index.html'

        content_type = ''
        if file_path.split('.')[-1] == 'html':
            content_type = 'text/html'
        elif file_path.split('.')[-1] == 'css':
            content_type = 'text/css'
        else:
            file_path = 'Unsupported'

        # if file doesn't exist
        if not os.path.isfile("www"+file_path):
            file_path = 'DNE'

        # now, if method and path is valid, send the appropriate page
        if method == 'GET' and file_path != 'DNE' and file_path != 'Unsupported':
            if path_fixed == True:
                self.send("HTTP/1.1 301 Moved Permanently\r\n")
                self.send("Location: http://127.0.0.1:8080"+new_path+"\r\n")
            else:
                # reference: https://stackoverflow.com/questions/21153262/sending-html-through-python-socket-server/21153368#21153368
                self.send("HTTP/1.1 200 OK\r\n")
                self.send("Content-Type: "+content_type+"\r\n")
                self.send("\r\n")

                self.serve_file(file_path)

        elif file_path == 'Unsupported':
            self.send("HTTP/1.1 415 Unsupported Media Type\r\n")

        elif file_path == 'DNE':
            self.send("HTTP/1.1 404 Page Not Found\r\n")

        # method is not 'GET'
        else:
            self.send("HTTP/1.1 405 Method Not Allowed\r\n")


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
