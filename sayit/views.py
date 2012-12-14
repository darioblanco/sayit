# -*- coding: UTF-8 -*-
from datetime import datetime

from flask import redirect, render_template, request
from flask.ext.login import (login_required, login_user,
                             logout_user, UserMixin)

from sayit import app
from sayit.database import User, Task
from sayit import settings


@app.route('/')
@login_required
def day_tasks():
    return render_template(
        'tasks_day.html',
        day_tasks=Task.get_tasks_by_day(settings.USERNAME)
    )


@app.route('/week')
@login_required
def week_tasks():
    return render_template(
        'tasks_week.html',
        week_tasks=Task.get_tasks_by_week(settings.USERNAME)
    )


@app.route('/completed')
@login_required
def completed_tasks():
    return render_template(
        'tasks_completed.html',
        completed_tasks=Task.get_tasks_by_status(settings.USERNAME, True)
    )


@app.route('/uncompleted')
@login_required
def uncompleted_tasks():
    return render_template(
        'tasks_uncompleted.html',
        uncompleted_tasks=Task.get_tasks_by_status(settings.USERNAME, False)
    )


@app.route('/task/create', methods=["POST"])
@login_required
def create_task():
    t = Task(settings.USERNAME, request.form['task'])
    t.save()
    return redirect('/')


@app.route('/task/delete', methods=["POST"])
@login_required
def delete_task():
    Task.remove(settings.USERNAME, request.form['task_id'])
    return redirect('/')


@app.route('/task/title', methods=["POST"])
@login_required
def edit_task_title():
    Task.edit_title(settings.USERNAME,
                    request.form['task_id'],
                    request.form['title'])
    return redirect('/')


@app.route('/task/status', methods=["POST"])
@login_required
def edit_task_status():
    status = request.form['status'] in ['True', 'true', 'TRUE']
    Task.edit_status(settings.USERNAME, request.form['task_id'], status)
    return redirect('/')


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    next = request.args.get('next')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember', False)
        if User.check_user_password(username, password):
            # Right password
            user = AuthUser(username)
            if login_user(user, remember=remember):
                # Logged in correctly
                return redirect('/')
        error = "Username or password incorrect"
    return render_template('login.html', login=True, next=next, error=error)


@app.route("/logout")
@login_required
def logout():
    next = request.args.get('next', '/')
    logout_user()
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

    def get_id(self):
        return self.username

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
