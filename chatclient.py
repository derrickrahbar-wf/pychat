
#############################################################################
# chat client
#############################################################################

import socket
import sys
import select
from communication import send, receive

BUFSIZ = 1024
class ChatClient(object):

    def __init__(self, name, host='192.168.1.14', port=5000):
        self.name = name
        self.flag = False
        self.port = int(port)
        self.host = host
        # Initial prompt
        self.prompt = '[%s]' % self.name
        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, self.port))
            print 'Connected to chat server@%d' % self.port
            # Send my name...
            send(self.sock, self.name)

            #data = receive(self.sock)
            data = self.sock.recv(BUFSIZ)

            # Contains client address, set it
            #addr = data.split('CLIENT: ')[1]
            #self.prompt = '[' + '@'.join((self.name, addr)) + ']> '

            self.prompt = '[%s]>' % self.name

        except socket.error, e:
            print e
            print 'Could not connect to chat server @%d' % self.port
            sys.exit(1)

    def cmdloop(self):

        while not self.flag:
            try:
                sys.stdout.write(self.prompt)
                sys.stdout.flush()

                # Wait for input from stdin & socket
                inputready, outputready,exceptrdy = select.select([0, self.sock], [],[])

                for i in inputready:
                    if i == 0:
                        data = sys.stdin.readline().strip()
                        #if data: send(self.sock, data)
                        if data: self.sock.send(data)
                    elif i == self.sock:
                        #data = receive(self.sock)
                        data = self.sock.recv(BUFSIZ)
                        if not data:
                            print 'Shutting down.'
                            self.flag = True
                            break
                        else:
                            sys.stdout.write(data + '\n')
                            sys.stdout.flush()

            except KeyboardInterrupt:
                print 'Interrupted.'
                self.sock.close()
                break


if __name__ == "__main__":
    client = ChatClient(sys.argv[1],sys.argv[2], int(sys.argv[3]))
    client.cmdloop()