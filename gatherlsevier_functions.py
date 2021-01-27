import requests, time, random, html, os
from threading import Thread, RLock
from bs4 import BeautifulSoup
from colorama import init, deinit
from termcolor import colored


def retrieve_url(single, doi, content, print_lock):

    url = {}
    doi_x = ""

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

        doi_x = doi[delete:]
        url["LIBGEN"] = "http://111.90.145.71/scimag/get.php?doi={}".format(doi_x)
        url["SCI-HUB"] = "https://scihub.unblockit.dev/{}".format(doi_x)
    
    except:
        success = False

    return url, success, doi_x


def retrieve_article(url, print_lock, main):

    backup = False
    count = 0
    pdf_address, filename = "", ""
    with print_lock:
        print("Retrieving article...")
    
    while count <= 10:

        if main == "LIBGEN":

            if count == 4:
                print("Switching for Sci-hub...")
                count += 1
                main = "SCI-HUB"
                backup = True
                continue

            try:
                success, found = True, True

                r = requests.get(url=url["LIBGEN"])
                
                soup = BeautifulSoup(r.content,"html.parser")

                if "wrong parameter doi" in str(r.content).lower() or "book with such" in str(r.content).lower():
                    if backup is True:
                        success, found = False, False
                        break
                    else:
                        print("Switching for Sci-hub...")
                        backup = True
                        main = "SCI-HUB"
                        count = 5
                        continue
                    break

                for url in soup.find_all("a", href=True):
                    pdf_address = url.get("href")
                    if "/scimag/" in str(pdf_address).lower():
                        break


                authors = str(r.content).split("Author(s): ")[1].split("<br>")[0]
                if len(authors.split(";")) >= 3:
                    authors = ";".join(authors.split(";")[0:3]) + " et al."

                year = str(r.content).split("Year: ")[1].split("<br>")[0]

                title = str(r.content).split("Title: ")[1].split("<br>")[0]

                filename = authors + " (" + year + "). " + title
                break

            except:
                success = False
                count += 1
                time.sleep(random.randrange(1000,5000)/1000)
    

        elif main == "SCI-HUB":

            if count == 4:
                print("Switching for Libgen...")
                count += 1
                main = "LIBGEN"
                backup = True
                continue

            try:
                success, found = True, True

                r = requests.get(url=url["SCI-HUB"])

                soup = BeautifulSoup(r.content,"html.parser")

                if "article not found" in str(r.content).lower():
                    if backup is True:
                        success, found = False, False
                        break
                    else:
                        print("Switching for Libgen...")
                        backup = True
                        main = "LIBGEN"
                        count = 5
                        continue

                for url in soup.find_all("iframe"):
                    pdf_address = url.get("src")


                filename = str(r.content).split('onclick = "clip(this)">')[1].split("</i>")[0].replace("<i>","").replace("\\xe2\\x80\\x93","-")

                if len(filename.split(".,")) > 3:
                    authors = ".,".join(filename.split(".,")[0:3])
                    title = "., et al. ("+ filename.split(" (")[1]
                    filename = authors + title
                    
                break

            except:
                success = False
                count += 1
                time.sleep(random.randrange(1000,5000)/1000)

    return pdf_address, filename, success, found


def download_article(pdf_address, print_lock):

    count = 0
    filecontent = ""
    with print_lock:
        print("Downloading article...")

    while count <= 10:

        try:
            success = True

            r = requests.get(url=pdf_address)
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
            filename = filename.replace("<","").replace(">","").replace(":"," -").replace("\"","").replace("/","").replace("\\","")\
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
    
    return filename, n_articles, success


def error_logs(doi_x, found, print_lock):

    if found is True:
        with print_lock:
            print(colored("Something wrong occured (DOI : {})\nIt may be server-side related (Libgen/Sci-hub)\nIf it persists over time, help at paris.bastien@hotmail.com".format(doi_x),"red"))
        with open("error_logs.txt","a") as opening:
            opening.write("\n{}".format(doi_x))
            
    elif found is False:
        with print_lock:
            print(colored("Something wrong occured (DOI : {} not found on Libgen and Sci-hub)".format(doi_x),"red"))
        with open("error_logs.txt","a") as opening:
            opening.write("\n{}".format(doi_x))