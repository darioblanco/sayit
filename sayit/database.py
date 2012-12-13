# -*- coding: UTF-8 -*-

import redis
from datetime import datetime

from sayit.settings import REDIS

rd = redis.StrictRedis(REDIS['host'],
                       port=REDIS['port'],
                       password=REDIS['password'],
                       socket_timeout=REDIS['timeout'])


class User(object):
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def save(self):
        rd.hset('user:{0}'.format(self.user), password=self.password)

    @classmethod
    def remove(cls, user):
        rd.delete('user:{0}'.format(user))


class Task(object):
    def __init__(self, user, title):
        self.user = user
        self.title = title
        self.date = datetime.now().strftime("%d/%m/%y-%H.%M")

    def save(self):
        rd.zadd('user-task:{0}'.format(self.user), self.date, self.title)

    @classmethod
    def remove(cls, user):
        rd.delete('user-task:{0}'.format(user))
