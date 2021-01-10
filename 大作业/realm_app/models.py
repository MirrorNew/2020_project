from datetime import datetime
from realm_app import db
# 下面这个包就是hash和检查hash的
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from realm_app import login

# 用户头像，我使用的是Gravatar来提供，使用这个网站生成头像是https:// s.gravatar.com/avatar/(hash) 这种格式，
# 会把邮箱地址用md5加密拼接在后面。如果感兴趣可以去上传一个玩一玩，如果不想去的话可以直接使用我提供的。
# https://www.gravatar.com/avatar/6b541a0a667f5558208aad7309c22936，默认像素是80x80，
# 但是你可以在这个地址后面添加参数?s=128，会变成128x128像素，当然你可以尝试改成更大的数字也可以，很是方便。
# 可以根据你的需求改变大小。接下来就来驶入它吧！
from hashlib import md5


class User(UserMixin, db.Model):

    # 这里面的属性都是会构成数据库表中的字段。
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # back是反向引用,User和Post是一对多的关系，backref是表示在Post中新建一个属性author，关联的是Post中的user_id外键关联的User对象。
    # lazy属性常用的值的含义，select就是访问到属性的时候，就会全部加载该属性的数据;joined则是在对关联的两个表进行join操作，
    #     从而获取到所有相关的对象;dynamic则不一样，在访问属性的时候，
    #     并没有在内存中加载数据，而是返回一个query对象, 需要执行相应方法才可以获取对象，比如.all()
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)


    def __repr__(self):
        return '<用户名:{}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    user_id = db .Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


# 因为flask-login对数据库是真的一无所知啊，那怎么获得用户信息呢？
# 所以这里要写一个加载用户信息的函数，因为是从session中读取，所以是id不是int类型，咱们要把它转成int类型哦。
# app/models.py : flask-login用户加载函数
@login.user_loader
def load_user(id):
    return User.query.get(int(id))