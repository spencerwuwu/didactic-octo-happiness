#!/usr/bin/env python3.7


import sys
import os
import time

from subprocess import Popen, PIPE
from bs4 import BeautifulSoup

"""
"   get the last released version from https://ftp.gnu.org/pub/gnu/xxx
"""
def get_download(html):
    with open(html) as target_f:
        soup = BeautifulSoup(target_f, features="lxml")
    columns = soup.find("table").find_all("tr")

    columns.reverse()

    for column in columns:
        obj = column.find_all("td")
        if len(obj) == 0:
            continue
        obj = obj[1].a.string
        if "sig" in obj:
            continue
        else:
            return obj

"""
"   Store the released projects into gnu_projects
"""
def save_project(target):
    print("Proecssing %s..." % target)
    target = target.lower()
    wget_cmd = "wget -O index.html https://ftp.gnu.org/pub/gnu/" + target

    print("\t" + wget_cmd)
    process = Popen(wget_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = process.communicate()
    err = err.decode()

    if "ERROR" in err:
        print("\tFailed to find page for %s" % target)
    else:
        obj = get_download("index.html")
        store_cmd = "wget -O gnu_projects/%s https://ftp.gnu.org/pub/gnu/%s/%s" % (obj, target, obj)
        print("\t" + store_cmd)
        process = Popen(store_cmd, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = process.communicate()
        print("\tStored gnu_project/%s" % obj)

"""
"   wget -O GNU.html https://directory.fsf.org/wiki/GNU
"""
def main():
    with open("GNU.html") as target_f:
        soup = BeautifulSoup(target_f, features="lxml")
    table = soup.find("table", class_="sortable wikitable smwtable").tbody

    targets = []

    for tr in table.find_all('tr', class_="row-even"):
        targets.append(tr.find_all("td", class_="smwtype_wpg")[0].a.string)
    for tr in table.find_all('tr', class_="row-odd"):
        targets.append(tr.find_all("td", class_="smwtype_wpg")[0].a.string)

    for t in targets:
        save_project(t)
        print("Sleep for 2 secnods...")
        time.sleep(2)


if __name__ == '__main__':
    main()
