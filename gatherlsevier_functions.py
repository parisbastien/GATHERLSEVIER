import requests
from threading import Thread, RLock
from bs4 import BeautifulSoup
from colorama import init, deinit
from termcolor import colored


def retrieve_url(single, doi, content):

    url = ""

    try:
        success = True
        if single is False:
            doi = content.pop(0)

        delete = 0
        for char in doi:
            try:
                char = int(char)
                break
            except:
                delete += 1

        doi = doi[delete:]
        url = "http://185.39.10.101/scimag/ads.php?doi={}".format(doi)
    
    except:
        success = False

    return url, success


def retrieve_article(url):

    count = 0
    fckElsevier, filename = "", ""
    print("Retrieving article...")

    while count < 5:

        try:
            success = True
            r = requests.get(url=url)
            filename = str(r.content).split("Year: ")[1].split("<br>")[0] + " - " + str(r.content).split("Title: ")[1].split("<br>")[0]
            soup = BeautifulSoup(r.content,"html.parser")

            for url in soup.find_all("a", href=True):
                fckElsevier = url.get("href")
                if "booksdl.org" in str(fckElsevier).lower():
                    break

            if "wrong parameter doi" in str(r.content).lower() or "book with such" in str(r.content).lower():
                success = False
                break

            break

        except:
            success = False
            count += 1
    
    return fckElsevier, filename, success


def download_article(fckElsevier):

    count = 0
    filename, filecontent = "", ""
    print("Downloading article...")

    while count < 5:

        try:
            success = True
            r = requests.get(url=fckElsevier)
            filecontent = r.content
            if len(filecontent) <= 10000:
                success = False
            break

        except:
            success = False
            count += 1

    return filecontent, success


def save_article(filename, filecontent, single, length, n_articles, url):

    try:
        n_articles += 1
        success = True
        filename = filename.replace("<","").replace(">","").replace(":","").replace("\"","").replace("/","").replace("\\","")\
        .replace("|","").replace("?","").replace("*","")
        with open("./saved references/{}.pdf".format(filename), "wb") as opening:
            opening.write(filecontent)
            if single is True:
                print(colored("Article saved","green"))
            else:
                print(colored("Article {}/{} saved".format(str(n_articles), length),"green"))
    
    except:
        success = False
    
    return n_articles, success


def error_logs(url):

    print(colored("Something wrong occured (DOI : {})\nIt may be related to Libgen's servers\nIf it persists, help at bastien.paris@etu.univ-grenoble-alpes.fr".format(url.split("=")[1]),"red"))
    with open("error_logs.txt","a") as opening:
        opening.write("\n{}".format(url.split("=")[1]))