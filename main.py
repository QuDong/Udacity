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
        self.write(self.render_str(templete, **kwargs))


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


class SignupPage(BaseHandler):
    def get(self):
        self.render("signup.html")

    def post(self):
        user_username = self.request.get('username')
        user_pw1 = self.request.get('pw1')
        user_pw2 = self.request.get('pw2')
        user_email = self.request.get('email')

        username = valid_username(user_username)
        pw1 = valid_password(user_pw1)
        pw2 = valid_password(user_pw2)
        pw_same = True if user_pw1 == user_pw2 else False
        email = valid_email(user_email)

        if not user_email:  # since it is optional
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

            self.render('signup.html', user_str=user_username,
                        email_str=user_email,
                        name_err=user_err,
                        pw1_err=pw1_err,
                        pw2_err=pw2_err,
                        email_err=email_err)

        else:
            # For redirect, default it is using GET, and GET pass params in the URL
            self.redirect(
                '/signup/welcome?username=' + user_username)  # NOTE: how to pass the infor through GET method during redirect


class WelcomePage(BaseHandler):
    def get(self):
        username = self.request.get('username')
        self.write("Welcome, {}".format(username))


# ===========================
# HW3 Build a Blog
# ===========================
from google.appengine.ext import db


class Post(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class BlogMainPage(BaseHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        # posts = Post.get_by_id([5171003185430528, 6578378068983808])
        self.render('blogmain.html', posts=posts)


class NewPostPage(BaseHandler):
    def render_newpost(self, title="", content="", error=""):
        self.render('newpost.html', title=title, content=content, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
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
        post = Post.get_by_id(int(posid),)
        self.render("post.html", post=post)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/testform', TestPage),
                               ('/thanks', ThanksPage),
                               ('/rot13', Rot13Page),
                               ('/signup', SignupPage),
                               ('/signup/welcome', WelcomePage),
                               ('/blog/', BlogMainPage),
                               ('/blog', BlogMainPage),
                               ('/blog/newpost', NewPostPage),
                               ('/blog/(\d+)', BlogPage),
                               ],
                              debug=True)
