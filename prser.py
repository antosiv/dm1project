import requests
from lxml import html
import csv
from tqdm import tqdm
import random
from time import sleep
import numpy as np
import sys


class Req:

    def __init__(self, proxies_file):

        self.curr_proxy = 0
        r = requests.get('https://hidemy.name/api/proxylist.txt?out=plain&lang=en&code= <code> &maxtime=500')
        self.proxies = r.text.split('\r\n')

    def get(self, url, headers=None):
        while True:
            try:
                r_ = requests.get(url, proxies={'https': self.proxies[self.curr_proxy]}, timeout=10)
            except Exception:
                self.curr_proxy += 1
                if self.curr_proxy == len(self.proxies):
                    self.update_proxies()
                continue
            except requests.exceptions.Timeout:
                self.curr_proxy += 1
                if self.curr_proxy == len(self.proxies):
                    self.update_proxies()
                continue
            tree_ = html.fromstring(r_.text)
            try:
                tmp = tree_.xpath('/html/head/title')[0].text.split()[0]
            except IndexError:
                with open('data.html', 'w') as data:
                    data.write(r_.text)
                tmp = None
            except AttributeError:
                with open('data.html', 'w') as data:
                    data.write(r_.text)
                tmp = None
            if r_.status_code != 200 or tmp == 'Доступ':
                self.curr_proxy += 1
                if self.curr_proxy == len(self.proxies):
                    self.update_proxies()
                continue
            else:
                return r_

    def update_proxies(self):
        sleep(60)
        self.curr_proxy = 0
        r = requests.get('https://hidemy.name/api/proxylist.txt?out=plain&lang=en&code=466628178860992&maxtime=500')
        self.proxies = r.text.split('\r\n')




headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0'
    }


def get_info(url, session):
    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)

    i = 1
    res = {}
    while True:
        try:
            field = tree.xpath('/html/body/div[4]/div[1]/div[3]/div[2]/div[1]/div[2]/div[3]/div/ul/li[%i]/span' % i)[0].text
            value = tree.xpath('/html/body/div[4]/div[1]/div[3]/div[2]/div[1]/div[2]/div[3]/div/ul/li[%i]/text()' % i)[1]
            i += 1
            res.update({field[:-2]: value[:-2]})
        except IndexError:
            break
    try:
        price = tree.xpath('/html/body/div[4]/div[1]/div[3]/div[2]/div[2]/div[1]/div/div[1]/div/span')[0].text
        res.update({'Цена': price[1:]})
    except IndexError:
        return {}
    return res


def get_last_search_pos(mark, session):
    req = session.get('https://www.avito.ru' + mark, headers=headers)
    r_tree = html.fromstring(req.text)
    tmp = r_tree.xpath('/html/body/div[5]/div[1]/div[4]/div[1]/div[4]/div[2]/a[10]/@href')[0]
    tmp = tmp[tmp.index('p=') + 2:]
    try:
        trash_ind = tmp.index('&radius=')
    except ValueError:
        return int(tmp)
    return int(tmp[:trash_ind])


def get_cars(url, session):
    r_ = session.get(url, headers=headers)
    tree_ = html.fromstring(r_.text)
    i = 1
    links = []
    while True:
        tmp_2 = tree_.xpath('/html/body/div[5]/div[1]/div[4]/div[1]/div[2]/div[1]/div[%i]/@class' % i)
        if not tmp_2:
            break

        tmp = tree_.xpath('/html/body/div[5]/div[1]/div[4]/div[1]/div[2]/div[1]/div[%i]/@id' % i)
        if not tmp:
            i += 1
            continue
        try:
            car_link = tree_.xpath('/html/body/div[5]/div[1]/div[4]/div[1]/div[2]/div[1]/div[%i]/div[2]/div[1]/h3/a/@href' % i)[0]
        except IndexError:
            break
        links.append(car_link)
        i += 1

    i = 1
    while True:
        try:
            car_link = tree_.xpath('/html/body/div[5]/div[1]/div[4]/div[1]/div[2]/div[2]/div[%i]/div[2]/div[1]/h3/a/@href' % i)[0]
            links.append(car_link)
            i += 1
        except IndexError:
            break
    return links


session = Req('proxies.csv')
with open('marks.csv', 'r') as mrks:
    marks_ = []
    reader = csv.reader(mrks)
    for row in reader:
        marks_.extend(row)

marks = []
tmp = ''
for i in sys.argv[1:]:
    marks.append(marks_[int(i)])
    tmp += i

head = get_info('https://www.avito.ru/moskva/avtomobili/bmw_1_seriya_2013_1062462732', session).keys()
with open('data' + tmp + '.csv', 'a') as data:
    writer = csv.DictWriter(data, fieldnames=head)
    writer.writeheader()
    for mark in marks:
        try:
            mark_ = mark[:mark.index('?radius=')]
        except ValueError:
            mark_ = mark
        print(mark_, ':')
        for i in range(1, get_last_search_pos(mark_, session) + 1):
            links = get_cars('https://www.avito.ru' + mark_ + '?p=%i' % i, session)
            ids = np.arange(0, len(links))
            np.random.shuffle(ids)
            for i in tqdm(range(ids.size)):
                info = get_info('https://avito.ru' + links[ids[i]], session)
                writer.writerow(info)