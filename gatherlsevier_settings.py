import requests, time, random, html, os
from threading import Thread, RLock
from bs4 import BeautifulSoup
from colorama import init, deinit
from termcolor import colored

init()

while 1:
    client_choice = input("Please select the website you want to target as main to retrieve your article (SCI-HUB is usually faster). Enter one of the following value in order to do so:\n\nSCI-HUB\nLIGBEN\n\nThe other website will be targeted as a backup.\n\n")
    if client_choice.lower() == "sci-hub":
        client_choice = "SCI-HUB"
        backup_choice = "LIBGEN"
        break
    elif client_choice.lower() == "libgen":
        client_choice = "LIBGEN"
        backup_choice = "SCI-HUB"
        break
    else:
        print(colored("Please enter either \"SCI-HUB\" or \"LIBGEN\"\n\n","red"))

with open("gatherlsevier_run.py","r") as opening:
    content = opening.read().split("\n")

content[8] = "client = \"{}\"".format(client_choice)
content[9] = "backup = \"{}\"".format(backup_choice)

with open("gatherlsevier_run.py","w") as opening:
    opening.write("\n".join(content))

print(colored("Settings applied with success!","green"))
os.system("pause")