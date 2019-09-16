import configparser
import os
import re
import shutil

# WordOps git configuration management
config = configparser.ConfigParser()
config.read(os.path.expanduser("~")+'/.gitconfig')
try:
    wo_user = config['user']['name']
    wo_email = config['user']['email']
except Exception:
    print("WordOps (wo) require an username & and an email "
          "address to configure Git (used to save server configurations)")
    print("Your informations will ONLY be stored locally")

    wo_user = input("Enter your name: ")
    while wo_user == "":
        print("Unfortunately, this can't be left blank")
        wo_user = input("Enter your name: ")

    wo_email = input("Enter your email: ")

    while not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$",
                       wo_email):
        print("Whoops, seems like you made a typo - "
              "the e-mailaddress is invalid...")
        wo_email = input("Enter your email: ")

    os.system("git config --global user.name {0}".format(wo_user))
    os.system("git config --global user.email {0}".format(wo_email))

if not os.path.isfile('/root/.gitconfig'):
    shutil.copy2(os.path.expanduser("~")+'/.gitconfig', '/root/.gitconfig')
