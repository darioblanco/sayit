# -*- coding: UTF-8 -*-
import time
from datetime import datetime

import redis

from sayit.settings import REDIS

rd = redis.StrictRedis(REDIS['host'],
                       port=REDIS['port'],
                       password=REDIS['password'],
                       socket_timeout=REDIS['timeout'])


class User(object):
    def __init__(self, username, password, enabled=True):
        self.username = username
        self.user_data = {
            'password': password,
            'enabled': enabled
        }

    def save(self):
        """Stores the created user"""
        rd.hmset('user:{0}'.format(self.username), self.user_data)

    @classmethod
    def remove(cls, username):
        """Removes the specificed user"""
        rd.delete('user:{0}'.format(username))

    @classmethod
    def get(cls, username):
        """Returns user and password"""
        try:
            user_data = rd.hgetall('user:{0}'.format(username))
        except redis.RedisError:
            user_data = None
        if user_data:
            user_data['username'] = username
        return user_data


class Task(object):
    def __init__(self, username, title, completed=False):
        self.username = username
        self.timestamp = int(time.time()) + 1  # The taskid
        dt = datetime.now()
        ic = dt.isocalendar()  # year/weeknumber/weekday
        self.data = {
            'day': dt.strftime("%d/%m/%Y"),
            'week': "{0}/{1}".format(ic[1], ic[0]),
            'title': title,
            'completed': False
        }

    def save(self):
        # Hash of task with user
        rd.hmset('task:{0}:user:{1}'.format(self.timestamp,
                                            self.username),
                 self.data)
        # List of tasks ids per day and user
        rd.lpush('taskday:{0}:user:{1}'.format(self.data['day'],
                                               self.username),
                 self.timestamp)
        # List of tasks ids per week and user
        rd.lpush('taskweek:{0}:user:{1}'.format(self.data['week'],
                                                self.username),
                 self.timestamp)

    @classmethod
    def remove(cls, username, task_id):
        key = 'task:{0}:user:{1}'.format(task_id, username)
        data = rd.hgetall(key)
        rd.lrem('taskday:{0}:user:{1}'.format(data['day'], username), 1,
                task_id)
        rd.lrem('taskweek:{0}:user:{1}'.format(data['week'], username), 1,
                task_id)
        rd.delete(key)

    @classmethod
    def edit_title(cls, username, task_id, title):
        rd.hset('task:{0}:user:{1}'.format(task_id, username), 'title', title)

    @classmethod
    def edit_status(cls, username, task_id, completed):
        rd.hset('task:{0}:user:{1}'.format(task_id, username),
                'completed', completed)

    @classmethod
    def get_tasks_by_week(cls, username):
        """Returns a list of weeks with tasks for the specified user"""
        week_tasks = {}  # {week: [{taskid: task_data}]}

        key_weeks = rd.keys('taskweek:*:user:{0}'.format(username))
        for key_week in key_weeks:
            task_ids = rd.lrange(key_week, 0, -1)  # Get task ids by week
            # Get task data
            week_task_list = []
            for task_id in task_ids:
                task_data = rd.hgetall("task:{0}:user:{1}".format(task_id,
                                                                  username))
                task_data['timestamp'] = task_id
                week_task_list.append(task_data)
            # For humanizing, the week is the first day which have tasks
            first_week_day = week_task_list[-1:][0]['day']
            week_tasks[first_week_day] = week_task_list

        return week_tasks

    @classmethod
    def get_tasks_by_day(cls, username):
        """Returns a list of days with tasks for the specified user"""
        day_tasks = {}  # {day: [{taskid: task_data}]}

        key_days = rd.keys('taskday:*:user:{0}'.format(username))
        for key_day in key_days:
            day = key_day.rstrip('user:{0}'.format(username))
            day = day.lstrip('taskday:')
            task_ids = rd.lrange(key_day, 0, -1)  # Get task ids by day
            day_tasks[day] = []
            for task_id in task_ids:
                task_data = rd.hgetall("task:{0}:user:{1}".format(task_id,
                                                                  username))
                task_data['timestamp'] = task_id
                day_tasks[day].append(task_data)

        return day_tasks
