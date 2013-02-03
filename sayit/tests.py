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
        """Should create a user with the correct data"""
        expected_user_data = {
            'username': USER['username'],
            'password': crypt(USER['password'], SECRET_KEY),
            'enabled': "True"
        }
        self.assertEqual(User.get(USER['username']), expected_user_data)

    def test_check_password(self):
        """Should check that the user credentials are valid"""
        self.assertTrue(User.check_user_password(USER['username'],
                                                 USER['password']))

    def test_delete_user(self):
        """Should remove a user when a username is given"""
        User.remove(USER['username'])
        self.assertEquals(User.get(USER['username']), {})


class TaskTestCase(BaseTestCase):
    def setUp(self):
        super(TaskTestCase, self).setUp()
        for task in TASK_FIXTURES:
            t = Task(USER['username'], task)
            t.save()

    def test_create_task(self):
        """Should check the task creation"""
        tasks = self.rd.keys("task:*")
        self.assertEqual(len(tasks), 4)
        for task_id in tasks:
            task_data = self.rd.hgetall(task_id)
            self.assertTrue("Dummy" in task_data['title'])
            self.assertEqual(task_data['status'], 'uncompleted')
            self.assertEqual(task_data['username'], USER['username'])

    def test_remove_task(self):
        """Should remove and specific task"""
        task_redis_id = self.rd.keys("task:*")[0]
        Task.remove(task_redis_id.replace('task:', ''))
        tasks = self.rd.keys("task:*")
        self.assertEqual(len(tasks), 3)
        self.assertFalse(self.rd.keys(task_redis_id))

    def test_edit_field(self):
        """Should change the value of a specific field"""
        task_redis_id = self.rd.keys("task:*")[0]
        old_task_data = self.rd.hgetall(task_redis_id)
        task_id = task_redis_id.replace('task:', '')
        Task.edit_field(task_id, 'title', 'New title')
        Task.edit_field(task_id, 'status', 'completed')
        new_task_data = self.rd.hgetall(task_redis_id)
        self.assertNotEqual(old_task_data['title'], 'New title')
        self.assertNotEqual(old_task_data['status'], 'completed')
        self.assertEqual('New title', new_task_data['title'])
        self.assertEqual('completed', new_task_data['status'])
