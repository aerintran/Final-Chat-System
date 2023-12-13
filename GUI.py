import threading
import select
import tkinter as tk
from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter import messagebox
from chat_utils import *
import json
import pickle
from time import sleep
from PIL import ImageGrab,Image,ImageTk
import emoji
import socket
import requests
import urllib.request
import gzip
from tkinter import filedialog
import os
#from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex 
import socket
import getpass
import hashlib
# from quicktranslate import get_translate_youdao
import random




class GUI:
    def __init__(self, send, recv, sm, s):
        self.Window = tk.Tk()
        self.Window.withdraw()
        self.send = send
        self.recv = recv
        self.sm = sm
        self.socket = s
        self.my_msg = ""
        self.system_msg = ""
        
    def login(self):
        self.flag = False
        self.login_name = ''
        self.login = tk.Toplevel()
        self.login.title("Login")
        self.login.geometry('400x250')

        ttk.Label(self.login, text="Please login to continue", font=("Helvetica", 14)).grid(row=0, columnspan=2, pady=10)

        ttk.Label(self.login, text="Username:", font=("Helvetica", 12)).grid(row=1, column=0, pady=5)
        var_usr_name = tk.StringVar()
        ttk.Entry(self.login, textvariable=var_usr_name, font=("Helvetica", 12)).grid(row=1, column=1, pady=5)

        ttk.Label(self.login, text="Password:", font=("Helvetica", 12)).grid(row=2, column=0, pady=5)
        var_usr_pwd = tk.StringVar()
        ttk.Entry(self.login, textvariable=var_usr_pwd, show='*', font=("Helvetica", 12)).grid(row=2, column=1, pady=5)

        ttk.Button(self.login, text='Login', command=lambda: self.usr_log_in(var_usr_name.get(), var_usr_pwd.get())).grid(row=3, column=0, pady=10)
        ttk.Button(self.login, text='Registration', command=self.usr_sign_up).grid(row=3, column=1, pady=10)
        ttk.Button(self.login, text='Quit', command=self.usr_sign_quit).grid(row=3, column=2, pady=10)

        self.Window.mainloop()

    def usr_log_in(self, var_usr_name, var_usr_pwd):
        usr_name = var_usr_name
        usr_pwd = var_usr_pwd

        try:
            with open('usr_info.pickle', 'rb') as usr_file:
                usrs_info = pickle.load(usr_file)
        except FileNotFoundError:
            with open('usr_info.pickle', 'wb') as usr_file:
                usrs_info = {'admin': 'admin'}
                pickle.dump(usrs_info, usr_file)

        if usr_name == '' or usr_pwd == '':
            messagebox.showerror(message='Username or password is empty.')

        if usr_name in usrs_info:
            if usr_pwd == usrs_info[usr_name]:
                messagebox.showinfo(message=f'Welcome {usr_name}!', title='Login Successful')
                self.flag = True
                self.login_name = usr_name
                self.gopage = tk.Toplevel(self.login)
                self.gopage.title("CHATROOM")
                self.gopage.geometry('400x300')
                ttk.Label(self.gopage, text="Welcome to Our Chatroom!", font=("Helvetica", 14)).pack(pady=20)
                ttk.Button(self.gopage, text="CONTINUE", command=lambda: self.goAhead(self.login_name)).pack()

            else:
                messagebox.showerror(message='Incorrect password.')
        else:
            is_signup = messagebox.askyesno(message='You have not registered yet, would you like to register now?',
                                            title='Registration Confirmation')
            if is_signup:
                self.usr_sign_up()

    def usr_sign_up(self):
        def signtoreg():
            nn = var_new_name.get()
            np = var_new_pwd.get()
            npf = var_new_pwd_confirm.get()

            try:
                with open('usr_info.pickle', 'rb') as usr_file:
                    exist_usr_info = pickle.load(usr_file)
            except FileNotFoundError:
                exist_usr_info = {}

            if nn in exist_usr_info:
                messagebox.showerror('Error!', 'Username already exists.')
            elif np == '' or nn == '':
                messagebox.showerror('Error!', 'Username or password is empty.')
            elif np != npf:
                messagebox.showerror('Error!', 'Inconsistent passwords.')
            else:
                messagebox.showinfo('Registered successfully!', 'Welcome!')
                self.flag = True
                self.login_name = nn
                window_sign_up.destroy()
                exist_usr_info[nn] = np
                with open('usr_info.pickle', 'wb') as usr_file:
                    pickle.dump(exist_usr_info, usr_file)
                self.gopage = tk.Toplevel(self.login)
                self.gopage.title("CHATROOM")
                self.gopage.geometry('400x300')
                ttk.Label(self.gopage, text="Welcome to Our Chatroom!", font=("Helvetica", 14)).pack(pady=20)
                ttk.Button(self.gopage, text="CONTINUE", command=lambda: self.goAhead(self.login_name)).pack()

        window_sign_up = tk.Toplevel(self.login)
        window_sign_up.geometry('350x200')
        window_sign_up.title('Registration')

        var_new_name = tk.StringVar()
        var_new_pwd = tk.StringVar()
        var_new_pwd_confirm = tk.StringVar()

        ttk.Label(window_sign_up, text='Username:').grid(row=0, column=0, pady=5)
        ttk.Entry(window_sign_up, textvariable=var_new_name).grid(row=0, column=1, pady=5)
        ttk.Label(window_sign_up, text='Password:').grid(row=1, column=0, pady=5)
        ttk.Entry(window_sign_up, textvariable=var_new_pwd, show='*').grid(row=1, column=1, pady=5)
        ttk.Label(window_sign_up, text='Confirm Password:').grid(row=2, column=0, pady=5)
        ttk.Entry(window_sign_up, textvariable=var_new_pwd_confirm, show='*').grid(row=2, column=1, pady=5)

        ttk.Button(window_sign_up, text='Complete Registration', command=signtoreg).grid(row=3, column=1, pady=10)

        window_sign_up.mainloop()

    def usr_sign_quit(self):
        self.login.destroy()

    def goAhead(self, name):
        if len(name) > 0:
            msg = json.dumps({"action": "login", "name": name})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.login.destroy()
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(name)
                self.layout(name)
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, menu + "\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)
            process = threading.Thread(target=self.proc)
            process.daemon = True
            process.start()
    # The main layout of the chat
    def layout(self, name):
        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width = False,
                              height = False)
        self.Window.configure(width = 470,
                              height = 550,
                              bg = "#17202A")
        self.labelHead = Label(self.Window,
                             bg = "#17202A", 
                              fg = "#EAECEE",
                              text = self.name ,
                               font = "Helvetica 13 bold",
                               pady = 5)
          
        self.labelHead.place(relwidth = 1)
        self.line = Label(self.Window,
                          width = 450,
                          bg = "#ABB2B9")
          
        self.line.place(relwidth = 1,
                        rely = 0.07,
                        relheight = 0.012)
          
        self.textCons = Text(self.Window,
                             width = 20, 
                             height = 2,
                             bg = "#17202A",
                             fg = "#EAECEE",
                             font = "Helvetica 14", 
                             padx = 5,
                             pady = 5)
          
        self.textCons.place(relheight = 0.745,
                            relwidth = 1, 
                            rely = 0.08)
          
        self.labelBottom = Label(self.Window,
                                 bg = "#ABB2B9",
                                 height = 80)
          
        self.labelBottom.place(relwidth = 1,
                               rely = 0.825)
          
        self.entryMsg = Entry(self.labelBottom,
                              bg = "#2C3E50",
                              fg = "#EAECEE",
                              font = "Helvetica 13")
          
        # place the given widget
        # into the gui window
        self.entryMsg.place(relwidth = 0.74,
                            relheight = 0.06,
                            rely = 0.008,
                            relx = 0.011)
          
        self.entryMsg.focus()
          
        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text = "Send",
                                font = "Helvetica 10 bold", 
                                width = 20,
                                bg = "#ABB2B9",
                                command = lambda : self.sendButton(self.entryMsg.get()))
          
        self.buttonMsg.place(relx = 0.77,
                             rely = 0.008,
                             relheight = 0.06, 
                             relwidth = 0.22)
          
        self.textCons.config(cursor = "arrow")
          

        #============================ emoji ===========================================
        self.buttonEmoji = Button(self.labelBottom,
                                text="\U0001f612",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.sendButton("emoji"))

        self.buttonEmoji.place(relx=0.6,
                             rely=0.008,
                             relheight=0.06,
                             relwidth=0.22)
        #==============================================================================
        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)
          
        # place the scroll bar 
        # into the gui window
        scrollbar.place(relheight = 1,
                        relx = 0.974)
          
        scrollbar.config(command = self.textCons.yview)
          
        self.textCons.config(state = DISABLED)

        
        

        # function to basically start the thread for sending messages
    def sendButton(self, msg):
        self.textCons.config(state=DISABLED)
        self.my_msg = msg
        self.entryMsg.delete(0, END)

    def proc(self):
        while True:
            read, write, error = select.select([self.socket], [], [], 0)
            peer_msg = []
            if self.socket in read:
                peer_msg = self.recv()
            if len(self.my_msg) > 0 or len(peer_msg) > 0:
                self.system_msg += self.sm.proc(self.my_msg, peer_msg)
                self.my_msg = ""
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, self.system_msg +"\n\n")      
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)

    def run(self):
        self.login()

# create a GUI class object
if __name__ == "__main__":
    g = GUI()