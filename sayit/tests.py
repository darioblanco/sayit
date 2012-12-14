import unittest

import redis
from logbook import TestHandler
from pbkdf2 import crypt

from sayit.database import Task, User
from sayit.settings import REDIS, SECRET_KEY

USER = {
    'username': 'user1',
    'password': 'password1'
}

TASK_FIXTURES = [
    'Dummy1', 'Dummy2', 'Dummy3', 'Dummy4'
]


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Capture the log
        self.log_handler = TestHandler()
        self.log_handler.push_application()
        # Connect to the database
        self.rd = redis.StrictRedis(REDIS['host'],
                                    port=REDIS['port'],
                                    password=REDIS['password'],
                                    socket_timeout=REDIS['timeout'])
        self.rd.flushdb()

    def tearDown(self):
        # Removes the log capture
        self.log_handler.pop_application()
        # Removes all data from the local redis instance
        self.rd.flushdb()


class UserTestCase(BaseTestCase):
    def setUp(self):
        super(UserTestCase, self).setUp()
        u = User(USER['username'], USER['password'])
        u.save()

    def test_create_user(self):
        expected_user_data = {
            'username': USER['username'],
            'password': crypt(USER['password'], SECRET_KEY),
            'enabled': "True"
        }
        self.assertEqual(User.get(USER['username']), expected_user_data)

    def test_check_password(self):
        self.assertTrue(User.check_user_password(USER['username'],
                                                 USER['password']))

    def test_delete_user(self):
        User.remove(USER['username'])
        self.assertEquals(User.get(USER['username']), {})


class TaskTestCase(BaseTestCase):
    def setUp(self):
        super(TaskTestCase, self).setUp()
        for task in TASK_FIXTURES:
            t = Task(USER['username'], task)
            t.save()
