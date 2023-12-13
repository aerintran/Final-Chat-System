"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json
from cryptography.fernet import Fernet # Requires cryptography to be installed


class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def encrypt(self, my_msg):
        with open('key.key', 'rb') as f:
            key = f.read() # Get personal key
            fern = Fernet(key) # Initialize 
            encrypted_text = fern.encrypt(my_msg.encode()).decode() # Encrypt msg as byets and decode enrypted bytes

        return encrypted_text

    def decrypt(self, encrypted_text):
        with open('key.key', 'rb') as f:
            key = f.read() # Get personal key
            fern = Fernet(key) # Initialize
            decrypted_text = fern.decrypt(encrypted_text.encode()).decode() # Decrypt args
        
        return decrypted_text

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + ' and your messages are encrypted. Chat away (securely)!\n\n'
                        self.out_msg += '-----------------------------------\n'
                        with open('key.key', 'wb') as f:
                            _key = Fernet.generate_key()
                            f.write(_key)
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    # print(poem)
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

# ================================== emoji ====================================
                elif my_msg=='(eh)':
                        self.out_msg += "\U0001f600"
                        mysend(self.s, json.dumps({"action":"emoji", "target":"\U0001f600"}))
                elif my_msg=='(es)':
                        self.out_msg += "\U0001f612"
                        mysend(self.s, json.dumps({"action":"emoji", "target":"\U0001f612"}))
                elif my_msg=='(eu)':
                        self.out_msg += "\U0001f610"
                        mysend(self.s, json.dumps({"action":"emoji", "target":"\U0001f610"}))
                elif my_msg == 'emoji':
                    self.out_msg += "\U0001f612"
                    mysend(self.s, json.dumps({"action":"emoji", "target":"\U0001f612"}))
#==============================================================================



                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
            
#================================ emoji =======================================
               if "(eh)" not in my_msg and "(eu)" not in my_msg and "(es)" not in my_msg and "emoji" not in my_msg:
                    mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
               if "(eh)" or "(eu)" or "(es)" in my_msg:
                    if"(eh)" in my_msg:
                        emoji = my_msg.replace("(eh)","\U0001f600")
                        self.out_msg = my_msg.replace("(eh)","\U0001f600")
                        mysend(self.s, json.dumps({"action":"emoji_exchange", "from":"[" + self.me + "]", "message":emoji}))
                    if"(es)" in my_msg:
                        emoji = my_msg.replace("(es)","\U0001f612")
                        self.out_msg = my_msg.replace("(es)","\U0001f612")
                        mysend(self.s, json.dumps({"action":"emoji_exchange", "from":"[" + self.me + "]", "message":emoji}))
                    if"(eu)" in my_msg:
                        emoji = my_msg.replace("(eu)","\U0001f610")
                        self.out_msg = my_msg.replace("(eu)","\U0001f610")
                        mysend(self.s, json.dumps({"action":"emoji_exchange", "from":"[" + self.me + "]", "message":emoji}))
               if my_msg == 'emoji':
                    self.out_msg += "\U0001f612"
                    mysend(self.s, json.dumps({"action":"emoji_exchange", "from":"[" + self.me + "]", "message":"\U0001f612"}))
#============================================================================== 

           
               if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                else:
                    self.out_msg += peer_msg["from"] + peer_msg["message"]


            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
