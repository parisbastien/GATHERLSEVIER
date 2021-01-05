import requests, time, random, html, os
from threading import Thread, RLock
from bs4 import BeautifulSoup
from colorama import init, deinit
from termcolor import colored
from gatherlsevier_functions import *

init()
client = "SCI-HUB"
backup = "LIBGEN"

print("This script allows you to instant-download (no captcha or web surfing) the articles you want from "+colored("l","cyan")+\
colored("i","green")+colored("b","yellow")+colored("g","cyan")+colored("e","green")+colored("n","yellow")+\
colored(".","cyan")+colored("l","green")+colored("c","yellow")+" and "+colored("s","green")+\
colored("c","yellow")+colored("i","cyan")+colored("-","green")+colored("h","yellow")+colored("u","cyan")+\
colored("b","green")+colored(".","yellow")+colored("t","cyan")+colored("w\n","green"))

print("It bypasses any "+colored("l","yellow")+colored("i","cyan")+colored("b","green")+\
colored("g","yellow")+colored("e","cyan")+colored("n","green")+colored(".","yellow")+colored("l","cyan")+\
colored("c","green")+" restriction from internet providers (at least in France)\n")

print("Bulk instant-download of articles is possible : Instead of a DOI, input the full name of a .txt file (e.g., references.txt) \
that contains a different DOI on each line\n")

print("PDF files are saved in the \"saved references\" folder\n\n")

print(colored("You are currently targetting {} as main, and {} as backup.".format(client, backup),"green"))
print("Run gatherlsevier_settings.py to change your preferences\n")

single = True
n_articles, n_thread = 0, 0
content, length, doi = "", "", ""
item_lock, save_lock, print_lock = RLock(), RLock(), RLock()

class libgen_scrapper(Thread):

    def __init__(self):
        Thread.__init__(self)
    
    def run(self):

        global single
        global doi
        global n_articles
        global content
        global length
        found = True

        with item_lock:
            url, success, doi_x = retrieve_url(single, doi, content, print_lock)
        if success is True:
            pdf_address, filename, success, found = retrieve_article(url, print_lock, client)
            if success is True:
                filecontent, success = download_article(pdf_address, print_lock)
                if success is True:
                    with save_lock:
                        filename, n_articles, success = save_article(filename, filecontent, single, length, n_articles, url, print_lock)
                    if success is True:
                        if single is True:
                            os.startfile("{}\\saved references\\{}.pdf".format(os.path.abspath(os.getcwd()), filename))
                    else:
                        error_logs(doi_x, found, print_lock)
                else:
                    error_logs(doi_x, found, print_lock)
            else:
                error_logs(doi_x, found, print_lock)

while 1:
    if single is True:
        doi = input("DOI / File name (case sensitive if file name) ? ")

        if ".txt" in doi:
            single = False
            n_articles = 0
            with open(doi,"r") as opening:
                content = opening.read().split("\n")

            length = str(len(content))
            print(colored("\n{} references in line\n".format(length),"green"))
    
    else:
        if len(content) == 0:
            single = True
            continue
    
    if single is True:
        item = libgen_scrapper()
        item.start()
        item.join()
    else:
        thread_list = []
        for i in range(0,10):
            thread_list.append(libgen_scrapper())
        for item in thread_list:
            item.start()
        for item in thread_list:
            item.join()

    print("\n")