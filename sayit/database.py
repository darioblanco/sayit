# -*- coding: UTF-8 -*-
import time
from datetime import timedelta

import redis
from pbkdf2 import crypt

from sayit.settings import REDIS, SECRET_KEY

rd = redis.StrictRedis(REDIS['host'],
                       port=REDIS['port'],
                       password=REDIS['password'],
                       socket_timeout=REDIS['timeout'])


class User(object):
    def __init__(self, username, password, enabled=True):
        self.username = username
        self.user_data = {
            'password': crypt(password, SECRET_KEY),
            'enabled': enabled
        }

    def save(self):
        """Stores the created user"""
        rd.hmset('user:{0}'.format(self.username), self.user_data)

    @classmethod
    def remove(cls, username):
        """Removes the specified user"""
        rd.delete('user:{0}'.format(username))

    @classmethod
    def get(cls, username):
        """Returns user and password"""
        user_data = rd.hgetall('user:{0}'.format(username))
        if user_data:
            user_data['username'] = username
        return user_data

    @classmethod
    def check_user_password(cls, username, password):
        return (rd.hget('user:{0}'.format(username), 'password') ==
                crypt(password, SECRET_KEY))


class Task(object):
    def __init__(self, username, title, status='uncompleted'):
        self.username = username
        self.timestamp = time.time()  # Float creation time
        self.task_id = repr(self.timestamp)  # The taskid
        self.data = {
            'username': username,
            'title': title,
            'status': status
        }

    def save(self):
        # Hash of task with the full timestamp as id
        rd.hmset('task:{0}'.format(self.task_id), self.data)
        # Set the filters as a sorted set of task keys
        score = timedelta(seconds=self.timestamp).days
        # Ordered tasks belonging to a user
        rd.zadd('tasks.all:{0}'.format(self.username), score, self.task_id)
        # Ordered completed or uncompleted tasks belonging to a user
        rd.zadd('tasks.{0}:{1}'.format(self.data['status'], self.username),
                score, self.task_id)

    @classmethod
    def remove(cls, task_id):
        key = 'task:{0}'.format(task_id)
        data = rd.hgetall(key)
        rd.zrem('tasks.all:{0}'.format(data['username']), task_id)
        rd.zrem('tasks.{0}:{1}'.format(data['status'], data['username']),
                task_id)
        rd.delete(key)

    @classmethod
    def edit_field(cls, task_id, field_name, field_value):
        task_key = 'task:{0}'.format(task_id)
        if field_name == 'status':
            # Extra logic for the status field change
            data = rd.hgetall(task_key)
            if not (data['status'] == field_value):
                # Remove from the previous state list
                tasks_key = 'tasks.{0}:{1}'.format(data['status'],
                                                   data['username'])
                score = rd.zscore(tasks_key)
                rd.zrem(tasks_key, task_id)
                # Add to the new state list
                rd.add('tasks.{0}:{1}'.format(field_value, data['username']),
                       score, task_id)
        rd.hset(task_key, field_name, field_value)

    @classmethod
    def get_tasks(cls, username, status='all', limit=20):
        """Returns a list of tasks for the specified user"""
        tasks = []
        task_ids = rd.zrevrange("tasks.{0}:{1}".format(status, username),
                                0, limit)
        for task_id in task_ids:
            task_data = rd.hgetall("task:{0}".format(task_id))
            task_data['timestamp'] = task_id
            tasks.append(task_data)

        return tasks
