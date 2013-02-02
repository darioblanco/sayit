# -*- coding: UTF-8 -*-
from datetime import datetime

from flask import redirect, render_template, request
from flask.ext.login import (current_user, login_required,
                             login_user, logout_user, UserMixin)

from sayit import app
from sayit.database import User, Task


@app.route('/')
@login_required
def day_tasks():
    day_tasks = {}
    tasks = Task.get_tasks(current_user.get_id())
    for task in tasks:
        day_tasks.setdefault(task['timestamp'], []).append(task)
    return render_template(
        'tasks_day.html',
        day_tasks=day_tasks
    )


@app.route('/week')
@login_required
def week_tasks():
    week_tasks = Task.get_tasks(current_user.get_id())
    return render_template(
        'tasks_week.html',
        week_tasks=week_tasks
    )


@app.route('/completed')
@login_required
def completed_tasks():
    return render_template(
        'tasks_completed.html',
        completed_tasks=Task.get_tasks(current_user.get_id(),
                                       status='completed')
    )


@app.route('/uncompleted')
@login_required
def uncompleted_tasks():
    return render_template(
        'tasks_completed.html',
        uncompleted_tasks=Task.get_tasks(current_user.get_id(),
                                         status='uncompleted')
    )


@app.route('/task/create', methods=["POST"])
@login_required
def create_task():
    next = request.args.get('next', '/')
    t = Task(current_user.get_id(), request.form['task'])
    t.save()
    return redirect(next)


@app.route('/task/delete', methods=["POST"])
@login_required
def delete_task():
    next = request.args.get('next', '/')
    Task.remove(request.form['task_id'])
    return redirect(next)


@app.route('/task/title', methods=["POST"])
@login_required
def edit_task_title():
    next = request.args.get('next', '/')
    Task.edit_field(current_user.get_id(),
                    request.form['task_id'],
                    'title',
                    request.form['title'])
    return redirect(next)


@app.route('/task/status', methods=["POST"])
@login_required
def edit_task_status():
    next = request.args.get('next', '/')
    if request.form['status'] in ['True', 'true', 'TRUE']:
        status = 'completed'
    else:
        status = 'uncompleted'
    Task.edit_field(current_user.get_id(), request.form['task_id'],
                    'status', status)
    return redirect(next)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    next = request.args.get('next')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not User.get(username):
            u = User(username, password)
            u.save()
            return redirect('/')
        else:
            error = "The user already exists"
    return render_template('signup.html', login=True, next=next, error=error)


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
    next = request.args.get('next', '/login')
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
def datefromstr(timestamp):
    try:
        return datetime.fromtimestamp(float(timestamp)).strftime(
            '%a, %d. %b %Y')
    except ValueError:
        return ''
