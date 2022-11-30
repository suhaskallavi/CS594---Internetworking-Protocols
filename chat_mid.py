"""
    CS594-003 - Internet Protocols
    Suhas Dwarakanath (PSU ID: 974533141), Shishir Gururaj (PSU ID: 954839640)
    Internet Relay Chat Application
"""

"Interface b/w server and client"

import socket
import re

Expr_Exit = '$exit$'
Client_Limit = 32


def sock_crt(addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(False)
    s.bind(addr)
    s.listen(Client_Limit)
    print("\nThe server is listening at", addr)
    print("\n")
    return s


"""
    Here we have defined the class which handles user names and class names
    It also contains various user defined functions to handle the IRC application
"""

class ErrorBase(Exception):  #Exception Base Class
    pass

class WrongRoomLeaveError(ErrorBase):  #When a user tries to leave a room they are not part of
    pass

class InvalidSwitchError(ErrorBase):  #When a user tries to switch to a room they have not joined
    pass

class InvalidCommandError(ErrorBase):  #Invalid Command
    pass

class InvalidUserError(ErrorBase):  #Invalid User
    pass

class NotPresentInRoomError(ErrorBase):  #When a user tries to send message without joining any room or dm
    pass

class MainWindow:
    def __init__(self):
        self.rooms = {}  # {room_name: Room}
        self.link_user_room = {}  # {username-room_name: room_name}
        self.link_user = {}  # {username : user}


    @staticmethod
    def client_join(user_new):     #Display message when a client connects to server
        user_new.socket.sendall(b'\nWelcome to the Internet Relay Chat Application!\n\nEnter your name:\n')

    def cmd_ctrl(self, user, msg):  #Handling different messages

        # This works like a user manual
        commands = b'\n\nUser Command Guide:\n' \
                       + b'$rooms             : Gives a list of rooms you can join\n' \
                       + b'$join <room_name>  : To join an existing room or start one\n' \
                       + b'$dm <user_name>    : To have a private conversation with another user\n' \
                       + b'$guide             : Displays user guide\n' \
                       + b'$switch <room_name>: To switch between rooms\n' \
                       + b'$leave <room_name> : To leave a room\n' \
                       + b'$exit              : To exit the application\n' \
                       + b'If you have already joined a room, you can go ahead with your messages' \
                       + b'\n'
        
        if user.name != "new":
            print(user.name + " says: " + msg)
        
        if "name:" in msg:
            name = msg.split()[1]
            user.name = name
            print("We have a new connection from", user.name)
            print("\n")
            self.link_user[user.name] = user
            user.socket.sendall(commands)

        elif "$join" in msg:
            same_room = False
            try:
                if len(msg.split()) == 2:  # Command validation
                    room_name = msg.split()[1]
                    user.current_room = room_name
                    if user.name + "-" + room_name in self.link_user_room:  # Switch Validation
                        if self.link_user_room[user.name + "-" + room_name] == room_name:
                            user.socket.sendall(b'You are already a part of room ' + room_name.encode() + b'\n\n')
                            same_room = True
                        else:  # switch
                            room_old = self.link_user_room[user.name + "-" + room_name]
                        # self.rooms[room_old].rmv_mem(user)
                    if not same_room:
                        if not room_name in self.rooms:  # Room creation
                            room_new = Room(room_name)
                            self.rooms[room_name] = room_new
                        self.rooms[room_name].users.append(user)
                        self.rooms[room_name].client_join(user)
                        self.link_user_room[user.name + "-" + room_name] = room_name
                else:
                    raise InvalidCommandError
            except:
                print('Exception Handling Invalid Command\n')
                msg = 'Please check the entered command and try again, you can use the below guide as reference to verify the syntax'
                user.socket.sendall(msg.encode())
                user.socket.sendall(commands)

        elif "$rooms" in msg:
            msg2 = '$rooms'
            try:
                #if len(msg.split()) == 1:  # Command Validation
                msg2 = re.search("^\$rooms$", msg)    # Command Validation
                if msg2.string:
                    #print(self.rooms)
                    #print(self.link_user_room)
                    self.room_list(user)
                else:
                    raise InvalidCommandError
            except:
                print('Exception Handling Invalid Command\n')
                msg = 'Please check the entered command and try again, you can use the below guide as reference to verify the syntax'
                user.socket.sendall(msg.encode())
                user.socket.sendall(commands)

        elif "$guide" in msg:
            msg2 = '$guide'
            try:
                msg2 = re.search("^\$guide$", msg)    # Command Validation
                if msg2.string:
                    user.socket.sendall(commands)
                else:
                    raise InvalidCommandError
            except:
                print('Exception Handling Invalid Command\n')
                msg = 'Please check the entered command and try again, you can use the below guide as reference to verify the syntax'
                user.socket.sendall(msg.encode())
                user.socket.sendall(commands)

        elif "$leave" in msg:
            try:
                if len(msg.split()) == 2:  # Command Validation
                    leaving_room = msg.split()[1]

                    try:
                        if user.name + "-" + leaving_room in self.link_user_room:
                            del self.link_user_room[user.name + "-" + user.current_room]
                            self.rooms[leaving_room].rmv_mem(user)
                            print(user.name + " left room " + leaving_room + "\n")   # Server Display
                            if len(self.rooms[leaving_room].users) == 0:
                                del self.rooms[leaving_room]
                        else:
                            raise WrongRoomLeaveError
                    except WrongRoomLeaveError:
                        print("Exception Handling Wrong Room Leave\n")
                        msg = "You do not seem to be part of a room by the mentioned name. Please check and try again.\n"
                        user.socket.sendall(msg.encode())
                else:
                    raise InvalidCommandError
            except:
                print('Exception Handling Invalid Command\n')
                msg = 'Please check the entered command and try again, you can use the below guide as reference to verify the syntax'
                user.socket.sendall(msg.encode())
                user.socket.sendall(commands)

        elif "$exit" in msg:
            msg2 = '$exit'
            try:
                #if len(msg.split()) == 1:  # Command Validation
                msg2 = re.search("^\$exit$", msg)    # Command Validation
                if msg2.string:
                    user.socket.sendall(Expr_Exit.encode())
                    self.rmv_mem(user)
                else:
                    raise InvalidCommandError
            except:
                print('Exception Handling Invalid Command\n')
                msg = 'Please check the entered command and try again, you can use the below guide as reference to verify the syntax'
                user.socket.sendall(msg.encode())
                user.socket.sendall(commands)

        elif "$switch" in msg:
            try:
                if len(msg.split()) == 2:  #Command Validation
                    room_switch = msg.split()[1]
                    #   isRoom = self.link_user_room[user.name+"-"+room_switch]
                    #   if isRoom == room_switch :

                    try:
                        if user.name + "-" + room_switch in self.link_user_room:   #User-Room Link Validation
                            user.current_room = room_switch
                        else:
                            raise InvalidSwitchError
                    except:
                        print("Exception Handling Invalid Switch\n")
                        msg = "\nWe do not have a record of you being in the mentioned room. You can join the room using \'$join <room_name>\'\n\n"
                        user.socket.sendall(msg.encode())
                else:
                    raise InvalidCommandError
            except:
                print('Exception Handling Invalid Command\n')
                msg = 'Please check the entered command and try again, you can use the below guide as reference to verify the syntax'
                user.socket.sendall(msg.encode())
                user.socket.sendall(commands)

        elif "$dm" in msg:
            try:
                if len(msg.split()) == 2:      #Command Validation
                    username = msg.split()[1]
                    try:
                        if username in self.link_user:
                            userNew = self.link_user[username]
                            dm_room = Room("dm-" + user.name + "-" + username)
                            self.rooms["dm-" + user.name + "-" + username] = dm_room
                            self.rooms["dm-" + user.name + "-" + username].users.append(user)
                            self.rooms["dm-" + user.name + "-" + username].users.append(userNew)
                            self.link_user_room[user.name + "-" + "dm-" + user.name + "-" + username] = "dm-" + user.name + "-" + username
                            # self.rooms[room_name].client_join(user)
                            self.link_user_room[username + "-" + "dm-" + user.name + "-" + username] = "dm-" + user.name + "-" + username
                            user.current_room = "dm-" + user.name + "-" + username
                            userNew.current_room = "dm-" + user.name + "-" + username
                        else:
                            raise InvalidUserError
                    except InvalidUserError:
                        msg = "There is no user by the name mentioned. Please check and try again\n"
                        user.socket.sendall(msg.encode())
                else:
                    raise InvalidCommandError
            except:
                print('Exception Handling Invalid Command\n')
                msg = 'Please check the entered command and try again, you can use the below guide as reference to verify the syntax'
                user.socket.sendall(msg.encode())
                user.socket.sendall(commands)

        elif not msg:
            self.rmv_mem(user)

        else:
            try:
                if user.name + "-" + user.current_room in self.link_user_room:         # Checking whether the user is present in a room
                    self.rooms[self.link_user_room[user.name + "-" + user.current_room]].broadcast(user, msg.encode())
                else:
                    raise NotPresentInRoomError
            except NotPresentInRoomError:
                msg = '\nIt looks like you are not present in any room to send messages \n' \
                      + 'You can use \'$rooms\' to get a list of rooms you can join \n' \
                      + 'You can use \'$join <room_name>\' to join an existing room or start one of your own \n' \
                      + 'You can use \'$dm <user_name>\' to chat with an existing user \n\n'
                user.socket.sendall(msg.encode())

    # List of rooms
    def room_list(self, user):

        if len(self.rooms) == 0:
            msg = 'There does not seem to be any available room right now. You can start a new one using \'$join <room_name>\'\n\n'
            user.socket.sendall(msg.encode())
        else:
            msg = '\nHere is a list of rooms you can join: \n'
            for room in self.rooms:
                if '$dm' not in room:
                    #print(self.rooms[room].users)
                    msg += room + ": " + str(len(self.rooms[room].users)) + " user(s)\n"
                    for member1 in self.rooms[room].users:
                        msg += member1.name + "\n"
            user.socket.sendall(msg.encode())

    def rmv_mem(self, user):
        if user.name + "-" + user.current_room in self.link_user_room:
            print(user.name + " left room " + user.current_room + "\n")
            self.rooms[self.link_user_room[user.name + "-" + user.current_room]].rmv_mem(user)
            del self.link_user_room[user.name + "-" + user.current_room]


class Room:
    def __init__(self, name):
        self.users = []  #socket list
        self.name = name

    def client_join(self, user_from):
        msg = '\n\n' + "Welcoming " + user_from.name + " to room " + self.name + '!\n'
        for user in self.users:
            user.socket.sendall(msg.encode())

    def broadcast(self, user_from, msg):
        msg = b"\n\n*****" + user_from.current_room.encode() + b"*****\n" + user_from.name.encode() + b": " + msg
        for user in self.users:
            if user.name != user_from.name:
                user.socket.sendall(msg)

    def leave_broadcast(self, user_from, msg):
        msg = b"\n\n" + msg
        for user in self.users:
            if user.name != user_from.name:
                user.socket.sendall(msg)

    def rmv_mem(self, user):
        self.users.remove(user)
        leave_msg = user.name.encode() + b" left room " + self.name.encode() + b"\n"        # Room Display
        self.leave_broadcast(user, leave_msg)


class ChatUser:
    def __init__(self, socket, name="new", current_room="new"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name
        self.current_room = current_room

    def fileno(self):
        return self.socket.fileno()
