# 从realm_app模块中即从__init__.py中导入创建的app应用
from realm_app import app
from flask import render_template, flash, redirect, url_for

from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required

from realm_app.models import User
from realm_app.models import Post
from realm_app.forms import LoginForm


from flask import request
from werkzeug.urls import url_parse


from realm_app import db
from realm_app.forms import RegistrationForm

from realm_app.forms import EditProfileForm
from realm_app.forms import EditBlogForm
from datetime import datetime


# 建立路由，通过路由可以执行其覆盖的方法，可以多个路由指向同一个方法。

@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/index')
@login_required
def index():
    users = User.query.all()
    p = []
    for user in users:
        u = User.query.get(user.id)
        posts = u.posts.all()
        for post in posts:
            if post.body is None:
                post.body = ''
            p.append({'author': user, 'timestamp': post.timestamp,
                      'title': post.title, 'id': post.id, 'len': len(str(post.body)),
                      'body': post.body, 'head': str(post.body)[:10]})

    return render_template('indexD.html', posts=p)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    # 对表格数据进行验证
    if form.validate_on_submit():
        # 根据表格里的数据进行查询，如果查询到数据返回User对象，否则返回None
        user = User.query.filter_by(username=form.username.data).first()
        # 判断用户不存在或者密码不正确
        if user is None or not user.check_password(form.password.data):
            # 如果用户不存在或者密码不正确就会闪现这条信息
            flash('无效的用户名或密码')
            # 然后重定向到登录页面
            return redirect(url_for('login'))
        # 这是一个非常方便的方法，当用户名和密码都正确时来解决记住用户是否记住登录状态的问题
        login_user(user, remember=form.remember_me.data)
        # 此时的next_page记录的是跳转至登录页面是的地址
        next_page = request.args.get('next')
        # 如果next_page记录的地址不存在那么就返回首页
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        # 综上，登录后要么重定向至跳转前的页面，要么跳转至首页
        return redirect(next_page)
    return render_template('loginD.html', title='登录', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    print("dwr")
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('恭喜你成为我们网站的新用户!')
        return redirect(url_for('login'))
    print("register程序结束")
    return render_template('registerD.html', title='注册', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    p = []
    posts = user.posts.all()
    for post in posts:
        p.append({'author': user, 'title':post.title, 'timestamp': post.timestamp, 'body': post.body, 'id': post.id})
    return render_template('userD.html', user=user, posts=p)


@app.route('/blog/<post_id>')
@login_required
def blog_user(post_id):
    post = Post.query.get(post_id)
    user = User.query.get(post.user_id)
    return render_template('user_blog.html', user=user, post=post, len=len(post.body))


@app.route('/user/delete/<post_id>')
@login_required
def user_delete(post_id):
    p = Post.query.get(post_id)
    db.session.delete(p)
    db.session.commit()
    user(current_user.username)
    return redirect(url_for('user', username=current_user.username))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('你的提交已变更.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='个人资料编辑',
                           form=form)


@app.route('/edit_blog', methods=['GET', 'POST'])
@login_required
def edit_blog():
    form = EditBlogForm()
    if form.validate_on_submit():
        if len(str(form.title.data)) == 0:
            flash('标题不准为空.')
            return render_template('writeBlog.html', form=form,
                                   username=current_user.username)
        p = Post(body=form.body.data, author=current_user, title=form.title.data)
        db.session.add(p)
        db.session.commit()
        flash('你的博客信息已变更.')
        return redirect(url_for('user', username=current_user.username))
    return render_template('writeBlog.html', form=form,
                           username=current_user.username)


@app.route('/change_blog/<post_id>', methods=['GET', 'POST'])
@login_required
def change_blog(post_id):
    form = EditBlogForm()
    p = Post.query.get(post_id)
    if form.validate_on_submit():
        if len(str(form.title.data)) == 0:
            flash('标题不准为空.')
            form.title.data = p.title
            form.body.data = p.body
            return render_template('writeBlog.html', form=form,
                                   username=current_user.username)
        p.body = form.body.data
        p.title = form.title.data
        db.session.commit()
        flash('你的博客信息已变更.')
        user(current_user.username)
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.body.data = p.body
        form.title.data = p.title
    return render_template('writeBlog.html', form=form)
