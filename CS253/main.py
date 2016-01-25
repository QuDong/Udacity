#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

import string
import re
import os
import jinja2
from google.appengine.ext import db
import random
import hashlib
import string
import hmac
import json

templete_dir = os.path.join(os.path.dirname(__file__), 'templetes')  # get the absolute path of templetes
env = jinja2.Environment(loader=jinja2.FileSystemLoader(templete_dir),
                         autoescape=True)

# if the method="get", then ?q=qudong is in the url, example: http://localhost:8080/testform?q=qudong
# if the method="post", then q=qudong is in the HTTP request body, url is : http://localhost:8080/testform
form2 = """
<form action="/testform" method="get">
    <input type="text" name="q">
    <br>
    <input type="submit">
</form>
"""

months = ['January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December']
month_abbvs = dict((m[:3].lower(), m) for m in months)


def validate_month(month):
    if month:
        short_month = month[:3].lower()
        return month_abbvs.get(short_month)


def validate_day(day):
    if day and day.isdigit():
        if 1 <= int(day) <= 31:
            return int(day)


def validate_year(year):
    if year and year.isdigit():
        if 1900 <= int(year) <= 2020:
            return int(year)


def escape_html(s):
    """
    manually build functions to escape html
    """
    import cgi  # only used in this function
    # s = s.replace('&', '&amp;')
    # s = s.replace('>', '&gt;')
    # s = s.replace('<', '&lt;')
    # s = s.replace('"', '&quot;')

    # for (i, o) in (('&', '&amp;'),
    # ('>', '&gt;'),
    # ('<', '&lt;'),
    # ('"', '&quot;')):
    # s = s.replace(i, o)
    s = cgi.escape(s, quote=True)
    return s


# For generating secure cookies
secret = 'fart'


def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


class BaseHandler(webapp2.RequestHandler):
    def write(self, *kw, **kwargs):
        self.response.out.write(*kw, **kwargs)

    def render_str(self, templete, **kwargs):
        """
        # >>> from jinja2 import Template
        # >>> template = Template('Hello {{ name }}!')
        # >>> template.render(name='John Doe')
        # u'Hello John Doe!'
        """
        t = env.get_template(templete)
        return t.render(**kwargs)

    def render(self, templete, **kwargs):
        kwargs['user'] = self.user
        self.write(self.render_str(templete, **kwargs))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val)
        )

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        # http://www.diveintopython.net/power_of_introspection/and_or.html
        # and-or trick: None, 0 means false, the rest is just value
        # for and, it will the first false value if there is, or it will return the last value
        # in this case, it will return check_secure_val(cookie_val), which is user id in the cookie_val
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def render_json(self, d):
        json_text = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_text)


    def initialize(self, *a, **kw):
        """
        This a function which is called by google app engine framework every when user
        make a request. To check if the user is logged in or not, through valid cookie
        If the user is logged in, self.user will be the User object, otherwise None
        """
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')

        self.user = uid and User.by_id(int(uid))

        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'


class MainPage(BaseHandler):
    def write_form(self, error="", day="", month="", year=""):
        self.render("birthdate.html", error=error, day=day, month=month, year=year)

    def get(self):
        self.write_form()  # self.response.out.write(form)
        # self.response.out.write(form2)

    def post(self):
        user_month = self.request.get("month")
        user_day = self.request.get("day")
        user_year = self.request.get("year")

        month = validate_month(user_month)
        day = validate_day(user_day)
        year = validate_year(user_year)

        if month and day and year:
            # self.response.out.write("Day:{0} Month:{1} Year:{2}   ".format(day, month, year))
            # self.response.out.write("Thanks! That's a totally valid day!")
            self.redirect("/thanks?year={}&month={}&day={}".format(year, month[:3], day))
        else:
            # self.response.out.write(self.request)
            self.write_form("Date is not valid!", user_day, user_month, user_year)  # self.response.out.write(form)


class ThanksPage(webapp2.RequestHandler):
    def get(self):
        month = self.request.get("month")
        day = self.request.get("day")
        year = self.request.get("year")
        self.response.out.write("Thanks! That's a totally valid day!<br>")
        self.response.out.write("your date of birth is {}-{}-{}".format(day, month, year))


class TestPage(webapp2.RequestHandler):
    """ Just simple functions to test the request"""

    def get(self):
        q = self.request.get("q")
        self.response.out.write(self.request)

    def post(self):
        q = self.request.get("q")
        self.response.out.write(self.request)


def rot13_transfer(_s):
    """
    By making use of string.translate, from stack overflow
    """
    rot13 = string.maketrans(
        "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
        "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")
    return string.translate(_s, rot13)


class Rot13Page(BaseHandler):
    def fill_rot13html(self, s=""):
        # self.response.out.write(rot13html % {'content': s})
        self.render("rot13.html", s=s)

    def get(self):
        self.fill_rot13html()
        # self.response.out.write(rot13html)

    def post(self):
        # uploaded_file = self.request.body
        # content = uploaded_file.split("=")[1]
        content = self.request.get('text')

        # self.fill_rot13html((content.encode('rot13')))  # must to have the html escape
        self.fill_rot13html(content.encode('rot13'))


