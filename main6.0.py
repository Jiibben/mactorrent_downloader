from logging import log
import os
from time import sleep
from bs4 import BeautifulSoup
import time
import requests
import csv
import os
import datetime
import logging

# different variables :
downloads  = 0
p = "/home/allanburnier/projects/mactorrent_downloader/mactorrent_downloader"
path = p + "/torrents/"
log_path = p + "/logs/"
dwn_file = log_path + "dwn.txt"
csv_file = log_path + "log.csv"
log_file = log_path + "logging.log"
sleeping_time = 12*3600
sleeping_time_error = 1*3600

# create logger
logger = logging.getLogger('log')
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler(log_file)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)



def check_path(path):
    if path.endswith("/") and os.path.exists(path):
        return True
    else:
        print("[-]path : %s doesn't exist or is not valid"% path)
        raise AttributeError("invalid path")

def scrapping(url):
    already_downloaded = list(map(lambda x: x.replace("\n", ""), open(dwn_file, "r+").readlines()))
    dwn = []
    dtl = []
    list_of_dict = []
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    for i in soup.find_all("a", href=True):
        if "mode=download" in str(i) and str(i["href"]) not in already_downloaded:
            dwn.append(str(i["href"]))
        elif "mode=details" in str(i) and str(i) not in already_downloaded:
            dtl.append(str(i["href"]))
        
    for x in range(len(dwn)):
        list_of_dict.append(
            {
                "link":dwn[x],
                "name": get_title(str(dtl[x]))
            }
        )
    return list_of_dict

def get_title(url):
    sp = BeautifulSoup(requests.get(url).content, 'html.parser')
    eny = sp.find_all("div", attrs={'align':'center'})[1].find(href=True)
    if eny is not None:
        return eny.text
    else:
        return "not found"

def write_csv(dict, filename):
    w = csv.writer(open(filename,"a+"))
    w.writerow(["name", "link", "date"])
    for sa in dict:
        w.writerow([sa["name"], sa["link"], datetime.datetime.now()])

def download(list_of_dict):
    global downloads
    print("[+]Starting download of : %s torrents" % len(list_of_dict))
    for i in list_of_dict:
        print("[+]downloading torrent nammed : %s" % i["name"][0:10], end="\r")
        requ = requests.get("http://mactorrent.co/" + str(i["link"]), allow_redirects=True)
        open(dwn_file, "a+").write(str(i["link"]) + "\n")
        open(path + "torrent_" + str(downloads) + ".torrent", "wb").write(requ.content)
        downloads += 1

def check_file(file):
    if os.path.isfile(file):
        return True
    else:
        print("[+]creating file %s " % file)
        os.system("touch %s" %file)


def filecheck(file, limit, keep : int):
    i = open(file, "r").readlines()
    if len(i) >= limit:
        del i[0:len(i)-keep]
        print("[+]file: %s was too large deleted %s lines." %(file, len(i)-keep))
        open(file, "w+").writelines(i)
    else:
        pass
def sleep_program(time_, err):
    if not err:
        time.sleep(time_)
        print("[+]going to sleep at %s for %s hours" % (datetime.datetime.now(), sleeping_time/3600))
    else:
        time.sleep(time_)
        print("[-]something went wrong skipping this pass and going to sleep at %s for %s hours CHECK THE LOG FILE FOR MORE INFORMATION" % (datetime.datetime.now(), sleeping_time/3600))

def main():

    passes = 1
    check_path(path)
    check_path(log_path)

    while True:
        try:
            check_file(csv_file)
            check_file(dwn_file)
            print("[+]Starting script")
            main = scrapping("http://mactorrent.co/torrents1.php?mode=category&cat=28")
            download(main)
            write_csv(main, csv_file)
            filecheck(dwn_file, 1500, 200)
            print("[+]finished passes number : %s " % passes)
            passes += 1
            sleep_program(sleeping_time, False)
        except Exception as e:
            logger.error("an error occured %s " % e)
            sleep_program(sleeping_time_error, True)

    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[+] detected ctrl + c stopping ...")