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
        finally:
            cursor.close()
            return True

    def insert_comment(self, film, content, star, uid, time):
        if star == 0:
            return False
        self.reconnect()
        content = cht_to_chs(content.replace('\n', '').replace('\r', ''))
        cursor = self.db.cursor()
        sql = "INSERT INTO comment (film, content, star, author_id, time) VALUES ('%s', '%s', '%f', '%d', '%s')" % (
            film, content, float(star), int(uid), time)
        try:
            cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
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
        finally:
            cursor.close()
            return True

    def is_exist(self, table, keyword, value):
        self.reconnect()
        cursor = self.db.cursor()
        sql = 'SELECT COUNT(*) from %s where `%s` = "%s"' % (table, keyword, value)
        cursor.execute(sql)
        data = cursor.fetchone()
        if data[0]:
            return True
        else:
            return False

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
