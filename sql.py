#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from config import sql
from text import *
import pymysql


class Sql(object):
    def __init__(self, info):
        if isinstance(info, dict):
            self.address = info['address']
            self.port = info['port']
            self.username = info['username']
            self.password = info['password']
            self.database = info['database_name']
            self.db = None

    def connect(self):
        self.db = pymysql.connect(host=self.address, port=self.port, user=self.username,
                                  passwd=self.password, db=self.database, charset='utf8')

    def insert_film(self, film, info, booking):
        if self.is_exist('film', 'name', film):
            return False
        cursor = self.db.cursor()
        sql = "INSERT INTO film (name, director, role, type, score, country, runtime, ReleaseDate, booking) VALUES ('%s', '%s', '%s', '%s', '%f', '%s', '%s', '%s', '%s')" % (
            film, info['director'], pymysql.escape_string(str(info['role_list'])), pymysql.escape_string(info['type']), float(info['score']), info['country'], info['runtime'], pymysql.escape_string(info['ReleaseDate']), pymysql.escape_string(str(booking)))
        try:
            cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
            return False
        finally:
            cursor.close()
            return True

    def insert_comment(self, film, content, star, uid, time):
        if star == 0:
            return False
        content = cht_to_chs(content.replace('\n', '').replace('\r', ''))
        cursor = self.db.cursor()
        sql = "INSERT INTO comment (film, content, star, author_id, time) VALUES ('%s', '%s', '%f', '%d', '%s')" % (
            film, content, float(star), int(uid), time)
        try:
            cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
            return False
        finally:
            cursor.close()
            return True

    def insert_user_info(self, author, location):
        if self.is_exist('user', 'uid', str(author['id'])):
            return False
        cursor = self.db.cursor()
        sql = 'INSERT INTO user (uid, name, location) VALUES ("%d", "%s", "%s")' % (
            int(author['id']), author['name'], location)
        try:
            cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
            return False
        finally:
            cursor.close()
            return True

    def is_exist(self, table, keyword, value):
        self.reconnect()
        cursor = self.db.cursor()
        sql = 'SELECT COUNT(*) from %s where `%s` = "%s"' % (table, keyword, value)
        cursor.execute(sql)
        data = cursor.fetchone()
        cursor.close()
        if data[0]:
            return True
        else:
            return False

    def delete(self, table, keyword, value):
        self.reconnect()
        cursor = self.db.cursor()
        sql = "DELTE FROM %s WHERE %s = '%s'" % (table, keyword, value)
        try:
            cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
            return False
        finally:
            cursor.close()
            return True

    def select(self, commit):
        self.reconnect()
        cursor = self.db.cursor()
        cursor.execute(commit)
        data = cursor.fetchall()
        cursor.close()
        return data

    def reconnect(self):
        try:
            self.db.ping()
        except:
            self.connect()

    def close(self):
        self.db.close()


def connect():
    db = Sql(sql)
    db.connect()
    return db


def test():
    db = connect()
    commit = 'SELECT * FROM `film` ORDER BY `film`.`score` DESC'
    data = db.select(commit)
    film_list = []
    director_list = []
    role_list = []
    for x in data:
        if x[2] == 'None':
            continue
        if x[5] > 9.0:
            film_list.append(x[1])
        elif '中国' in x[-2] and('2018' in x[-2] or '2017' in x[-2] or '2016' in x[-2] or '2015' in x[-2] or'2014' in x[-2] or'2013' in x[-2] or '2012' in x[-2] or '2011' in x[-2]):
            film_list.append(x[1])
        if x[1] in film_list and x[2] not in director_list:
            director_list.append(x[2])
        if x[1] in film_list:
            role = re.findall("'name': '(.*?)'", x[3])
            for i in role:
                if i not in role_list:
                    role_list.append(i)
    flag = 1
    f = open('film.txt', 'w', encoding='utf-8')
    for x in film_list:
        f.write(str(flag) + ' ' + x + '\n')
        flag += 1
    f.close()
    flag = 1
    f = open('director.txt', 'w', encoding='utf-8')
    for x in director_list:
        f.write(str(flag) + ' ' + x + '\n')
        flag += 1
    f.close()
    flag = 1
    f = open('role.txt', 'w', encoding='utf-8')
    for x in role_list:
        f.write(str(flag) + ' ' + x + '\n')
        flag += 1
    f.close()
    print(len(film_list), len(director_list), len(role_list))


if __name__ == '__main__':
    test()