# todo: to understand how re works
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PW_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")


def valid_username(username):
    return USER_RE.match(username)


def valid_password(password):
    return PW_RE.match(password)


def valid_email(email):
    return EMAIL_RE.match(email)


# Password hashing
def make_salt():
    return ''.join(random.choice(string.ascii_letters) for x in range(5))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)


def valid_pw(name, pw, h):
    salt = h.split(',')[1]
    return h == make_pw_hash(name, pw, salt)


# =======================
# sign up page
# =======================
class User(db.Model):
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = make_pw_hash(name, pw)
        return User(name=name,
                    pw_hash=pw_hash,
                    email=email)

    @classmethod
    def login(cls, name, pw):
        u = User.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


class SignupPage(BaseHandler):
    def get(self):
        self.render("signup.html")

    def post(self):
        self.user_username = self.request.get('username')
        self.user_pw1 = self.request.get('pw1')
        self.user_pw2 = self.request.get('pw2')
        self.user_email = self.request.get('email')

        username = valid_username(self.user_username)
        pw1 = valid_password(self.user_pw1)
        pw2 = valid_password(self.user_pw2)
        pw_same = True if self.user_pw1 == self.user_pw2 else False
        email = valid_email(self.user_email)

        if not self.user_email:  # since it is optional
            email = True

        if not (username and pw1 and pw2 and email and pw_same):
            if not username:
                user_err = "That's not a valid username."
            else:
                user_err = ""
            if not pw1:
                pw1_err = "That wasn't a valid password."
            else:
                pw1_err = ""
            if pw1 and not pw_same:
                pw2_err = "Your passwords didn't match."
            else:
                pw2_err = ""
            if not email:
                email_err = "That's not a valid email."
            else:
                email_err = ""

            self.render('signup.html', user_str=self.user_username,
                        email_str=self.user_email,
                        name_err=user_err,
                        pw1_err=pw1_err,
                        pw2_err=pw2_err,
                        email_err=email_err)

        else:
            self.done()

    def done(self, *kw, **kwargs):
        raise NotImplementedError


class Unit2Signup(SignupPage):
    def done(self):
        # For redirect, default it is using GET, and GET pass params in the URL
        self.redirect(
            '/signup/welcome?username=' + self.user_username)  # NOTE: how to pass the infor through GET method during redirect


class BlogSignupPage(SignupPage):
    def done(self):
        u = User.by_name(self.user_username)
        if u:
            self.render('signup.html', user_str=self.user_username,
                        email_str=self.user_email,
                        name_err="That user already exists.")
        else:
            u = User.register(self.user_username, self.user_pw1, self.user_email)
            u.put()

            self.login(u)
            self.redirect('/blog')


class BlogLogin(BaseHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        pwd = self.request.get('password')

        u = User.login(username, pwd)
        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            self.render('login-form.html', error="Invalid login")


class BlogLogout(BaseHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')


class WelcomePage(BaseHandler):
    def get(self):
        username = self.request.get('username')
        self.write("Welcome, {}".format(username))


# ===========================
# HW3 Build a Blog
# ===========================
class Post(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def as_dict(self):
        post_json = dict()
        post_json['title'] = self.title
        post_json['content'] = self.content
        post_json['created'] = self.created.strftime('%c')
        return post_json


class BlogMainPage(BaseHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        # posts = Post.get_by_id([5171003185430528, 6578378068983808])
        if self.format == 'html':
            self.render('blogmain.html', posts=posts)
        else:
            self.render_json([p.as_dict() for p in posts])


class NewPostPage(BaseHandler):
    def get(self):
        if self.user:
            self.render('newpost.html')
        else:
            self.redirect('/login')

    def post(self):
        if not self.user:
            self.redirect('/blog')

        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            a = Post(title=title, content=content)
            a.put()
            postid = a.key().id()
            self.redirect('/blog/%s' % postid)
        else:
            error = "Either Title or content is not filled up!"
            self.render("newpost.html", title=title, content=content, error=error)


class BlogPage(BaseHandler):
    def get(self, posid):
        post = Post.get_by_id(int(posid), )
        if not post:
            self.error(404)
            return
        if self.format == 'html':
            self.render("post.html", post=post)
        else:
            self.render_json(post.as_dict())


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/testform', TestPage),
                               ('/thanks', ThanksPage),
                               ('/rot13', Rot13Page),
                               ('/unit2/signup', Unit2Signup),
                               ('/signup', BlogSignupPage),
                               ('/login', BlogLogin),
                               ('/logout', BlogLogout),
                               ('/signup/welcome', WelcomePage),
                               ('/blog(?:.json)?', BlogMainPage),  # json re
                               ('/blog/newpost', NewPostPage),
                               ('/blog/(\d+)(?:.json)?', BlogPage),  # json re
                               ],
                              debug=True)
