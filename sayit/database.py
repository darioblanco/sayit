# -*- coding: UTF-8 -*-
import time
from datetime import datetime

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

    @classmethod
    def check_user_password(cls, username, password):
        return (rd.hget('user:{0}'.format(username), 'password') ==
                crypt(password, SECRET_KEY))


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
            'completed': completed
        }

    def save(self):
        # Hash of task with user
        rd.hmset('task:{0}:user:{1}'.format(self.timestamp,
                                            self.username),
                 self.data)
        # List of tasks ids per day and user
        rd.lpush('tasksday:{0}:user:{1}'.format(self.data['day'],
                                                self.username),
                 self.timestamp)
        # List of tasks ids per week and user
        rd.lpush('tasksweek:{0}:user:{1}'.format(self.data['week'],
                                                 self.username),
                 self.timestamp)
        # List of completed or uncompleted tasks
        rd.lpush('tasks.completed:{0}:user:{1}'.format(self.data['completed'],
                                                       self.username),
                 self.timestamp)

    @classmethod
    def remove(cls, username, task_id):
        key = 'task:{0}:user:{1}'.format(task_id, username)
        data = rd.hgetall(key)
        rd.lrem('tasksday:{0}:user:{1}'.format(data['day'], username), 1,
                task_id)
        rd.lrem('tasksweek:{0}:user:{1}'.format(data['week'], username), 1,
                task_id)
        rd.lrem('tasks.completed:{0}:user:{1}'.format(data['completed'],
                                                      username),
                1, task_id)
        rd.delete(key)

    @classmethod
    def edit_title(cls, username, task_id, title):
        rd.hset('task:{0}:user:{1}'.format(task_id, username), 'title', title)

    @classmethod
    def edit_status(cls, username, task_id, completed):
        key = 'task:{0}:user:{1}'.format(task_id, username)
        prev_completed = rd.hget(key, 'completed') in ['True', 'true', 'TRUE']
        # If the new state is different
        if not (prev_completed == completed):
            # Remove from the previous state list
            rd.lrem('tasks.completed:{0}:user:{1}'.format(prev_completed,
                                                          username),
                    1, task_id)
            # Add to the new state list
            rd.lpush('tasks.completed:{0}:user:{1}'.format(completed,
                                                           username),
                     task_id)
            rd.hset('task:{0}:user:{1}'.format(task_id, username),
                    'completed', completed)

    @classmethod
    def get_tasks_by_week(cls, username):
        """Returns a list of weeks with tasks for the specified user"""
        week_tasks = {}

        key_weeks = rd.keys('tasksweek:*:user:{0}'.format(username))
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
        day_tasks = {}

        key_days = rd.keys('tasksday:*:user:{0}'.format(username))
        for key_day in key_days:
            day = key_day.rstrip('user:{0}'.format(username))
            day = day.lstrip('tasksday:')
            task_ids = rd.lrange(key_day, 0, -1)  # Get task ids by day
            day_tasks[day] = []
            for task_id in task_ids:
                task_data = rd.hgetall("task:{0}:user:{1}".format(task_id,
                                                                  username))
                task_data['timestamp'] = task_id
                day_tasks[day].append(task_data)

        return day_tasks

    @classmethod
    def get_tasks_by_status(cls, username, status):
        """Returns a list of completed tasks for the specified user"""
        tasks = []

        task_ids = rd.lrange(
            "tasks.completed:{0}:user:{1}".format(status, username), 0, -1)
        for task_id in task_ids:
            task_data = rd.hgetall("task:{0}:user:{1}".format(task_id,
                                                              username))
            task_data['timestamp'] = task_id
            tasks.append(task_data)

        return tasks
