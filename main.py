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
import cgi
import string
import re

form = """
<form method="post">
    What is your birthday?
    <br>
    <label>Month <input type="text" name="month" value=%(month)s></label>
    <label>Day <input type="text" name="day" value=%(day)s></label>
    <label>Year <input type="text" name="year" value=%(year)s></label>
    <div style="color: red">%(error)s</div>
    <br><br>
    <input type="submit">
</form>
"""

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


class MainPage(webapp2.RequestHandler):
    def write_form(self, error="", day="", month="", year=""):
        self.response.out.write(form % {"error": error,
                                        "day": escape_html(day),
                                        "month": escape_html(month),
                                        "year": escape_html(year)})

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
            self.redirect("/thanks")
        else:
            # self.response.out.write(self.request)
            self.write_form("Date is not valid!", user_day, user_month, user_year)  # self.response.out.write(form)


class ThanksPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Thanks! That's a totally valid day!")


class TestPage(webapp2.RequestHandler):
    def get(self):
        q = self.request.get("q")
        self.response.out.write(self.request)

    def post(self):
        q = self.request.get("q")
        self.response.out.write(self.request)


rot13html = """
<!DOCTYPE html>

<html>
  <head>
    <title>Unit 2 Rot 13</title>
  </head>

  <body>
    <h2>Enter some text to ROT13:</h2>
    <form method="post">
      <textarea name="text" style="height: 100px; width: 400px;">%(content)s</textarea>
      <br>
      <input type="submit">
    </form>
  </body>

</html>
"""


def rot13_transfer(_s):
    rot13 = string.maketrans(
        "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
        "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")
    return string.translate(_s, rot13)


class Rot13Page(webapp2.RequestHandler):
    def fill_rot13html(self, s=""):
        self.response.out.write(rot13html % {'content': s})

    def get(self):
        self.fill_rot13html()
        # self.response.out.write(rot13html)

    def post(self):
        # uploaded_file = self.request.body
        # content = uploaded_file.split("=")[1]
        content = self.request.get('text')

        self.fill_rot13html(escape_html(content.encode('rot13')))  # must to have the html escape
        # self.fill_rot13html(content.encode('rot13'))

        # TEST http request contents
        # self.response.out.write(self.request.get('text'))
        # self.response.out.write('<br><br>')
        # self.response.out.write(uploaded_file)
        # self.response.out.write('<br><br>')
        # self.response.out.write(content)
        # self.response.out.write('<br><br>')
        # self.response.out.write(rot13_transfer(content))


signuphtml = """
<!DOCTYPE html>

<html>
  <head>
    <title>Sign Up</title>
    <style type="text/css">
      .label {text-align: right}
      .error {color: red}
    </style>
  </head>

  <body>
    <h2>Signup</h2>
    <form method="post">
    <table>
        <tr>
            <td class=label>Username</td>
            <td><input type="text" name="username" value=%(username)s></td>
            <td class=error>%(name_err)s</td>
        </tr>
        <tr>
            <td class=label>Password</td>
            <td><input type="password" name="pw1"></td>
            <td class=error>%(pw1_err)s</td>
        </tr>
        <tr>
            <td class=label>Verify Password</td>
            <td><input type="password" name="pw2"></td>
            <td class=error>%(pw2_err)s</td>
        </tr>
        <tr>
            <td class=label>Email (optional)</td>
            <td><input type="text" name="email" value=%(email)s></td>
            <td class=error>%(email_err)s</td>
        </tr>
    </table>
      <input type="submit">
    </form>
  </body>

</html>
"""

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


class SignupPage(webapp2.RequestHandler):
    def fill_signup(self, user_str="", email_str="", name_err="", pw1_err="", pw2_err="", email_err=""):
        self.response.out.write(signuphtml % {'username': user_str,
                                              'email': email_str,
                                              'name_err': name_err,
                                              'pw1_err': pw1_err,
                                              'pw2_err': pw2_err,
                                              'email_err': email_err})

    def get(self):
        self.fill_signup()

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

            self.fill_signup(user_str=user_username,
                             email_str=user_email,
                             name_err=user_err,
                             pw1_err=pw1_err,
                             pw2_err=pw2_err,
                             email_err=email_err)

        else:
            # For redirect, default it is using GET, and GET pass params in the URL
            self.redirect(
                '/signup/welcome?username=' + user_username)  # NOTE: how to pass the infor through GET method during redirect


class WelcomePage(webapp2.RequestHandler):
    def get(self):
        username = self.request.get('username')
        self.response.out.write("Welcome, {}".format(username))


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/testform', TestPage),
                               ('/thanks', ThanksPage),
                               ('/rot13', Rot13Page),
                               ('/signup', SignupPage),
                               ('/signup/welcome', WelcomePage)
                               ],
                              debug=True)
