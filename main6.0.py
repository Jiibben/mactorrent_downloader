import os
from bs4 import BeautifulSoup
import time
import requests
import csv
import os
import datetime
downloads  = 0
passes = 1
path = "/home/allanburnier/projects/mactorrent_downloader/torrents/"
dwn_file = "dwn.txt"
csv_file = "log.csv"
sleeping_time = 12*3600
restart = 20
def check_path(path):
    if path.endswith("/") and os.path.exists(path):
        return True
    else:
        print("[-]invalid path")
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
    print("downloading : %s " % len(list_of_dict))
    for i in list_of_dict:
        print("[+]downloading %s" % i["name"][0:10], end="\r")
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
check_path(path)

try:
    while True:
        check_file(csv_file)
        check_file(dwn_file)
        main = scrapping("http://mactorrent.co/torrents1.php?mode=category&cat=28")
        download(main)
        write_csv(main, csv_file)
        if passes % restart == 0 and passes !=0:
            os.remove(csv_file)
            os.remove(dwn_file)
            open(csv_file, "w+").close()
            open(dwn_file, "w+").close()
        print("[+]finished passes number %s " % passes)
        passes += 1
        print("[+]going to sleep at %s for %s hours" % (datetime.datetime.now(), sleeping_time/3600))
        time.sleep(sleeping_time)

except KeyboardInterrupt:
    print("[+]detected ctrl+C stopping ...")
else:
    print("[-]something went wrong")