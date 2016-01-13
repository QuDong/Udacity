#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
form = """
<form method="post">
    What is your birthday?
    <br>
    <label>
        Month
        <input type="text" name="month">
    </label>
    <label>
        Day
        <input type="text" name="day">
    </label>
    <label>
        Year
        <input type="text" name="year">
    </label>
    <br><br>
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
        short_month=month[:3].lower()
        return month_abbvs.get(short_month)

def validate_day(day):
    if day and day.isdigit():
        if 1<=int(day)<=31:
            return int(day)

def validate_year(year):
    if year and year.isdigit():
        if 1900<=int(year)<=2020:
            return int(year)
    

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(form)

    def post(self):
        month = validate_month(self.request.get("month"))
        day = validate_day(self.request.get("day"))
        year = validate_year(self.request.get("year"))
        if month and day and year:
            self.response.out.write("Day:{0} Month:{1} Year:{2}   ".format(day, month, year))
            self.response.out.write("Thanks! That's a totally valid day!")
        else:
            self.response.out.write(form)

app = webapp2.WSGIApplication([('/', MainPage)], debug=True)
