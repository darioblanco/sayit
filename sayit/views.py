# -*- coding: UTF-8 -*-
from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask.ext.login import (login_required, login_user,
                             logout_user, UserMixin)

from sayit import app
from sayit.database import User, Task
from sayit import settings


@app.route('/')
# @login_required
def day_tasks():
    return render_template(
        'tasks_day.html',
        day_tasks=Task.get_tasks_by_day(settings.USERNAME)
    )


@app.route('/week')
# @login_required
def week_tasks():
    return render_template(
        'tasks_week.html',
        week_tasks=Task.get_tasks_by_week(settings.USERNAME)
    )


@app.route('/task/create', methods=["POST"])
# @login_required
def create_task():
    task = request.form['task']
    t = Task(settings.USERNAME, task)
    t.save()
    return redirect('/')


@app.route('/task/edit', methods=["POST"])
# @login_required
def edit_task_title():
    task_id = request.form['task_id']
    title = request.form['title']
    Task.edit_title(settings.USERNAME, task_id, title)
    return redirect('/')


@app.route('/task/delete', methods=["POST"])
# @login_required
def delete_task():
    task_id = request.form['task_id']
    Task.remove(settings.USERNAME, task_id)
    return redirect('/')


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    next = request.args.get('next')
    if request.method == 'POST':
        username = request.form['username']
        # password = request.form['password']
        if login_user(username):
            flash("You have logged in")
            return redirect(next or url_for('index', error=error))
    error = "Login failed"
    return render_template('login.html', login=True, next=next, error=error)


@app.route("/logout")
@login_required
def logout():
    next = request.args.get('next', '/')
    logout_user()
    flash('You are logged out')
    return redirect(next)


@app.login_manager.user_loader
def load_user(user_id):
    user = User.get(user_id)
    if user:
        return AuthUser(user['username'])
    else:
        return None


class AuthUser(UserMixin):
    """Wraps User object for Flask-Login"""
    def __init__(self, username, active=True):
        self.username = username
        self.active = active

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True


@app.template_filter()
def datefromstr(value):
    try:
        str_date = datetime.strptime(value, '%d/%m/%Y').strftime(
            '%a, %d. %b %Y')
    except ValueError:
        str_date = value
    return str_date
