"""
Basic chat server which allows 5 clients to connect simultaneously
"""

import select
import socket
import sys
import signal

from communication import send, receive

BUFSIZ = 1024

class ChatServer(object):

    def __init__(self, port=5000, max_clients=5):
        self.clients = 0
        # Client map
        self.clientmap = {}
        # Output socket list
        self.outputs = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server.bind(('192.168.1.14',port))
        print 'Host at :', socket.gethostname()
        print 'Listening to port',port,'...'
        self.server.listen(max_clients)
        # handle keystrokes with asynch interrupts
        signal.signal(signal.SIGINT, self.signal_handler)

    # Interrupt service routine which closes server
    def signal_handler(self, signum, frame):
        print 'Shutting down server...'
        for sock in self.outputs:
             sock.close()
        self.server.close()

    # Returns the name of the given client
    def get_name(self, client):
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return '@'.join((name, host))
    
    def set_name(self, client, name):
        address, oldName = self.clientmap[client]
        self.clientmap[client] = (address, name)

    def run_server(self):
        inputs = [self.server,sys.stdin]
        self.outputs = []

        running = 1

        while running:
            try:
                read_Ready,write_Ready,exception_Ready = select.select(inputs, self.outputs, [])
            except select.error, e:
                print "\nWhoops ~ Select.error\n"
                break
            except socket.error, e:
                print "\nWhoops ~ Socket.error\n"
                break

            for s in read_Ready:
                if s == self.server:
                    # handle the server socket
                    client, address = self.server.accept()
                    print 'A connection came in from address: %s' % (address[0])

                    cname = client.recv(BUFSIZ)
                    self.clients += 1
                    inputs.append(client)
                    client.send('1')

                    # Sometimes during a remote socket connection, the client will initally send an empty packet
                    # followed by a packed filled with the contents of whats usually sent in the initial request
                    # (i.e. the name of the client)
                    if len(cname) == 0: cname = '.'
                    self.clientmap[client] = (address, cname)
                    msg = '\n%s has joined the chatroom' % (cname)
                    for o in self.outputs:
                        o.send(msg)
                    self.outputs.append(client)

                elif s == sys.stdin:
                    # handle standard input
                    junk = sys.stdin.readline()
                    running = 0
                # This means a client is ready to be read from meaning that client has sent a message
                else:
                    # handle all other sockets
                    try:
                        data = s.recv(BUFSIZ)
                        #data = receive(s)
                        if data:
                            print self.get_name(s)
                            if self.get_name(s)[0] == '.':
                                print data
                                name = data.split(': ')[1].replace('\'','').split('\n')[0]
                                name = "test name"
                                self.set_name(s, name)

                            msg = '\n[' + self.get_name(s) + ']> ' + data

                            # Send data to everyone in chat room
                            for client in self.outputs:
                                if client != s:
                                    client.send(msg)
                        else:
                            print 'chatserver: %d hung up' % s.fileno()
                            self.clients -= 1
                            s.close()
                            inputs.remove(s)
                            self.outputs.remove(s)

                            # Notify others in the chat room about client that is leaving
                            msg = '\n(%s Left the chat room.)' % self.get_name(s)
                            for o in self.outputs:
                                o.send(msg)
                    except socket.error, e:
                        # Remove
                        inputs.remove(s)
                        self.outputs.remove(s)



        self.server.close()

if __name__ == "__main__":
    ChatServer().run_server()
