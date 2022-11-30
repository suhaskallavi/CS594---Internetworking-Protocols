"""
    CS594-003 - Internet Protocols
    Suhas Dwarakanath (PSU ID: 974533141), Shishir Gururaj (PSU ID: 954839640)
    Internet Relay Chat Application
"""

"Server"


import select

import chat_mid
from chat_mid import MainWindow, ChatUser

Buffer_Limit_Read = 1024

listenSocket = chat_mid.sock_crt(('127.0.0.1', 5005))
# Socket object return

serverSocket = listenSocket
admin_list = MainWindow()
conn_list = [listenSocket]
# All the sockets, server sockets, appending to the client socket

while True:
    user_read, write_players, error_sockets = select.select(conn_list, [], [])

    for user in user_read:
        # if there are multiple items, add 10+ clients, listen sockets
        if user is listenSocket:
            """
                when you receive a message in connection_list, it will not be there in listenSocket,
                hence it goes to else and adds message from the client socket
            """

            sock_new, add = user.accept()
            # accept client's who is trying to connect, store socket connection of the new client, add client's PORT

            mem_new = ChatUser(sock_new)
            # create ChatUser object and initialize all the values, set socket as new socket

            conn_list.append(mem_new)
            # append chat user object to the  connection_list

            admin_list.client_join(mem_new)
            # call the function client_join in the class MainWindow()

        else:
            # This is for new message
            msg = user.socket.recv(Buffer_Limit_Read)

            # particular clients socket message
            if not msg:
                admin_list.rmv_mem(user)

            if msg:
                msg = msg.decode().lower()
                admin_list.cmd_ctrl(user, msg)

            else:
                user.socket.close()
                conn_list.remove(user)

    for sock in error_sockets:
        # close all the error sockets
        sock.close()
        conn_list.remove(sock)
