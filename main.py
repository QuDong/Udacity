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
        content=self.request.get('text')

        self.fill_rot13html(escape_html(content.encode('rot13'))) # must to have the html escape
        # self.fill_rot13html(content.encode('rot13'))

        # TEST http request contents
        # self.response.out.write(self.request.get('text'))
        # self.response.out.write('<br><br>')
        # self.response.out.write(uploaded_file)
        # self.response.out.write('<br><br>')
        # self.response.out.write(content)
        # self.response.out.write('<br><br>')
        # self.response.out.write(rot13_transfer(content))


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/testform', TestPage),
                               ('/thanks', ThanksPage),
                               ('/rot13', Rot13Page),
                               ],
                              debug=True)
