import requests, time, random, html
from threading import Thread, RLock
from bs4 import BeautifulSoup
from colorama import init, deinit
from termcolor import colored


def retrieve_url(single, doi, content, print_lock):

    url = ""

    try:
        success = True
        if single is False:
            doi = content.pop(0)
            
        doi = doi.replace("gaelnomade-1","")

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


def retrieve_article(url, print_lock):

    count = 0
    fckElsevier, filename = "", ""
    with print_lock:
        print("Retrieving article...")

    while count <= 10:

        try:
            success, found = True, True

            r = requests.get(url=url)

            if r.status_code == 404:
                success, found = False, False
                break

            authors = str(r.content).split("Author(s): ")[1].split("<br>")[0]
            if len(authors.split(";")) >= 3:
                authors = ";".join(authors.split(";")[0:3]) + " et al."

            year = str(r.content).split("Year: ")[1].split("<br>")[0]

            title = str(r.content).split("Title: ")[1].split("<br>")[0]

            filename = authors + " - " + year + " - " + title

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
            time.sleep(random.randrange(1000,5000)/1000)
    
    return fckElsevier, filename, success, found


def download_article(fckElsevier, print_lock):

    count = 0
    filecontent = ""
    with print_lock:
        print("Downloading article...")

    while count <= 10:

        try:
            success = True

            r = requests.get(url=fckElsevier)
            filecontent = r.content
            if len(filecontent) <= 10000:
                success = False
                count += 1
                time.sleep(random.randrange(1000,5000)/1000)

            if success is True:
                break

        except:
            success = False
            count += 1
            time.sleep(random.randrange(1000,5000)/1000)

    return filecontent, success


def save_article(filename, filecontent, single, length, n_articles, url, print_lock):

    count = 0
    n_articles += 1
    bytes_clearer = 0

    filename = filename.split("\\x")
    for content in filename:
        if bytes_clearer != 0:
            filename[bytes_clearer] = content[2:]
        bytes_clearer +=1
    filename = "".join(filename)
    filename = html.unescape(filename)

    while count <= 100:

        try:
            success = True
            filename = filename.replace("<","").replace(">","").replace(":",";").replace("\"","").replace("/","").replace("\\","")\
            .replace("|","").replace("?","").replace("*","")

            if count == 0:
                with open("./saved references/{}.pdf".format(filename), "wb") as opening:
                    opening.write(filecontent)
            else:
                with open("./saved references/{}.pdf".format(filename[:-count]), "wb") as opening:
                    opening.write(filecontent)

            if single is True:
                with print_lock:
                    print(colored("Article saved","green"))
            else:
                with print_lock:
                    print(colored("Article {}/{} saved".format(str(n_articles), length),"green"))

            break
        
        except:
            success = False
            count += 1
    
    return n_articles, success


def error_logs(url, found, print_lock):

    if found is True:
        with print_lock:
            print(colored("Something wrong occured (DOI : {})\nIt may be related to Libgen's servers\nIf it persists, help at paris.b6stien@gmail.com".format(url.split("=")[1]),"red"))
        with open("error_logs.txt","a") as opening:
            opening.write("\n{}".format(url.split("=")[1]))
            
    elif found is False:
        with print_lock:
            print(colored("Something wrong occured (DOI : {} not found on Libgen's servers)".format(url.split("=")[1]),"red"))
        with open("error_logs.txt","a") as opening:
            opening.write("\n{}".format(url.split("=")[1]))