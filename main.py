#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' DouBan-Spider '
__author__ = '惊蛰'

from movie import *
from sql import *
import requests
import datetime
import time
import sys
import re


def crawler(film):
    print(film)
    m = Movie(film)
    film_info = m.get_film_info()
    if film_info:
        if db.insert_film(film, film_info, m.get_booking()):
            for i in range(5):
                start = i * 100
                comment_list = m.get_comments(start)
                try:
                    for x in comment_list:
                        db.insert_comment(film, x['content'], x['rating']['value'],
                                          x['author']['id'], x['created_at'])
                        db.insert_user_info(x['author'], get_user_local(x['author']['id']))
                except TypeError as comment_list:
                    print("Can't get the comments.")
                    return False
        else:
            return False
    else:
        return False


def main():
    global db
    db = connect()
    for p in range(1, 800):
        film_list = get_film_list_fm(p)
        if film_list == []:
            break
        else:
            for film in film_list:
                crawler(film)
    for id in range(1, 150000):
        film = get_film_maoyan(id)
        if film:
            crawler(film)
        else:
            break
    db.close()
    print("finish!")


if __name__ == '__main__':
    main()
