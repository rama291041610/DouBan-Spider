#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from text import *
import requests
import datetime
import time
import json
import bs4
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}


def sleep(res):
    if "rate_limit_exceeded2:" in res:
        print(datetime.datetime.now(), "sleep for two minutes")
        time.sleep(120)
        return True
    else:
        return False


class Movie(object):
    def __init__(self, name):
        self.name = name
        self.douban_id = None
        self.maoyan_id = None

    def set_basis(self):
        if self.douban_id == None:
            self.set_douban_id()
        if self.maoyan_id == None:
            self.set_maoyan_id()

    def set_douban_id(self):
        r = requests.get(
            'https://api.douban.com/v2/movie/search?count=10&apikey=0b2bdeda43b5688921839c8ecb20399b&q=' + self.name)
        if sleep(r.text):
            self.set_douban_id()
            return
        res = r.json().get('subjects', [])
        for x in res:
            if self.name in x['title'] and x['subtype'] == 'movie':
                self.douban_id = x['id']
                return
        if self.douban_id == None:
            self.douban_id = -1

    def set_maoyan_id(self):
        rule = r'data-val="{movieId:(.*?)}">' + self.name
        r = requests.get('http://maoyan.com/query?kw=' + self.name, headers=headers)
        maoyan_id = re.search(rule, r.text)
        if maoyan_id:
            self.maoyan_id = maoyan_id.group(1)

    def get_film_info(self):
        if self.douban_id == None:
            self.set_basis()
        if self.douban_id == -1:
            return False
        r = requests.get('https://movie.douban.com/subject/' + str(self.douban_id), headers=headers)
        soup = bs4.BeautifulSoup(r.text, "lxml")
        type_list = soup.find_all(property="v:genre")
        genres = ''
        for x in type_list:
            genres += x.string.strip() + '\\'
        genres = genres[:-1]
        runtime = soup.find(property="v:runtime").text
        country = re.search('<span class="pl">制片国家/地区:</span> (.*?)<br/>', r.text)
        ReleaseDate_list = soup.find_all(property="v:initialReleaseDate")
        ReleaseDate = ''
        for x in ReleaseDate_list:
            ReleaseDate += x.string.strip() + '\\'
        ReleaseDate = ReleaseDate[:-1]
        director = soup.find(rel="v:directedBy").text
        score = soup.find(property="v:average").text
        role_list_soup = soup.find_all(attrs={'class': 'info'})
        role_list = []
        for x in role_list_soup:
            name = x.find(attrs={'class': 'name'}).string
            try:
                role = x.find(attrs={'class': 'role'}).string
            except:
                role = None
            finally:
                if role != '导演':
                    role_list.append({'name': name, 'role': role})
        return {'type': genres, 'runtime': runtime, 'country': country.group(1), 'score': score, 'ReleaseDate': ReleaseDate, 'director': director, 'role_list': role_list}

    def get_booking(self):
        if self.maoyan_id == None:
            self.set_maoyan_id()
        r = requests.get('http://m.maoyan.com/movie/' + str(self.maoyan_id) + '/box?_v_=yes', headers=headers)
        detail = re.search('<script>var AppData = (.*?);</script>', r.text)
        if detail:
            booking = json.loads(detail.group(1))
            if booking.get('area', None):
                return booking
            else:
                return False
        else:
            return None

    def get_comments(self, start):
        if self.douban_id == None:
            self.set_douban_id()
        r = requests.get('https://api.douban.com/v2/movie/subject/' +
                         str(self.douban_id) + '/comments?count=100&start=' + str(start) + '&apikey=0b2bdeda43b5688921839c8ecb20399b')
        if sleep(r.text):
            self.get_comments(start)
            return
        res = r.json()
        return res.get('comments', None)


def get_user_local(uid):
    r = requests.get('https://api.douban.com/v2/user/' + str(uid) + '?apikey=0b2bdeda43b5688921839c8ecb20399b')
    if sleep(r.text):
        get_user_local(uid)
        return
    localname = r.json().get('loc_name', 'NULL')
    return localname


def get_film_top250():
    url = 'http://api.douban.com/v2/movie/top250'
    film_list = []
    for x in range(5):
        start = x * 50
        r = requests.get(url, params={'start': str(start), 'count': '50',
                                      'apikey': '0b2bdeda43b5688921839c8ecb20399b'})
        tmp = r.json()
        for name in tmp['subjects']:
            film_list.append(name['title'])
    return film_list


def get_film_list_fm(p):
    r = requests.get('http://dianying.fm/search/?p=' + str(p), cookies={
                     'sessionid': '".eJxVy80OgjAQBOB36VlISyi03vDkyQsP0Gy325SIkPTHxBjfXTBeuE1m5nszNyVcnxRfBkuMtGR2ZjOl6jGlKoLdo9BSsRMzUHIwJVE0AVLYftpqtMilcui096LvWoVKcuebnnMgJbXzXtERW8A7LW7zgLiWJde_LQUQ9W0dYc7jdRDD1l3-zwOfdtk2otOSfb6S2kA_:1fC5qU:6HD585xd0sOeZUNvM2CgtGrAnSQ"'})
    film = bs4.BeautifulSoup(r.text, "lxml").find_all(attrs={'class': 'fm-movie-title'})
    film_list = []
    for x in film:
        film_list.append(x.find('a').text.strip())
    return film_list


def get_film_maoyan(id):
    r = requests.get('http://maoyan.com/films/' + str(id) + '?_v_=yes', headers=headers)
    soup = bs4.BeautifulSoup(r.text, "lxml")
    return soup.h3.string
