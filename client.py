"""
    CS594-003 - Internet Protocols
    Suhas Dwarakanath (PSU ID: 974533141), Shishir Gururaj (PSU ID: 954839640)
    Internet Relay Chat Application
"""

"Client"


import sys
import socket
import select
import chat_mid

"""

1) The select() module provides access to platform-specific I/O monitoring functions. Python’s select() function is a 
direct interface to the underlying operating system implementation. It monitors sockets, open files, and pipes until 
they become readable or writable, or a communication error occurs. select() makes it easier to monitor multiple 
connections at the same time, and is more efficient than writing a polling loop in Python using socket timeouts, 
because the monitoring happens in the operating system network layer, instead of the interpreter.

2) Socket programming is started by importing the socket library and making a simple socket. 

3) The python sys module provides functions and variables which are used to manipulate different parts of the Python 
Runtime Environment. It lets us access system-specific parameters and functions. 

"""


Buffer_Limit_Read = 1000

# Socket creation
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
conn.connect(('127.0.0.1', 5005))  # Server connection

print("\nConnected to the chat server successfully\n")

msg_prefix = ''  #change

sockets = [sys.stdin, conn]


class ErrorBase(Exception):  #Exception Base Class
    pass


class ErrorServerDown(ErrorBase):  #Server Down Error
    pass


def prompt():
    sys.stdout.write('\nYou: ')
    sys.stdout.flush()


try:
    while True:
        sock_read, sock_write, sock_error = select.select(sockets, [], [])

        for x in sock_read:

            if x is conn:  # Getting the messages
                msg = x.recv(Buffer_Limit_Read)
                if not msg:
                    #print("\n\nSorry for the inconvenience, the server is down!")
                    #sys.exit(2)
                    raise ErrorServerDown
                else:
                    if msg == chat_mid.Expr_Exit.encode():
                        # Incoming message from server
                        sys.stdout.write('\nExiting the server\n\n')     #Server exit
                        sys.exit(2)
                    else:
                        sys.stdout.write(msg.decode())
                        if 'Enter your name' in msg.decode():
                            msg_prefix = 'name: '    #Name Identifier
                        else:
                            msg_prefix = ''
                        prompt()

            else:
                msg = msg_prefix + sys.stdin.readline()
                conn.sendall(msg.encode())

except ErrorServerDown:
    print("\n\nSorry for the inconvenience, the server is down!")
    sys.exit(2)

finally:
    sys.exit(2)
